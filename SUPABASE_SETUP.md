# Supabase SQL Setup for RayMine

## Create memories table
```sql
CREATE TABLE IF NOT EXISTS memories (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for full-text search
CREATE INDEX IF NOT EXISTS memories_content_idx ON memories USING GIN (to_tsvector('english', content));

-- Create index for category filtering
CREATE INDEX IF NOT EXISTS memories_category_idx ON memories (category);

-- Optional: Enable pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE memories ADD COLUMN IF NOT EXISTS embedding vector(1536);
CREATE INDEX IF NOT EXISTS memories_embedding_idx ON memories USING ivfflat (embedding vector_cosine_ops);
```

## Supabase RLS Policy (Optional)
```sql
-- Enable RLS
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;

-- Allow all operations in development
CREATE POLICY "Allow all" ON memories
    FOR ALL USING (true)
    WITH CHECK (true);
```

## Run Setup
1. Go to Supabase Dashboard
2. Navigate to SQL Editor
3. Create a new query
4. Paste the SQL above
5. Execute

After setup, your Supabase is ready for RayMine!
