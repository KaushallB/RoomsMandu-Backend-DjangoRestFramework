FROM python:3.11-alpine

WORKDIR /usr/src/django_roomsmandu_backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache netcat-openbsd postgresql-client

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Remove carriage returns from entrypoint script and make it executable
RUN sed -i 's/\r$//g' /usr/src/django_roomsmandu_backend/entrypoint.sh
RUN chmod +x /usr/src/django_roomsmandu_backend/entrypoint.sh

ENTRYPOINT [ "sh", "/usr/src/django_roomsmandu_backend/entrypoint.sh" ]