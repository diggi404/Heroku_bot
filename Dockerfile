FROM python:3.11-alpine3.20
RUN addgroup -S botgroup && adduser -S botuser -G botgroup
WORKDIR /app/
COPY . /app/
RUN chown -R botuser:botgroup /app
USER botuser
RUN pip install --no-cache -r requirements.txt
CMD [ "python", "main.py" ]