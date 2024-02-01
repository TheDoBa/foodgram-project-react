import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Пользовательская команда управления Django для загрузки данных.

    Эта команда перебирает словарь моделей и путей к файлам CSV,
    загружая данные из каждого CSV-файла в соответствующую модель Django.

    Использование:
    python manage.py load_csv
    """

    def handle(self, *args, **kwargs):
        csv_file_path = os.path.join(
            settings.BASE_DIR, 'data', 'ingredients.csv')
        try:
            self.load_data(csv_file_path)
        except FileNotFoundError:
            self.handle_file_not_found(csv_file_path)
        except Exception as error:
            self.handle_error(error)

    def load_data(self, csv_file_path):
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            ingredients_to_create = (
                Ingredient(name=row[0], measurement_unit=row[1])
                for row in reader
            )
            Ingredient.objects.bulk_create(ingredients_to_create)
        self.stdout.write(self.style.SUCCESS('Все ингредиенты загружены!'))

    def handle_file_not_found(self, csv_file_path):
        self.stdout.write(self.style.ERROR(
            f'Файл {csv_file_path} не найден. Проверьте путь к файлу.'
        ))

    def handle_error(self, error):
        self.stdout.write(
            self.style.ERROR('Произошла ошибка: {}'.format(str(error)))
        )
