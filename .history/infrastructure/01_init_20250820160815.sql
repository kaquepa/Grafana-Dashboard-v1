-- infrastructure/01_init.sql
-- Verifica se o usuário existe antes de criar
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'Postgre_Admin') THEN
        CREATE USER "Postgre_Admin" WITH PASSWORD 'secure_password_123';
    END IF;
END
$$;

-- Verifica se o banco existe antes de criar
SELECT 'CREATE DATABASE "Grafana_DB" WITH OWNER "Postgres_Admin"'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'Grafana_DB')\gexec

-- Garante privilégios
GRANT ALL PRIVILEGES ON DATABASE "Grafana_DB" TO "Postgres_Admin";