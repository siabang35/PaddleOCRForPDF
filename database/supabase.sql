/*RUN First  for activate Extension*/
CREATE EXTENSION IF NOT EXISTS vector;


/*AFTER THAT RUN THIS SCRIPT*/
/*
  # Database Initialization for Research Paper ETL in Supabase

  1. Tables Setup
  2. Indexes for Performance
  3. Full-Text Search Configuration
*/

-- Create documents table
CREATE TABLE IF NOT EXISTS public.documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    entities JSONB,
    keywords TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create charts table
CREATE TABLE IF NOT EXISTS public.charts (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES public.documents(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    characteristics JSONB,
    type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create embeddings table for vector search
CREATE TABLE IF NOT EXISTS public.embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES public.documents(id) ON DELETE CASCADE,
    embedding VECTOR(384),  -- Requires pgvector extension
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_keywords ON public.documents USING GIN (keywords);
CREATE INDEX IF NOT EXISTS idx_documents_entities ON public.documents USING GIN (entities);
CREATE INDEX IF NOT EXISTS idx_charts_document_id ON public.charts(document_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_document_id ON public.embeddings(document_id);

-- Create full-text search index
ALTER TABLE public.documents ADD COLUMN IF NOT EXISTS document_vector tsvector;
CREATE INDEX IF NOT EXISTS idx_fts_document ON public.documents USING GIN (document_vector);

-- Create trigger to update full-text search vector
CREATE OR REPLACE FUNCTION public.documents_trigger() RETURNS trigger AS $$
BEGIN
    NEW.document_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'A');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tsvector_update ON public.documents;
CREATE TRIGGER tsvector_update 
    BEFORE INSERT OR UPDATE ON public.documents 
    FOR EACH ROW 
    EXECUTE FUNCTION public.documents_trigger();

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add update timestamp triggers
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_charts_updated_at
    BEFORE UPDATE ON public.charts
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Ensure pgvector extension exists
CREATE EXTENSION IF NOT EXISTS vector;

