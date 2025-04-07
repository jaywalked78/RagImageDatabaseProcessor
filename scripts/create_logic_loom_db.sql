-- TheLogicLoomDB Schema
-- A comprehensive database for managing content embeddings, metadata, and relationships

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set up schemas
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS embeddings;
CREATE SCHEMA IF NOT EXISTS metadata;
CREATE SCHEMA IF NOT EXISTS relationships;

-- Core Tables --

-- Source videos table
CREATE TABLE IF NOT EXISTS content.videos (
    video_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    duration INTEGER,  -- in seconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    folder_path TEXT,
    source_url TEXT,
    tool_used TEXT[],  -- array of tools used in the video
    topics TEXT[]      -- array of topics covered
);

-- Video frames table
CREATE TABLE IF NOT EXISTS content.frames (
    frame_id TEXT PRIMARY KEY,
    video_id TEXT REFERENCES content.videos(video_id),
    timestamp FLOAT NOT NULL,  -- seconds from start of video
    frame_number INTEGER,
    image_url TEXT,            -- URL to the image in Google Drive
    sequence_index INTEGER,    -- position in sequence
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    folder_name TEXT,
    file_name TEXT,
    UNIQUE(video_id, frame_number)
);

-- Frame metadata table - detailed information about each frame
CREATE TABLE IF NOT EXISTS metadata.frame_details (
    frame_id TEXT REFERENCES content.frames(frame_id),
    description TEXT,           -- detailed description of what's in the frame
    summary TEXT,               -- brief summary
    tools_used TEXT[],          -- tools visible or used in this frame
    actions_performed TEXT[],   -- actions being performed
    technical_details JSONB,    -- structured technical data
    workflow_stage TEXT,        -- e.g., "configuration", "testing", "deployment"
    context_relationship TEXT,  -- relationship to previous frames
    tags TEXT[],                -- searchable tags
    PRIMARY KEY (frame_id)
);

-- Content pieces - segments derived from videos
CREATE TABLE IF NOT EXISTS content.segments (
    segment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT REFERENCES content.videos(video_id),
    start_timestamp FLOAT,
    end_timestamp FLOAT,
    title TEXT,
    description TEXT,
    transcript TEXT,            -- text content/transcript
    key_points TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Content ideas generated from the videos/frames
CREATE TABLE IF NOT EXISTS content.ideas (
    idea_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    content_type TEXT NOT NULL, -- 'longform', 'shortform', etc.
    target_platform TEXT,       -- 'youtube', 'instagram', etc.
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'draft', -- 'draft', 'in_progress', 'published'
    tags TEXT[]
);

-- External content sources (Reddit, YouTube, GitHub)
CREATE TABLE IF NOT EXISTS content.external_sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform TEXT NOT NULL,     -- 'reddit', 'youtube', 'github', etc.
    external_id TEXT,           -- original ID from the source platform
    title TEXT,
    content TEXT,               -- could be post body, comment, etc.
    url TEXT,
    author TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB              -- platform-specific metadata
);

