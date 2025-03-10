/*
  # Database Initialization for Research Paper ETL

  1. Database Creation
  2. Tables Setup
  3. Indexes for Performance
  4. Full-Text Search Configuration
*/

-- Create database if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_database WHERE datname = 'studycasevidavox'
    ) THEN
        CREATE DATABASE studycasevidafox;
    END IF;
END
$$;

-- Connect to the database
\c studycasevidafox;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    entities JSONB,
    keywords TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create charts table
CREATE TABLE IF NOT EXISTS charts (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    characteristics JSONB,
    type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create embeddings table for vector search
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    embedding VECTOR(384),  -- Dimension matches the BERT model output
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_keywords ON documents USING GIN (keywords);
CREATE INDEX IF NOT EXISTS idx_documents_entities ON documents USING GIN (entities);
CREATE INDEX IF NOT EXISTS idx_charts_document_id ON charts(document_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_document_id ON embeddings(document_id);

-- Create full-text search index
ALTER TABLE documents ADD COLUMN IF NOT EXISTS document_vector tsvector;
CREATE INDEX IF NOT EXISTS idx_fts_document ON documents USING GIN (document_vector);

-- Create trigger to update full-text search vector
CREATE OR REPLACE FUNCTION documents_trigger() RETURNS trigger AS $$
BEGIN
    NEW.document_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'A');
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tsvector_update ON documents;
CREATE TRIGGER tsvector_update 
    BEFORE INSERT OR UPDATE ON documents 
    FOR EACH ROW 
    EXECUTE FUNCTION documents_trigger();

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update timestamp triggers
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_charts_updated_at
    BEFORE UPDATE ON charts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Create extension for vector operations if not exists
CREATE EXTENSION IF NOT EXISTS vector;