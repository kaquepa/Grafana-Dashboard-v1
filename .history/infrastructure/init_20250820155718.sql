-- Garantir que o usuário existe
CREATE USER "Postgre_Admin" WITH PASSWORD 'secure_password_123';
CREATE DATABASE "Grafana_DB" OWNER "Postgre_Admin";
GRANT ALL PRIVILEGES ON DATABASE "Grafana_DB" TO "Postgre_Admin";