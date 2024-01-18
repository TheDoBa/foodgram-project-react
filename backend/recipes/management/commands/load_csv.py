from django.core.management.base import BaseCommand
import csv
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

class Command(BaseCommand):
    help = 'Load data from CSV file into PostgreSQL table'

    def handle(self, *args, **options):
        # Загрузка переменных окружения из файла .env
        load_dotenv()

        # Определение пути к файлу внутри проекта
        project_root = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(project_root, 'data', 'ingredients.csv')



        # Параметры подключения к базе данных из переменных окружения
        db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'dbname': os.getenv('POSTGRES_DB', 'django'),
            'user': os.getenv('POSTGRES_USER', 'django'),
            'password': os.getenv('POSTGRES_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 5432)),
        }

        # Имя таблицы в PostgreSQL
        table_name = 'ваша_таблица'

        # Функция для создания таблицы в базе данных
        def create_table(cursor):
            table_identifier = sql.Identifier(table_name)

            create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                unit VARCHAR(50)
            );
            """).format(table_identifier)

            cursor.execute(create_table_query)

        # Функция для загрузки данных из CSV файла в базу данных
        def load_data(cursor):
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Пропустить заголовок

                insert_query = """
                INSERT INTO {} (name, unit) VALUES (%s, %s);
                """.format(sql.Identifier(table_name))

                for row in csv_reader:
                    cursor.execute(insert_query, (row[0], row[1]))

        # Основная функция
        def main():
            # Подключение к базе данных
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            # Создание таблицы
            create_table(cursor)

            # Загрузка данных из CSV файла
            load_data(cursor)

            # Подтверждение изменений и закрытие соединения
            conn.commit()
            cursor.close()
            conn.close()

        main()
        self.stdout.write(self.style.SUCCESS('Data loaded successfully.'))
