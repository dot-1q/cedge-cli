FROM --platform=linux/amd64 python:3.12-alpine

WORKDIR /app

COPY monitor.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#SET OUTPUT TO K8S LOGS
ENV PYTHONUNBUFFERED=1

CMD [ "python3", "./monitor.py" ]