-- Folder structure and summaries
CREATE TABLE IF NOT EXISTS content.folders (
    folder_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    folder_path TEXT NOT NULL UNIQUE,
    parent_folder TEXT,
    name TEXT NOT NULL,
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vector embeddings tables --

-- Text embeddings
CREATE TABLE IF NOT EXISTS embeddings.text_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_id TEXT NOT NULL,         -- ID of the referenced content (video_id, frame_id, etc.)
    reference_type TEXT NOT NULL,       -- Type of content ('video', 'frame', 'segment', 'idea', etc.)
    text_content TEXT NOT NULL,         -- The original text that was embedded
    embedding vector(1024) NOT NULL,    -- Voyager embedding vector (adjust dimension as needed)
    model_name TEXT NOT NULL,           -- e.g., 'voyage-large-2', to track which model was used
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Multimodal embeddings (text + image)
CREATE TABLE IF NOT EXISTS embeddings.multimodal_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_id TEXT NOT NULL,        -- typically frame_id
    reference_type TEXT NOT NULL,      -- typically 'frame'
    text_content TEXT,                 -- Text component used for embedding
    image_url TEXT NOT NULL,           -- URL to the image used for embedding
    embedding vector(1024) NOT NULL,   -- Multimodal embedding vector
    model_name TEXT NOT NULL,          -- e.g., 'voyage-large-2-multimodal'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Relationship tables --

-- Content relationships (relates ideas to source content)
CREATE TABLE IF NOT EXISTS relationships.content_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL,           -- e.g., idea_id
    source_type TEXT NOT NULL,         -- e.g., 'idea'
    target_id TEXT NOT NULL,           -- e.g., segment_id, video_id, frame_id
    target_type TEXT NOT NULL,         -- e.g., 'segment', 'video', 'frame'
    relationship_type TEXT NOT NULL,   -- e.g., 'derived_from', 'references', 'includes'
    strength FLOAT,                    -- optional: strength of relationship (0.0-1.0)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Frame sequences (for tracking frame ordering and relationships)
CREATE TABLE IF NOT EXISTS relationships.frame_sequences (
    sequence_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id TEXT REFERENCES content.videos(video_id),
    frame_id TEXT REFERENCES content.frames(frame_id),
    prev_frame_id TEXT REFERENCES content.frames(frame_id),
    next_frame_id TEXT REFERENCES content.frames(frame_id),
    sequence_index INTEGER NOT NULL,
    context_note TEXT,            -- notes about the transition or sequence
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Similarity table (for pre-computed similarities)
CREATE TABLE IF NOT EXISTS relationships.similarities (
    similarity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    similarity_score FLOAT NOT NULL,   -- 0.0 to 1.0
    computation_method TEXT NOT NULL,  -- e.g., 'cosine', 'dot_product'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes --

-- Create indexes for text search
CREATE INDEX IF NOT EXISTS idx_videos_title_description ON content.videos USING gin (to_tsvector('english', title || ' ' || COALESCE(description, '')));
CREATE INDEX IF NOT EXISTS idx_frame_details_description ON metadata.frame_details USING gin (to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_ideas_title_description ON content.ideas USING gin (to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Create trigram indexes for fuzzy matching
CREATE INDEX IF NOT EXISTS idx_videos_title_trgm ON content.videos USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_ideas_title_trgm ON content.ideas USING gin (title gin_trgm_ops);

-- Create indexes for vector search (cosine similarity)
CREATE INDEX IF NOT EXISTS idx_text_embeddings_vector ON embeddings.text_embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_multimodal_embeddings_vector ON embeddings.multimodal_embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create indexes for relationship lookups
CREATE INDEX IF NOT EXISTS idx_content_rel_source ON relationships.content_relationships(source_id, source_type);
CREATE INDEX IF NOT EXISTS idx_content_rel_target ON relationships.content_relationships(target_id, target_type);
CREATE INDEX IF NOT EXISTS idx_frame_sequences_video ON relationships.frame_sequences(video_id);

-- Create indexes for frame lookups
CREATE INDEX IF NOT EXISTS idx_frames_video_timestamp ON content.frames(video_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_frames_folder ON content.frames(folder_name);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create update timestamp triggers for all tables with updated_at
CREATE TRIGGER update_videos_timestamp
BEFORE UPDATE ON content.videos
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_text_embeddings_timestamp
BEFORE UPDATE ON embeddings.text_embeddings
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_multimodal_embeddings_timestamp
BEFORE UPDATE ON embeddings.multimodal_embeddings
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_folders_timestamp
BEFORE UPDATE ON content.folders
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Comments
COMMENT ON TABLE content.videos IS 'Source videos containing n8n workflows and automation demonstrations';
COMMENT ON TABLE content.frames IS 'Individual frames extracted from videos with timestamp information';
COMMENT ON TABLE metadata.frame_details IS 'Detailed metadata about frame content, actions, and context';
COMMENT ON TABLE content.segments IS 'Content segments derived from videos (e.g., demonstrations of specific workflow steps)';
COMMENT ON TABLE content.ideas IS 'Content ideas for social media generated from video content';
COMMENT ON TABLE content.external_sources IS 'External content from Reddit, YouTube, GitHub for cross-referencing';
COMMENT ON TABLE content.folders IS 'Folder structure information with summaries';
COMMENT ON TABLE embeddings.text_embeddings IS 'Vector embeddings for text content using Voyager models';
COMMENT ON TABLE embeddings.multimodal_embeddings IS 'Vector embeddings for combined text and image content';
COMMENT ON TABLE relationships.content_relationships IS 'Relationships between different content pieces';
COMMENT ON TABLE relationships.frame_sequences IS 'Sequential relationships between frames';
COMMENT ON TABLE relationships.similarities IS 'Pre-computed similarity scores between content pieces'; 