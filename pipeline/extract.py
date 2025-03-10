import os
import json
from pathlib import Path
import cv2
import pdf2image
import fitz  # PyMuPDF
import numpy as np
import spacy
from paddleocr import PaddleOCR

# Direktori dan path
BASE_DIR = Path("C:/Users/wilda/OneDrive/Documents/studycase_vidavox/data")
INPUT_DIR = BASE_DIR / "input"
PROCESSED_DIR = BASE_DIR / "processed"

# Pastikan folder processed tersedia
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load SpaCy NER model (bisa ganti ke model lain sesuai kebutuhan)
nlp = spacy.load("en_core_web_sm")


def detect_charts_in_images(image_paths):
    """
    Deteksi apakah ada chart/tabel dalam gambar menggunakan OpenCV.
    Metode ini mencari garis, pola grid, dan bentuk geometris.
    """
    chart_data = []

    if not image_paths:
        print("⚠️ Tidak ada gambar tersedia untuk deteksi grafik.")
        return chart_data

    for image_path in image_paths:
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"⚠️ Gagal membaca gambar: {image_path}")
            continue

        # Konversi ke grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Threshold adaptif
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)

        # Canny edge detection
        edges = cv2.Canny(binary, 50, 150, apertureSize=3)

        # Deteksi garis menggunakan Hough Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                minLineLength=100, maxLineGap=20)

        # Deteksi kontur (untuk bentuk geometris)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Analisis karakteristik chart
        characteristics = {
            "has_lines": lines is not None and len(lines) > 10,
            "has_shapes": len(contours) > 5,
            "regular_patterns": False
        }

        # Analisis pola teratur (indikasi grid atau axis)
        if lines is not None:
            horizontal_lines, vertical_lines = 0, 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi)
                if angle < 5 or angle > 175:
                    horizontal_lines += 1
                elif 85 < angle < 95:
                    vertical_lines += 1

            characteristics["regular_patterns"] = horizontal_lines > 3 and vertical_lines > 3

        contains_chart = all(characteristics.values())

        chart_data.append({
            "image": str(image_path),
            "contains_chart": "Yes" if contains_chart else "No",
            "characteristics": characteristics,
            "confidence_score": sum(characteristics.values()) / len(characteristics)
        })

        print(f"📊 {image_path} → Contains Chart? {contains_chart}")

        # Simpan gambar debug jika chart terdeteksi
        if contains_chart:
            debug_path = PROCESSED_DIR / f"debug_{Path(image_path).name}"
            cv2.imwrite(str(debug_path), edges)
            print(f"🔍 Debug image saved at: {debug_path}")

    return chart_data


def extract_text_from_pdf(pdf_path):
    """
    Ekstrak teks langsung dari PDF menggunakan PyMuPDF.
    """
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc]).strip()
    return text if text else None


def pdf_to_images(pdf_path, output_folder=PROCESSED_DIR, dpi=300):
    """
    Konversi PDF ke gambar (PNG) menggunakan pdf2image.
    """
    images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
    image_paths = []

    for i, image in enumerate(images):
        image_path = output_folder / f"page_{i+1}.png"
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths


def extract_text_from_images(image_paths):
    """
    Ekstraksi teks dari gambar menggunakan PaddleOCR.
    """
    ocr = PaddleOCR(use_angle_cls=True, lang="en")
    extracted_text = []

    for image_path in image_paths:
        result = ocr.ocr(str(image_path), cls=True)

        if not result or not result[0]:
            extracted_text.append("[No text detected]")
        else:
            page_text = []
            for line in result:
                line_text = " ".join([word[1][0] for word in line if len(word) > 1])
                page_text.append(line_text)
            extracted_text.append("\n".join(page_text))

    return "\n\n".join(extracted_text)


def process_named_entities(text):
    """
    Proses teks menggunakan SpaCy untuk Named Entity Recognition (NER).
    """
    doc = nlp(text)
    return {ent.label_: ent.text for ent in doc.ents}


def main():
    pdf_path = INPUT_DIR / "input_data.pdf"
    output_text_path = PROCESSED_DIR / "extracted_text.json"
    chart_detection_output = PROCESSED_DIR / "chart_detection.json"

    try:
        # 1. Coba ekstraksi teks langsung
        extracted_text = extract_text_from_pdf(pdf_path)

        if extracted_text:
            print("✅ Teks langsung ditemukan dari PDF.")
            image_paths = []
        else:
            print("🖼️ PDF tidak mengandung teks langsung, konversi ke gambar...")
            image_paths = pdf_to_images(pdf_path)
            extracted_text = extract_text_from_images(image_paths)

        # 2. Konversi PDF ke gambar tetap dijalankan untuk chart detection
        if not image_paths:
            image_paths = pdf_to_images(pdf_path)

        # 3. Deteksi chart/tabel dari gambar
        chart_data = detect_charts_in_images(image_paths)

        # 4. NER - Named Entity Recognition dari teks
        named_entities = process_named_entities(extracted_text)

        # 5. Simpan hasil ke JSON
        extracted_data = {
            "text": extracted_text,
            "named_entities": named_entities
        }

        with open(output_text_path, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=4, ensure_ascii=False)

        with open(chart_detection_output, "w", encoding="utf-8") as f:
            json.dump(chart_data, f, indent=4, ensure_ascii=False)

        print(f"✅ Teks & Named Entities disimpan di: {output_text_path}")
        print(f"✅ Data Deteksi Chart disimpan di: {chart_detection_output}")

    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")


if __name__ == "__main__":
    main()
