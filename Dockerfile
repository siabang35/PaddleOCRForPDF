# Gunakan Python 3.10 (bukan 3.12)
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Set working directory
WORKDIR /app

# Install dependencies sistem yang diperlukan
RUN apt-get update && apt-get install -y \
    python3-distutils \
    python3-venv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy semua file ke dalam container
COPY . .

# Buat virtual environment dan install dependensi
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -r requirements.txt

# Gunakan user non-root untuk keamanan
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Jalankan aplikasi dengan Uvicorn
CMD ["/opt/venv/bin/uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
