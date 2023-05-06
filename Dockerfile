FROM python:3.11-alpine

COPY app requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 8080
CMD python server.py