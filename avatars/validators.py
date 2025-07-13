import os

from django.core.exceptions import ValidationError

# Максимальный размер файла в мегабайтах
MAX_FILE_SIZE_MB = 5


def validate_image_file_extension(value):
    """
    Проверяет, что расширение файла находится в списке разрешенных.
    """
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(f'Неподдерживаемый формат файла. Разрешены только: {", ".join(valid_extensions)}')


def validate_image_size(value):
    """
    Проверяет, что размер файла не превышает установленный лимит.
    """
    filesize = value.size
    limit_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if filesize > limit_bytes:
        raise ValidationError(f"Максимальный размер файла не должен превышать {MAX_FILE_SIZE_MB}МБ.")
