-- Migration: Add LLM Provider Selection
-- Description: Adds llm_provider column to project_settings table

-- Add llm_provider column with default value
ALTER TABLE project_settings 
ADD COLUMN IF NOT EXISTS llm_provider TEXT NOT NULL DEFAULT 'openai';

-- Add check constraint for valid values
ALTER TABLE project_settings 
ADD CONSTRAINT llm_provider_check 
CHECK (llm_provider IN ('openai', 'ollama'));

-- Add comment for documentation
COMMENT ON COLUMN project_settings.llm_provider IS 'LLM provider: openai or ollama';