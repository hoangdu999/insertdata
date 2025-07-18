#!/usr/bin/env python3
"""
Script để tạo file SQL chứa các câu lệnh INSERT dữ liệu
Thay vì insert trực tiếp vào DB, script này sinh ra file output.sql
"""

import pandas as pd
import uuid
import hashlib
import os
from datetime import datetime, timedelta
import logging
from faker import Faker
import sys
import random
import json

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_SQL_FILE = "output.sql"

# Số lượng bản ghi mẫu
NUM_USERS = 1000
NUM_KANJI = 5000  # Tăng từ 500 lên 5000
NUM_VOCAB = 50000  # Tăng từ 2000 lên 50000
NUM_GRAMMAR = 1000  # Tăng từ 300 lên 1000
NUM_READING = 400
NUM_QUIZZES = 50
NUM_QUESTIONS_PER_QUIZ = 20
NUM_FLASHCARDS_PER_USER = 10
NUM_BLOGS_PER_USER = 5
NUM_COMMENTS_PER_BLOG = 10
NUM_FAVORITES_PER_USER = 20
NUM_MESSAGES_PER_USER = 15
NUM_NOTIFICATIONS_PER_USER = 10
NUM_REPORTS = 200

class SQLGenerator:
    def __init__(self, output_file=OUTPUT_SQL_FILE):
        self.output_file = output_file
        self.sql_file = None
        self.fake = Faker(['ja_JP', 'vi_VN', 'en_US'])  # Thêm locale en_US
        self.user_ids = []
        self.kanji_ids = []
        self.vocab_ids = []
        self.grammar_ids = []
        self.reading_ids = []
        self.quiz_ids = []
        self.blog_ids = []
        
    def open_file(self):
        """Mở file SQL để ghi"""
        try:
            self.sql_file = open(self.output_file, 'w', encoding='utf-8')
            self.sql_file.write("-- Generated SQL script for Oboe Japanese Learning App\n")
            self.sql_file.write(f"-- Generated at: {datetime.now()}\n\n")
            logger.info(f"Đã tạo file SQL: {self.output_file}")
        except Exception as e:
            logger.error(f"Lỗi tạo file SQL: {e}")
            raise
    
    def close_file(self):
        """Đóng file SQL"""
        if self.sql_file:
            self.sql_file.close()
        logger.info(f"Đã đóng file SQL: {self.output_file}")

    def generate_uuid(self):
        """Tạo UUID và trả về dạng hex để dùng với UNHEX trong MySQL"""
        return uuid.uuid4().hex

    def hash_password(self, password):
        """Hash password bằng SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def write_sql(self, sql):
        """Ghi câu lệnh SQL vào file"""
        self.sql_file.write(sql + "\n")

    def generate_users(self):
        """Sinh dữ liệu cho bảng users"""
        logger.info("Generating users data...")
        self.write_sql("-- Insert users")
        
        for _ in range(NUM_USERS):
            user_id = self.generate_uuid()
            self.user_ids.append(user_id)
            
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            user_name = f"{first_name.lower()}_{last_name.lower()}_{random.randint(1, 999)}"
            password = self.hash_password('password123')
            auth_provider = random.choice(['EMAIL', 'GOOGLE', 'FACEBOOK'])
            account_type = random.choice(['FREE', 'PREMIUM'])
            role = random.choice(['ROLE_USER'] * 9 + ['ROLE_ADMIN'])  # 10% chance of admin
            status = random.choice(['ACTION'] * 9 + ['BAN'])  # 10% chance of ban
            
            sql = f"""INSERT INTO users 
                    (user_id, first_name, last_name, user_name, pass_word, 
                    auth_provider, account_type, role, status, day_of_birth, 
                    address, verified, create_at, update_at)
                    VALUES (UNHEX('{user_id}'), '{first_name}', '{last_name}', '{user_name}',
                    '{password}', '{auth_provider}', '{account_type}', '{role}',
                    '{status}', '{self.fake.date_of_birth(minimum_age=18, maximum_age=70)}',
                    '{self.fake.address()}', {random.choice([0,1])},
                    NOW(), NOW());"""
            self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_USERS} users")

    def generate_kanji(self):
        """Sinh dữ liệu cho bảng kanji"""
        logger.info("Generating kanji data...")
        self.write_sql("-- Insert kanji")
        
        jlpt_levels = ['N5', 'N4', 'N3', 'N2', 'N1']
        
        for _ in range(NUM_KANJI):
            kanji_id = self.generate_uuid()
            self.kanji_ids.append(kanji_id)
            
            # Tạo một ký tự kanji ngẫu nhiên từ bảng mã Unicode của kanji
            char = chr(random.randint(0x4E00, 0x9FBF))
            
            # Tạo các readings bằng hiragana (từ U+3040 đến U+309F)
            kun_reading = ''.join(chr(random.randint(0x3041, 0x3096)) for _ in range(random.randint(2, 5)))
            on_reading = ''.join(chr(random.randint(0x3041, 0x3096)) for _ in range(random.randint(2, 5)))
            
            # Tạo nghĩa tiếng Việt và tiếng Anh
            meaning_vi = self.fake['vi_VN'].word()
            meaning_en = self.fake['en_US'].word()
            
            # Tạo số nét ngẫu nhiên (1-30)
            strokes = random.randint(1, 30)
            
            # Chọn JLPT level ngẫu nhiên
            jlpt = random.choice(jlpt_levels)
            
            sql = f"""INSERT INTO kanji 
                    (kanji_id, character_name, kun_reading, on_reading, 
                    meaning_vi, meaning_en, jlpt_level, strokes)
                    VALUES (UNHEX('{kanji_id}'), '{char}', '{kun_reading}', 
                    '{on_reading}', '{meaning_vi}', '{meaning_en}', 
                    '{jlpt}', {strokes});"""
            self.write_sql(sql)
            
            if (_ + 1) % 1000 == 0:
                logger.info(f"Generated {_ + 1} kanji")
        
        self.write_sql("")
        logger.info(f"Generated {NUM_KANJI} kanji")

    def generate_vocabulary(self):
        """Sinh dữ liệu cho bảng vocabulary"""
        logger.info("Generating vocabulary data...")
        self.write_sql("-- Insert vocabulary")
        
        jlpt_levels = ['N5', 'N4', 'N3', 'N2', 'N1']
        word_types = ['noun', 'verb', 'adjective', 'adverb', 'particle', 'expression']
        
        for _ in range(NUM_VOCAB):
            vocab_id = self.generate_uuid()
            self.vocab_ids.append(vocab_id)
            
            # Tạo từ vựng bằng cách kết hợp 1-3 kanji
            num_kanji = random.randint(1, 3)
            word = ''.join(chr(random.randint(0x4E00, 0x9FBF)) for _ in range(num_kanji))
            
            # Tạo reading bằng hiragana
            reading = ''.join(chr(random.randint(0x3041, 0x3096)) for _ in range(random.randint(2, 8)))
            
            # Tạo nghĩa và ví dụ
            meaning_vi = self.fake['vi_VN'].sentence()
            meaning_en = self.fake['en_US'].sentence()
            example_jp = self.fake['ja_JP'].sentence()
            example_vi = self.fake['vi_VN'].sentence()
            example_en = self.fake['en_US'].sentence()
            
            # Chọn JLPT level và word type ngẫu nhiên
            jlpt = random.choice(jlpt_levels)
            word_type = random.choice(word_types)
            
            sql = f"""INSERT INTO vocabulary 
                    (vocalb_id, words, reading, meaning_vi, meaning_en,
                    example_jp, example_vi, example_en,
                    jlpt_level, word_type)
                    VALUES (UNHEX('{vocab_id}'), '{word}', '{reading}',
                    '{meaning_vi}', '{meaning_en}', '{example_jp}',
                    '{example_vi}', '{example_en}', '{jlpt}', '{word_type}');"""
            self.write_sql(sql)
            
            if (_ + 1) % 1000 == 0:
                logger.info(f"Generated {_ + 1} vocabulary entries")
        
        self.write_sql("")
        logger.info(f"Generated {NUM_VOCAB} vocabulary entries")

    def generate_grammar(self):
        """Sinh dữ liệu cho bảng grammar"""
        logger.info("Generating grammar data...")
        self.write_sql("-- Insert grammar rules")
        
        jlpt_levels = ['N5', 'N4', 'N3', 'N2', 'N1']
        particles = ['は', 'が', 'を', 'に', 'で', 'へ', 'から', 'まで', 'と', 'や']
        
        for _ in range(NUM_GRAMMAR):
            grammar_id = self.generate_uuid()
            self.grammar_ids.append(grammar_id)
            
            # Tạo pattern ngẫu nhiên bằng cách kết hợp từ vựng và trợ từ
            pattern = f"〜{random.choice(particles)}"
            
            # Tạo giải thích bằng 3 ngôn ngữ
            explanation_jp = self.fake['ja_JP'].paragraph()
            explanation_vi = self.fake['vi_VN'].paragraph()
            explanation_en = self.fake['en_US'].paragraph()
            
            # Tạo ví dụ bằng 3 ngôn ngữ
            example_jp = self.fake['ja_JP'].sentence()
            example_vi = self.fake['vi_VN'].sentence()
            example_en = self.fake['en_US'].sentence()
            
            # Chọn JLPT level ngẫu nhiên
            jlpt = random.choice(jlpt_levels)
            
            # Tạo notes
            notes = self.fake['en_US'].paragraph()
            
            sql = f"""INSERT INTO gramma 
                    (grammaid, pattern, explanation_jp, explanation_vi, explanation_en,
                    example_jp, example_vi, example_en, jlpt_level, notes)
                    VALUES (UNHEX('{grammar_id}'), '{pattern}',
                    '{explanation_jp}', '{explanation_vi}', '{explanation_en}',
                    '{example_jp}', '{example_vi}', '{example_en}',
                    '{jlpt}', '{notes}');"""
            self.write_sql(sql)
            
            if (_ + 1) % 100 == 0:
                logger.info(f"Generated {_ + 1} grammar rules")
        
        self.write_sql("")
        logger.info(f"Generated {NUM_GRAMMAR} grammar rules")

    def generate_reading(self):
        """Sinh dữ liệu cho bảng reading"""
        logger.info("Generating reading data...")
        self.write_sql("-- Insert reading entries")
        
        reading_types = ['hiragana', 'katakana', 'kanji', 'mixed']
        owner_types = ['vocabulary', 'grammar', 'kanji']
        
        for _ in range(NUM_READING):
            reading_id = self.generate_uuid()
            self.reading_ids.append(reading_id)
            
            # Chọn owner_id dựa trên owner_type
            owner_type = random.choice(owner_types)
            if owner_type == 'vocabulary' and self.vocab_ids:
                owner_id = random.choice(self.vocab_ids)
            elif owner_type == 'grammar' and self.grammar_ids:
                owner_id = random.choice(self.grammar_ids)
            elif owner_type == 'kanji' and self.kanji_ids:
                owner_id = random.choice(self.kanji_ids)
            else:
                continue
            
            sql = f"""INSERT INTO reading 
                    (readingid, reading_type, reading_text, owner_type, owner_id)
                    VALUES (UNHEX('{reading_id}'), '{random.choice(reading_types)}',
                    '{self.fake.sentence()}', '{owner_type}', UNHEX('{owner_id}'));"""
            self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_READING} reading entries")

    def generate_quizzes(self):
        """Sinh dữ liệu cho bảng quizzes và questions"""
        logger.info("Generating quizzes and questions data...")
        self.write_sql("-- Insert quizzes and questions")
        
        quiz_types = ['Vocabulary', 'Kanji', 'Grammar', 'Reading', 'Listening']
        jlpt_levels = ['N1', 'N2', 'N3', 'N4', 'N5']
        
        for _ in range(NUM_QUIZZES):
            quiz_id = self.generate_uuid()
            self.quiz_ids.append(quiz_id)
            
            quiz_type = random.choice(quiz_types)
            level = random.choice(jlpt_levels)
            
            sql = f"""INSERT INTO quizzes 
                    (quizzesid, title, description)
                    VALUES (UNHEX('{quiz_id}'), 
                    '{quiz_type} Quiz - {level}',
                    'Bài kiểm tra {quiz_type.lower()} trình độ {level}');"""
            self.write_sql(sql)
            
            # Tạo câu hỏi cho quiz
            for _ in range(NUM_QUESTIONS_PER_QUIZ):
                question_id = self.generate_uuid()
                options = json.dumps([self.fake.word() for _ in range(4)], ensure_ascii=False)
                
                sql = f"""INSERT INTO questions 
                        (questionid, question_name, options, correct_answer, quizzesid)
                        VALUES (UNHEX('{question_id}'), '{self.fake.sentence()}',
                        '{options}', '{random.choice(json.loads(options))}',
                        UNHEX('{quiz_id}'));"""
                self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_QUIZZES} quizzes with {NUM_QUESTIONS_PER_QUIZ} questions each")

    def generate_flashcards(self):
        """Sinh dữ liệu cho bảng flash_cards"""
        logger.info("Generating flashcards data...")
        self.write_sql("-- Insert flashcards")
        
        for user_id in self.user_ids:
            for _ in range(NUM_FLASHCARDS_PER_USER):
                card_id = self.generate_uuid()
                
                sql = f"""INSERT INTO flash_cards 
                        (card_id, term, description, created, user_id)
                        VALUES (UNHEX('{card_id}'), '{self.fake.word()}',
                        '{self.fake.sentence()}', NOW(), UNHEX('{user_id}'));"""
                self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_USERS * NUM_FLASHCARDS_PER_USER} flashcards")

    def generate_blogs(self):
        """Sinh dữ liệu cho bảng blogs và comments"""
        logger.info("Generating blogs and comments data...")
        self.write_sql("-- Insert blogs and comments")
        
        for user_id in self.user_ids:
            for _ in range(NUM_BLOGS_PER_USER):
                blog_id = self.generate_uuid()
                self.blog_ids.append(blog_id)
                
                sql = f"""INSERT INTO blogs 
                        (blog_id, title, content, created_at, updated_at, user_id)
                        VALUES (UNHEX('{blog_id}'), '{self.fake.sentence()}',
                        '{self.fake.text()}', NOW(), NOW(), UNHEX('{user_id}'));"""
                self.write_sql(sql)
                
                # Tạo comments cho blog
                for _ in range(NUM_COMMENTS_PER_BLOG):
                    comment_id = self.generate_uuid()
                    commenter_id = random.choice(self.user_ids)
                    
                    sql = f"""INSERT INTO comments 
                            (comment_id, content, created_at, reference_id,
                            title, user_id, parent_comment_id)
                            VALUES (UNHEX('{comment_id}'), '{self.fake.text()}',
                            NOW(), UNHEX('{blog_id}'), '{self.fake.sentence()}',
                            UNHEX('{commenter_id}'), NULL);"""
                    self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_USERS * NUM_BLOGS_PER_USER} blogs with {NUM_COMMENTS_PER_BLOG} comments each")

    def generate_favorites(self):
        """Sinh dữ liệu cho bảng favorites"""
        logger.info("Generating favorites data...")
        self.write_sql("-- Insert favorites")
        
        for user_id in self.user_ids:
            for _ in range(NUM_FAVORITES_PER_USER):
                favorite_id = self.generate_uuid()
                
                # Chọn ngẫu nhiên loại favorite
                favorite_type = random.choice(['kanji', 'vocabulary', 'grammar', 'flashcard'])
                if favorite_type == 'kanji' and self.kanji_ids:
                    item_id = random.choice(self.kanji_ids)
                elif favorite_type == 'vocabulary' and self.vocab_ids:
                    item_id = random.choice(self.vocab_ids)
                elif favorite_type == 'grammar' and self.grammar_ids:
                    item_id = random.choice(self.grammar_ids)
                else:
                    continue
                
                sql = f"""INSERT INTO favorites 
                        (favoritesid, content, favories_at, title,
                        {favorite_type}_id, user_id)
                        VALUES (UNHEX('{favorite_id}'), '{self.fake.sentence()}',
                        NOW(), '{self.fake.word()}', UNHEX('{item_id}'),
                        UNHEX('{user_id}'));"""
                self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_USERS * NUM_FAVORITES_PER_USER} favorites")

    def generate_messages(self):
        """Sinh dữ liệu cho bảng message"""
        logger.info("Generating messages data...")
        self.write_sql("-- Insert messages")
        
        for user_id in self.user_ids:
            for _ in range(NUM_MESSAGES_PER_USER):
                message_id = self.generate_uuid()
                receiver_id = random.choice([uid for uid in self.user_ids if uid != user_id])
                
                sql = f"""INSERT INTO message 
                        (messageid, sent_message, sent_at, senderid, receiverid)
                        VALUES (UNHEX('{message_id}'), '{self.fake.text()}',
                        NOW(), UNHEX('{user_id}'), UNHEX('{receiver_id}'));"""
                self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_USERS * NUM_MESSAGES_PER_USER} messages")

    def generate_notifications(self):
        """Sinh dữ liệu cho bảng notifications"""
        logger.info("Generating notifications data...")
        self.write_sql("-- Insert notifications")
        
        notification_types = [
            "Bạn có một tin nhắn mới",
            "Có người đã bình luận về bài viết của bạn",
            "Bạn đã hoàn thành bài kiểm tra",
            "Có bài học mới phù hợp với trình độ của bạn",
            "Nhắc nhở ôn tập từ vựng"
        ]
        
        for user_id in self.user_ids:
            for _ in range(NUM_NOTIFICATIONS_PER_USER):
                notif_id = self.generate_uuid()
                
                sql = f"""INSERT INTO notifications 
                        (notifi_id, text_notification, is_read, update_at, user_id)
                        VALUES (UNHEX('{notif_id}'), '{random.choice(notification_types)}',
                        {random.choice([0,1])}, NOW(), UNHEX('{user_id}'));"""
                self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_USERS * NUM_NOTIFICATIONS_PER_USER} notifications")

    def generate_reports(self):
        """Sinh dữ liệu cho bảng reports"""
        logger.info("Generating reports data...")
        self.write_sql("-- Insert reports")
        
        report_titles = [
            "Nội dung không phù hợp",
            "Spam",
            "Vi phạm điều khoản sử dụng",
            "Quấy rối",
            "Thông tin sai lệch"
        ]
        
        for _ in range(NUM_REPORTS):
            report_id = self.generate_uuid()
            user_id = random.choice(self.user_ids)
            
            sql = f"""INSERT INTO reports 
                    (reportid, title, content, report_at, status, user_id)
                    VALUES (UNHEX('{report_id}'), '{random.choice(report_titles)}',
                    '{self.fake.text()}', NOW(),
                    '{random.choice(['PENDING', 'APPROVED', 'REJECTED'])}',
                    UNHEX('{user_id}'));"""
            self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated {NUM_REPORTS} reports")

    def generate_quiz_results(self):
        """Sinh dữ liệu cho bảng quiz_results"""
        logger.info("Generating quiz results data...")
        self.write_sql("-- Insert quiz results")
        
        for user_id in self.user_ids:
            # Mỗi user làm khoảng 30% số quiz
            num_quizzes = int(len(self.quiz_ids) * 0.3)
            for quiz_id in random.sample(self.quiz_ids, num_quizzes):
                result_id = self.generate_uuid()
                
                sql = f"""INSERT INTO quiz_results 
                        (resultid, score, taken_at, quizzesid, user_id)
                        VALUES (UNHEX('{result_id}'), {random.uniform(0, 100):.2f},
                        NOW(), UNHEX('{quiz_id}'), UNHEX('{user_id}'));"""
                self.write_sql(sql)
        
        self.write_sql("")
        logger.info(f"Generated quiz results for {NUM_USERS} users")

    def run(self):
        """Chạy toàn bộ quá trình tạo dữ liệu"""
        try:
            self.open_file()
            
            # Generate data in order of dependencies
            self.generate_users()
            self.generate_kanji()
            self.generate_vocabulary()
            self.generate_grammar()
            self.generate_reading()
            self.generate_quizzes()
            self.generate_flashcards()
            self.generate_blogs()
            self.generate_favorites()
            self.generate_messages()
            self.generate_notifications()
            self.generate_reports()
            self.generate_quiz_results()
            
            logger.info("Hoàn thành tạo dữ liệu mẫu")
        except Exception as e:
            logger.error(f"Lỗi trong quá trình tạo dữ liệu: {e}")
        finally:
            self.close_file()

def main():
    generator = SQLGenerator()
    generator.run()

if __name__ == "__main__":
    main() 