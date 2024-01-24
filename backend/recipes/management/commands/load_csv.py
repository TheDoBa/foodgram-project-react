import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Пользовательская команда управления Django для загрузки данных
    из CSV-файлов в соответствующие модели.

    Эта команда перебирает словарь моделей и путей к файлам CSV,
    загружая данные из каждого CSV-файла в соответствующую модель Django.

    Использование:
    python manage.py load_csv
    """

    def handle(self, *args, **kwargs):
        # Путь к файлу CSV
        csv_file_path = os.path.join(
            settings.BASE_DIR, 'data', 'ingredients.csv')

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                ingredients_to_create = [
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in reader
                ]
                Ingredient.objects.bulk_create(ingredients_to_create)

            self.stdout.write(self.style.SUCCESS('Все ингредиенты загружены!'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл {csv_file_path} не найден. Проверьте путь к файлу.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {str(e)}'))
