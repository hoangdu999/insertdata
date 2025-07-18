#!/usr/bin/env python3
"""
Script để nhập dữ liệu từ CSV files vào MySQL database
Dữ liệu cho ứng dụng học tiếng Nhật Oboe
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import uuid
import hashlib
import os
from datetime import datetime
import logging
from faker import Faker
import sys
import random

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cấu hình database
DB_CONFIG = {
    'host': 'localhost',
    'database': 'oboe',
    'user': 'root',
    'password': 'Hoangdu1999s2@',
    'port': 3306
}

class DataImporter:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        self.fake = Faker()
        
    def connect(self):
        """Kết nối đến database"""
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("Kết nối database thành công")
        except Error as e:
            logger.error(f"Lỗi kết nối database: {e}")
            raise
    
    def disconnect(self):
        """Đóng kết nối database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Đã đóng kết nối database")

    def generate_uuid(self):
        """Tạo UUID và chuyển thành BINARY(16)"""
        return uuid.uuid4().bytes

    def hash_password(self, password):
        """Hash password bằng SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def import_users(self, csv_file):
        """Import dữ liệu users từ CSV"""
        logger.info(f"Importing users from {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                user_id = self.generate_uuid()
                password = self.hash_password('password123')  # Default password
                
                sql = """INSERT INTO users 
                        (user_id, first_name, last_name, user_name, pass_word, 
                        auth_provider, account_type, role, status, day_of_birth, 
                        address, verified, create_at, update_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        
                values = (user_id, row['first_name'], row['last_name'], row['user_name'],
                         password, row['auth_provider'], row['account_type'], row['role'],
                         row['status'], row['day_of_birth'], row['address'], row['verified'],
                         datetime.now(), datetime.now())
                         
                self.cursor.execute(sql, values)
                
            self.conn.commit()
            logger.info(f"Imported {len(df)} users successfully")
        except Exception as e:
            logger.error(f"Error importing users: {e}")
            self.conn.rollback()

    def import_kanji_and_vocabulary(self, csv_file):
        """Import dữ liệu kanji và vocabulary từ CSV"""
        logger.info(f"Importing kanji and vocabulary from {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                # Insert kanji
                kanji_id = self.generate_uuid()
                sql_kanji = """INSERT INTO kanji 
                              (kanji_id, character_name, meaning, strokes)
                              VALUES (%s, %s, %s, %s)"""
                values_kanji = (kanji_id, row['character_name'], 
                              row['meaning'], row['strokes'])
                self.cursor.execute(sql_kanji, values_kanji)

                # Insert vocabulary
                vocab_id = self.generate_uuid()
                sql_vocab = """INSERT INTO vocabulary 
                              (vocalb_id, words, meanning, script_type, 
                              word_type, kanji_id)
                              VALUES (%s, %s, %s, %s, %s, %s)"""
                values_vocab = (vocab_id, row['vocabulary'], 
                              row['meaning_vocab'], row['script_type'],
                              row['word_type'], kanji_id)
                self.cursor.execute(sql_vocab, values_vocab)

            self.conn.commit()
            logger.info(f"Imported {len(df)} kanji and vocabulary pairs successfully")
        except Exception as e:
            logger.error(f"Error importing kanji and vocabulary: {e}")
            self.conn.rollback()

    def import_grammar(self, csv_file):
        """Import dữ liệu ngữ pháp từ CSV"""
        logger.info(f"Importing grammar from {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                grammar_id = self.generate_uuid()
                sql = """INSERT INTO gramma 
                         (grammaid, grammar_type, structure, explanation, example)
                         VALUES (%s, %s, %s, %s, %s)"""
                values = (grammar_id, row['grammar_type'], row['structure'],
                         row['explanation'], row['example'])
                self.cursor.execute(sql, values)

            self.conn.commit()
            logger.info(f"Imported {len(df)} grammar rules successfully")
        except Exception as e:
            logger.error(f"Error importing grammar: {e}")
            self.conn.rollback()

    def import_reading(self, csv_file):
        """Import dữ liệu đọc hiểu từ CSV"""
        logger.info(f"Importing reading from {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                reading_id = self.generate_uuid()
                sql = """INSERT INTO reading 
                         (readingid, reading_type, reading_text, owner_type, owner_id)
                         VALUES (%s, %s, %s, %s, %s)"""
                values = (reading_id, row['reading_type'], row['reading_text'],
                         row['owner_type'], self.generate_uuid())  # Generate new owner_id
                self.cursor.execute(sql, values)

            self.conn.commit()
            logger.info(f"Imported {len(df)} reading entries successfully")
        except Exception as e:
            logger.error(f"Error importing reading: {e}")
            self.conn.rollback()

    def import_flashcards(self, csv_file):
        """Import dữ liệu flashcard từ CSV"""
        logger.info(f"Importing flashcards from {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                card_id = self.generate_uuid()
                sql = """INSERT INTO flash_cards 
                         (card_id, term, description, created, user_id)
                         VALUES (%s, %s, %s, %s, %s)"""
                values = (card_id, row['term'], row['description'],
                         datetime.now(), self.generate_uuid())  # Generate new user_id
                self.cursor.execute(sql, values)

            self.conn.commit()
            logger.info(f"Imported {len(df)} flashcards successfully")
        except Exception as e:
            logger.error(f"Error importing flashcards: {e}")
            self.conn.rollback()

    def import_quizzes(self, csv_file):
        """Import dữ liệu quiz và câu hỏi từ CSV"""
        logger.info(f"Importing quizzes and questions from {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                # Create quiz
                quiz_id = self.generate_uuid()
                sql_quiz = """INSERT INTO quizzes 
                             (quizzesid, title, description)
                             VALUES (%s, %s, %s)"""
                values_quiz = (quiz_id, row['title'], row['description'])
                self.cursor.execute(sql_quiz, values_quiz)

                # Create questions for this quiz
                questions = row['questions'].split('|')
                options = row['options'].split('|')
                answers = row['correct_answers'].split('|')

                for q, o, a in zip(questions, options, answers):
                    question_id = self.generate_uuid()
                    sql_question = """INSERT INTO questions 
                                    (questionid, question_name, options, 
                                    correct_answer, quizzesid)
                                    VALUES (%s, %s, %s, %s, %s)"""
                    values_question = (question_id, q, o, a, quiz_id)
                    self.cursor.execute(sql_question, values_question)

            self.conn.commit()
            logger.info(f"Imported {len(df)} quizzes with their questions successfully")
        except Exception as e:
            logger.error(f"Error importing quizzes: {e}")
            self.conn.rollback()

    def generate_sample_messages(self, num_messages=20):
        """Tạo dữ liệu mẫu cho tin nhắn"""
        logger.info(f"Generating {num_messages} sample messages")
        try:
            # Get all user IDs
            self.cursor.execute("SELECT user_id FROM users")
            user_ids = [row[0] for row in self.cursor.fetchall()]

            if len(user_ids) < 2:
                logger.warning("Not enough users to generate messages")
                return

            for _ in range(num_messages):
                message_id = self.generate_uuid()
                sender_id = random.choice(user_ids)
                receiver_id = random.choice([uid for uid in user_ids if uid != sender_id])

                sql = """INSERT INTO message 
                         (messageid, sent_message, sent_at, senderid, receiverid)
                         VALUES (%s, %s, %s, %s, %s)"""
                values = (message_id, self.fake.text(max_nb_chars=100),
                         datetime.now(), sender_id, receiver_id)
                self.cursor.execute(sql, values)

            self.conn.commit()
            logger.info(f"Generated {num_messages} sample messages")
        except Exception as e:
            logger.error(f"Error generating messages: {e}")
            self.conn.rollback()

    def generate_sample_notifications(self, num_notifications=30):
        """Tạo dữ liệu mẫu cho thông báo"""
        logger.info(f"Generating {num_notifications} sample notifications")
        try:
            # Get all user IDs
            self.cursor.execute("SELECT user_id FROM users")
            user_ids = [row[0] for row in self.cursor.fetchall()]

            notification_types = [
                "Bạn có một tin nhắn mới",
                "Quiz mới đã được thêm vào",
                "Có người bình luận về bài viết của bạn",
                "Đã đến giờ ôn tập Kanji",
                "Bạn đã hoàn thành %d%% khóa học"
            ]

            for _ in range(num_notifications):
                notif_id = self.generate_uuid()
                user_id = random.choice(user_ids)
                text = random.choice(notification_types)
                if "%d" in text:
                    text = text % random.randint(10, 100)

                sql = """INSERT INTO notifications 
                         (notifi_id, text_notification, is_read, update_at, user_id)
                         VALUES (%s, %s, %s, %s, %s)"""
                values = (notif_id, text, random.choice([0, 1]),
                         datetime.now(), user_id)
                self.cursor.execute(sql, values)

            self.conn.commit()
            logger.info(f"Generated {num_notifications} sample notifications")
        except Exception as e:
            logger.error(f"Error generating notifications: {e}")
            self.conn.rollback()

    def run(self):
        """Chạy toàn bộ quá trình import dữ liệu"""
        try:
            self.connect()
            
            # Import dữ liệu từ CSV
            self.import_users('data/users.csv')
            self.import_kanji_and_vocabulary('data/kanji_vocab.csv')
            self.import_grammar('data/grammar.csv')
            self.import_reading('data/reading.csv')
            self.import_flashcards('data/flashcards.csv')
            self.import_quizzes('data/quizzes.csv')
            
            # Generate dữ liệu mẫu
            self.generate_sample_messages()
            self.generate_sample_notifications()
            
            logger.info("Hoàn thành import dữ liệu")
        except Exception as e:
            logger.error(f"Lỗi trong quá trình import: {e}")
        finally:
            self.disconnect()

def main():
    importer = DataImporter(DB_CONFIG)
    importer.run()

if __name__ == "__main__":
    main() 