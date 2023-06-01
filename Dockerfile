FROM python:3.10-slim

COPY app requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV OVERPASS_URL=https://overpass.kumi.systems/api/interpreter/

EXPOSE 8080
CMD python main.py --overpass-url $OVERPASS_URL