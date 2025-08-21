-- infrastructure/01_init.sql para nomes simples
-- Conectar ao banco já criado automaticamente
\c grafana;

-- Criar extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Criar schema para aplicação
CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION postgres_admin;

-- Garantir permissões
GRANT ALL PRIVILEGES ON SCHEMA app TO postgres_admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres_admin;

-- Configurar search_path
ALTER USER postgres_admin  SET search_path TO app, public;

-- Log de confirmação
SELECT 'Database initialization completed successfully - Simple names version' AS status;