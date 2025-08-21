-- infrastructure/01_init.sql
-- Script de inicialização do PostgreSQL

-- Conectar ao banco principal (já criado automaticamente via POSTGRES_DB)
\c Grafana_DB;

-- Criar extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- O usuário Postgres_Admin já existe (criado via POSTGRES_USER)
-- Apenas garantir que tem as permissões necessárias

-- Criar schema para aplicação se necessário
CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION "Postgres_Admin";

-- Garantir privilégios completos
GRANT ALL PRIVILEGES ON DATABASE "Grafana_DB" TO "Postgres_Admin";
GRANT ALL PRIVILEGES ON SCHEMA public TO "Postgres_Admin";
GRANT ALL PRIVILEGES ON SCHEMA app TO "Postgres_Admin";

-- Definir search_path padrão
ALTER USER "Postgres_Admin" SET search_path TO app, public;

-- Log de confirmação
SELECT 'Database initialization completed successfully' AS status;