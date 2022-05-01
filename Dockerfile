FROM python:3.9.6-alpine

WORKDIR /app
COPY . .

RUN apk update
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]