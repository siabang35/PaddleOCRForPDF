import json
from pathlib import Path
from typing import Optional, Dict

import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

from config import PROCESSED_DIR, DATABASE_URL
from logger import setup_logger

# Setup logging
logger = setup_logger("load")

class DatabaseLoader:
    """Load processed data into PostgreSQL database."""
    
    def __init__(self):
        """Initialize database connection."""
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.cur = self.conn.cursor()
            self.setup_database()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
            
    def setup_database(self):
        """Create necessary database tables."""
        try:
            # Create documents table
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    entities JSONB,
                    keywords TEXT[],
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create charts table
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS charts (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    image_path TEXT NOT NULL,
                    confidence FLOAT,
                    characteristics JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create embeddings table
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    sentence TEXT NOT NULL,
                    vector FLOAT[],
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            logger.info("Database tables created/verified")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            self.conn.rollback()
            raise
            
    def load_data(self, data_path: Path) -> Optional[int]:
        """Load processed data into database."""
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Insert document
            self.cur.execute("""
                INSERT INTO documents (content, entities, keywords)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (
                '\n'.join(data['text_analysis']['sentences']),
                Json(data['text_analysis']['entities']),
                data['text_analysis']['keywords']
            ))
            
            document_id = self.cur.fetchone()[0]
            
            # Insert charts
            for chart in data['charts']:
                self.cur.execute("""
                    INSERT INTO charts (document_id, image_path, confidence, characteristics)
                    VALUES (%s, %s, %s, %s)
                """, (
                    document_id,
                    chart['image_path'],
                    chart['confidence'],
                    Json(chart['characteristics'])
                ))
                
            self.conn.commit()
            logger.info(f"Data loaded successfully. Document ID: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            self.conn.rollback()
            raise
            
    def close(self):
        """Close database connection."""
        try:
            self.cur.close()
            self.conn.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

def main():
    """Main execution function."""
    try:
        data_path = PROCESSED_DIR / "processed_data.json"
        if not data_path.exists():
            raise FileNotFoundError(f"Processed data not found: {data_path}")
            
        loader = DatabaseLoader()
        document_id = loader.load_data(data_path)
        
        if document_id:
            logger.info(f"Document loaded successfully with ID: {document_id}")
        
        loader.close()
        
    except Exception as e:
        logger.error(f"Loading process failed: {e}")
        raise

if __name__ == "__main__":
    main()