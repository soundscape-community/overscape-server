FROM python:3.10-slim

COPY app requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV BACKEND_URL=https://overpass.kumi.systems/api/interpreter/
# Leave these variables undefined; to use sentry, provide them in a .env file with docker compose or on the command line.
ENV SENTRY_DSN
ENV SENTRY_TSR
EXPOSE 8080
CMD python main.py --backend-url $BACKEND_URL --sentry-dsn $SENTRY_DSN --sentry-tsr $SENTRY_TSR