FROM --platform=linux/amd64 python:3.12-alpine

WORKDIR /app

COPY cedge.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [ "python3", "./cedge.py" ]
