ALTER TABLE project_settings 
ADD COLUMN IF NOT EXISTS llm_provider TEXT NOT NULL DEFAULT 'openai';

ALTER TABLE project_settings 
ADD CONSTRAINT llm_provider_check 
CHECK (llm_provider IN ('openai', 'ollama'));