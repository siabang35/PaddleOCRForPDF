# Study Case Vidavox ETL Pipeline

A comprehensive ETL (Extract, Transform, Load) pipeline for processing research papers, extracting text and charts, and providing a searchable interface.

## 🌟 Features

- **Text Extraction**: Uses PaddleOCR for accurate text extraction from PDFs
- **Chart Detection**: OpenCV-based chart detection and analysis
- **NLP Processing**: SpaCy integration for entity recognition and text analysis
- **Vector Search**: FAISS implementation for semantic search capabilities
- **REST API**: FastAPI-powered API for data access
- **Interactive UI**: Streamlit-based frontend for visualization

## 🛠️ Technology Stack

- **OCR Engine**: PaddleOCR
- **Image Processing**: OpenCV
- **NLP**: SpaCy, Sentence Transformers
- **Vector Search**: FAISS
- **Database**: PostgreSQL
- **API**: FastAPI
- **Frontend**: Streamlit
- **Language**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Virtual environment (recommended)

## 🚀 Installation

1. Clone the repository:
```bash
mkdir research-paper-etl
cd research-paper-etl
git clone https://github.com/siabang35/PaddleOCRForPDF.git
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate #On Linux:
env\Scripts\activate #On Windows:  
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. Set up environment variables:
Create a `.env` file with your database credentials:
```env
DATABASE_URL=your_supabasedb

```

5. Initialize the database:
```bash
psql -U postgres -f database/init.sql
```

## 🏃‍♂️ Running the Pipeline

1. Extract text and charts:
```bash
python pipeline/extract.py
```

2. Transform and process data:
```bash
python pipeline/transform.py
```

3. Load data into database:
```bash
python pipeline/load.py
```

## 🌐 Starting the Services

1. Start the API server:
```bash
uvicorn backend.api.main:app --reload --port 8000
```

2. Launch the frontend:
```bash
streamlit run frontend/app.py
```

## 📁 Project Structure

```
research-paper-etl/
├── api/                 # FastAPI application
│   ├── main.py         # API endpoints
│   ├── models.py       # Pydantic models
│   └── db.py           # Database operations
├── pipeline/           # ETL pipeline components
│   ├── extract.py      # Text and chart extraction
│   ├── transform.py    # Data processing
│   └── load.py         # Database loading         └── config.py
    └── logger.py
├── frontend/           # Streamlit frontend
│   └── app.py         # UI implementation
├── data/              # Data storage
│   ├── input/         # Input PDFs
│   └── processed/     # Processed data
├── database/          # Database scripts
│   └── db.sql       # Database initialization
└── requirements.txt   # Python dependencies
```

## 🔍 API Endpoints

- `GET /`: API health check
- `GET /documents/{doc_id}`: Retrieve document by ID
- `POST /search`: Search documents

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
