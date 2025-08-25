# Minimal container for local / other hosts (Render can ignore this if using native environment)
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Persist DB under /app/data when you mount a volume
ENV DB_PATH=/app/data/movies.db
CMD ["python", "-m", "app.main"]
