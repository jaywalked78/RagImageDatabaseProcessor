-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table with pgvector column
CREATE TABLE IF NOT EXISTS embeddings (
  doc_id TEXT PRIMARY KEY,
  embedding vector(768) NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster similarity search (IVF index)
CREATE INDEX IF NOT EXISTS idx_embedding_cosine 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

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