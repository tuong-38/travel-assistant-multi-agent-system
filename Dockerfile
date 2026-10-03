FROM python:3.11-slim

WORKDIR /app

# Cài đặt các system packages cần thiết cho psycopg và build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy file dependencies và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Expose các cổng cho FastAPI (8000) và Streamlit (8501)
EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]