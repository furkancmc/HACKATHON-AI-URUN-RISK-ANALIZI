-- pgvector extension'ını etkinleştir
CREATE EXTENSION IF NOT EXISTS vector;

-- Veritabanı ayarlarını optimize et
ALTER SYSTEM SET shared_preload_libraries = 'vector';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Ayarları yeniden yükle
SELECT pg_reload_conf();

-- Vektör indeksleri için özel ayarlar
CREATE OR REPLACE FUNCTION create_vector_index(table_name text, column_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_%I ON %I USING ivfflat (%I vector_cosine_ops) WITH (lists = 100)', 
                   table_name, column_name, table_name, column_name);
END;
$$ LANGUAGE plpgsql; 