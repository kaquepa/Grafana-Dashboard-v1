-- Garantir que o usuário existe
CREATE USER "Postgres_Admin" WITH PASSWORD 'secure_password_123';
CREATE DATABASE "Grafana_DB" OWNER "Postgres_Admin";
GRANT ALL PRIVILEGES ON DATABASE "Grafana_DB" TO "Postgres_Admin";