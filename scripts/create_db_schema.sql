-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table with pgvector column
CREATE TABLE IF NOT EXISTS embeddings (
  doc_id TEXT PRIMARY KEY,
  embedding vector(768) NOT NULL,
  metadata JSONB,
  ocr_data JSONB,
  ocr_text TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster similarity search (IVF index)
CREATE INDEX IF NOT EXISTS idx_embedding_cosine 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create a separate table for OCR data
CREATE TABLE IF NOT EXISTS ocr_data (
  frame_id TEXT PRIMARY KEY,
  raw_text TEXT,
  structured_data JSONB,
  is_flagged BOOLEAN DEFAULT FALSE,
  sensitive_explanation TEXT,
  topics TEXT[],
  content_types TEXT[],
  urls TEXT[],
  word_count INTEGER,
  char_count INTEGER,
  processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create text search index on OCR text
CREATE INDEX IF NOT EXISTS idx_ocr_text_search 
ON ocr_data 
USING gin(to_tsvector('english', raw_text));

-- Create index on frame_id for joins
CREATE INDEX IF NOT EXISTS idx_ocr_frame_id
ON ocr_data(frame_id);

-- Optional: Create a basic trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_embeddings_timestamp
BEFORE UPDATE ON embeddings
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_ocr_timestamp
BEFORE UPDATE ON ocr_data
FOR EACH ROW
EXECUTE FUNCTION update_timestamp(); 