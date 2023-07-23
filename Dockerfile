FROM python:3.10-slim

COPY app requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV BACKEND_URL=https://overpass.kumi.systems/api/interpreter/
# TO use Sentry, set at least SENTRY_DSN in a .env file,
# and pass it to docker when running, like:
# docker run --env-file .env -p 8080:8080 overscape
# The special string "none" is used here if no other environment variables overwrite it;
# overscape will initialize sentry with an empty string if this is passed as an argument
ENV SENTRY_DSN="none"
ENV SENTRY_TSR=""
EXPOSE 8080
CMD python main.py --backend-url $BACKEND_URL --sentry-dsn $SENTRY_DSN --sentry-tsr $SENTRY_TSR
