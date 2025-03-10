# Gunakan Python 3.10 yang lebih stabil
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Set working directory
WORKDIR /app

# Install dependencies sistem yang dibutuhkan (jika ada)
RUN apt-get update && apt-get install -y \
    python3-distutils \
    python3-venv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy semua file ke dalam container
COPY . .

# Buat virtual environment dan install dependencies
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Gunakan user non-root untuk keamanan
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Jalankan aplikasi dengan Uvicorn
CMD ["/opt/venv/bin/uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
