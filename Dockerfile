# Gunakan image Python yang kompatibel
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install dependensi yang hilang
RUN apt-get update && apt-get install -y python3-distutils

# Copy kode proyek
COPY . /app

# Buat virtual environment dan install dependencies
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Expose port untuk FastAPI
EXPOSE 8000

# Jalankan aplikasi
CMD ["/opt/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
