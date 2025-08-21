-- infrastructure/01_init.sql
-- Script de inicialização simplificado

-- Conectar ao banco criado automaticamente
\c grafana;

-- Criar extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Criar schema para aplicação
CREATE SCHEMA IF NOT EXISTS app;

-- Dar permissões ao usuário postgres
GRANT ALL PRIVILEGES ON SCHEMA app TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

-- Configurar search_path
ALTER USER postgres SET search_path TO app, public;

-- Log de confirmação
SELECT 'Database initialization completed successfully' AS status;