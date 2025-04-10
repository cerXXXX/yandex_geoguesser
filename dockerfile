# Используем официальный Python образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта внутрь контейнера
COPY . .

# Запускаем Gunicorn (4 воркера, на 0.0.0.0:5000)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
