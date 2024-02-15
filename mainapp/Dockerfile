# Используем официальный образ Python в качестве базового образа
FROM python:3.10-alpine
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /usr/src/app
# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Копируем файл requirements.txt внутрь контейнера
COPY requirements.txt ./
# Устанавливаем зависимости, описанные в файле requirements.txt
RUN pip install -r requirements.txt