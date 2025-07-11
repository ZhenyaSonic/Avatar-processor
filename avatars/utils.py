from PIL import Image
from io import BytesIO
from django.conf import settings


def process_image(image_file, quality=85, target_format='JPEG'):
    """
    Принимает файловый объект изображения, выполняет обработку и возвращает
    обработанное изображение в виде BytesIO-буфера.

    :param image_file: Входной файловый объект (из ImageField).
    :param quality: Качество сжатия для JPEG (по умолчанию 85).
    :param target_format: Целевой формат ('JPEG', 'PNG').
    :return: BytesIO-буфер с обработанным изображением.
    """
    try:
        pil_img = Image.open(image_file)
    except Exception as e:
        # Если Pillow не может открыть файл, возвращаем None или возбуждаем ошибку
        # Это дополнительная защита от некорректных файлов, прошедших валидацию
        return None

    # --- 1. Обрезка до квадрата ---
    width, height = pil_img.size
    if width != height:
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = (width + min_dim) // 2
        bottom = (height + min_dim) // 2
        pil_img = pil_img.crop((left, top, right, bottom))

    # --- 2. Конвертация и сжатие ---
    # Конвертируем в RGB, чтобы избавиться от проблем с прозрачностью (альфа-канал)
    # и другими цветовыми режимами (например, палитра 'P').
    if pil_img.mode in ('RGBA', 'P', 'LA'):
        pil_img = pil_img.convert('RGB')

    buffer = BytesIO()
    pil_img.save(
        buffer,
        format=target_format,
        quality=quality,
        optimize=True
    )
    # Возвращаем курсор в начало буфера, чтобы Django мог его прочитать
    buffer.seek(0)

    return buffer
