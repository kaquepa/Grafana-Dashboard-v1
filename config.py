from pathlib import Path
from dotenv import load_dotenv
import os
from typing import Dict, Any

class GrafanaConfig:
    def __init__(self, env_file: str = None):
        # 1️⃣ Define caminho padrão
        if env_file is None:
            env_file = Path(__file__).parent / 'grafana/grafana_api_key.txt'

        env_path = Path(env_file)
        if not env_path.exists():
            print(f"⚠️ Arquivo {env_path.resolve()} não encontrado!")
        else:
            print(f"📄 Carregando configurações de: {env_path.resolve()}")
            self._load_env_file(env_path)

        # 2️⃣ Definir variáveis com fallback
        self.URL = os.getenv("GRAFANA_URL", "http://grafana:3000")
        self.ADMIN_USER = os.getenv("GF_SECURITY_ADMIN_USER", "admin")
        self.ADMIN_PASSWORD = os.getenv("GF_SECURITY_ADMIN_PASSWORD", "admin")
        self.SERVICE_NAME = os.getenv("SA_NAME", "dashboards-service-v2")
        self.TOKEN_NAME = os.getenv("GRAFANA_TOKEN_NAME", "dashboard-token")
        self.API_KEY = os.getenv("GRAFANA_API_KEY", None)
        self.WAIT_TIMEOUT = int(os.getenv("GRAFANA_WAIT_TIMEOUT", 60))

    def _load_env_file(self, filepath: Path):
        """
        Lê um arquivo tipo .env (CHAVE=VALOR) ignorando comentários e espaços
        e define variáveis no os.environ.
        """
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Remove possíveis aspas e caracteres estranhos no final
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                os.environ[key] = value


class DatabaseConfig:
    def __init__(self, env_file: str = None):
        # Define o path do .env automaticamente se não fornecido
        if env_file is None:
            env_file = Path(__file__).parent / ".env"
        load_dotenv(dotenv_path=env_file)
        self.USER              = os.getenv("POSTGRES_USER")
        self.PASSWORD          = os.getenv("POSTGRES_PASSWORD")
        self.DATABASE          = os.getenv("POSTGRES_DB")
        self.HOST              = os.getenv("POSTGRES_HOST")
        self.PORT              = os.getenv("POSTGRES_PORT", 5432)
        self.connection_string = (
            f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user":     self.USER,
            "password": self.PASSWORD,
            "database": self.DATABASE,
            "host":     self.HOST,
            "port":     self.PORT,
            "connection_string": self.connection_string
        }

# Instância global
Config_database = DatabaseConfig()
Config_grafana  = GrafanaConfig()


 