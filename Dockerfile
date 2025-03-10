# Gunakan Python versi tertentu
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy semua file ke dalam container
COPY . .

# Install dependensi
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Jalankan aplikasi (sesuaikan dengan framework yang digunakan)
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

