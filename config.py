from pathlib import Path
from dotenv import load_dotenv
import os
from typing import Dict, Any

class DatabaseConfig:
    def __init__(self, env_file: str = None):
        # Define o path do .env automaticamente se não fornecido
        if env_file is None:
            env_file = Path(__file__).parent / ".env"
        load_dotenv(dotenv_path=env_file)
        
        self.host = os.getenv("HOST_DB", "localhost")
        self.database = os.getenv("POSTGRES_DB", "mydatabase")
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.sslmode = os.getenv("DB_SSLMODE", "disable")
        
        self.connection_string = (
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "port": self.port,
            "sslmode": self.sslmode,
            "connection_string": self.connection_string
        }

# Instância global
DatabaseConfig = DatabaseConfig()
