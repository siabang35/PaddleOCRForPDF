import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    """Database connection manager."""
    
    def __init__(self):
        """Initialize database configuration."""
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
            
    @contextmanager
    def get_connection(self):
        """Create and manage database connection."""
        conn = None
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

class DocumentRepository:
    """Repository for document-related database operations."""
    
    def __init__(self):
        """Initialize the repository."""
        self.db = DatabaseConnection()

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve document and its associated charts by ID."""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get document data
                cur.execute("""
                    SELECT 
                        d.id,
                        d.content,
                        d.entities,
                        d.keywords,
                        COALESCE(json_agg(
                            json_build_object(
                                'image_path', c.image_path,
                                'confidence', c.confidence,
                                'characteristics', c.characteristics,
                                'type', 'chart'
                            )
                        ) FILTER (WHERE c.id IS NOT NULL), '[]'::json) as charts
                    FROM documents d
                    LEFT JOIN charts c ON d.id = c.document_id
                    WHERE d.id = %s
                    GROUP BY d.id
                """, (doc_id,))
                
                return cur.fetchone()

    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents using full-text search."""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Periksa apakah konfigurasi sudah ada
                cur.execute("""
                    SELECT COUNT(*) FROM pg_ts_config WHERE cfgname = 'document_search';
                """)
                config_exists = cur.fetchone()["count"] > 0

                if not config_exists:
                    # Buat konfigurasi hanya jika belum ada
                    cur.execute("""
                        CREATE TEXT SEARCH CONFIGURATION document_search (COPY = pg_catalog.english);
                        ALTER TEXT SEARCH CONFIGURATION document_search
                            ALTER MAPPING FOR asciiword, word, numword, asciihword, hword, numhword
                            WITH english_stem;
                    """)

                # Query pencarian dengan ranking
                cur.execute("""
                    WITH search_results AS (
                        SELECT 
                            d.id,
                            d.content,
                            d.entities,
                            d.keywords,
                            ts_rank_cd(
                                to_tsvector('pg_catalog.english', d.content),
                                plainto_tsquery('pg_catalog.english', %s)
                            ) as rank
                        FROM documents d
                        WHERE to_tsvector('pg_catalog.english', d.content) @@ plainto_tsquery('pg_catalog.english', %s)
                    )
                    SELECT 
                        sr.*,
                        COALESCE(json_agg(
                            json_build_object(
                                'image_path', c.image_path,
                                'confidence', c.confidence,
                                'characteristics', c.characteristics,
                                'type', 'chart'
                            )
                        ) FILTER (WHERE c.id IS NOT NULL), '[]'::json) as charts
                    FROM search_results sr
                    LEFT JOIN charts c ON sr.id = c.document_id
                    GROUP BY sr.id, sr.content, sr.entities, sr.keywords, sr.rank
                    ORDER BY sr.rank DESC
                    LIMIT %s
                """, (query, query, limit))
                
                return cur.fetchall()

# Create global repository instance
document_repository = DocumentRepository()
