import os, time, sys
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from requests.exceptions import RequestException
from requests import Session, Response
# Adicionar o diretório pai ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import Config_grafana
    #print(f"✅ Config carregado: URL={Config_grafana.URL}")
except ImportError as e:
    print(f"❌ Erro: Não foi possível importar Config_grafana: {e}")
    sys.exit(1)
class GrafanaTokenManager:
    def __init__(self):
        self.config = self.load_grafana_config()
        if not  Config_grafana.ADMIN_USER or not Config_grafana.ADMIN_PASSWORD:
            raise ValueError("❌ Credenciais do Grafana não configuradas!")
        self.session = Session()
        self.session.auth = (Config_grafana.ADMIN_USER, Config_grafana.ADMIN_PASSWORD)
        self.session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})
        self.sa_id: Optional[int] = None
        self.api_key: Optional[str] = None
    def load_grafana_config(self) -> Dict[str, Any]:
        data_storage: Dict[str, Any] = {
            'wait_timeout': 60,
            'env_file': 'grafana/grafana_api_key.txt',
            'grafana_url': Config_grafana.URL,
            'sa_name': Config_grafana.SERVICE_NAME,
            'token_name': Config_grafana.TOKEN_NAME,
            'api_key': None
        }

        try:
            with open('grafana/grafana_api_key.txt', 'r') as file:
                for line in file:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        if key == "GRAFANA_API_KEY":
                            data_storage['api_key'] = value
                        elif key in ["GRAFANA_TOKEN_NAME", "TOKEN_NAME"]:
                            data_storage['token_name'] = value
                        elif key in ["SA_NAME", "GRAFANA_SA_NAME", "SERVICE_ACCOUNT_NAME"]:
                            data_storage['sa_name'] = value
                        elif key == "ENV_FILE":
                            data_storage['env_file'] = value
                        elif key == "GRAFANA_URL":
                            data_storage['grafana_url'] = value
        except FileNotFoundError:
            print("⚠️  Arquivo grafana_api_key.txt não encontrado")

        if not data_storage['sa_name'] or not data_storage['token_name']:
            raise ValueError("❌ SA_NAME e TOKEN_NAME são obrigatórios")

        return data_storage
    def _request(self, method: str, path: str, **kwargs) -> Response:
        url = f"{Config_grafana.URL}{path}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    def wait_for_grafana(self):
        print("⏳ Aguardando inicialização do Grafana...")
        timeout = self.config.get('wait_timeout', 60)
        for attempt in range(timeout):
            try:
                r = self._request("GET", "/api/health", timeout=5)
                if r.status_code == 200:
                    print("✅ Grafana está operacional")
                    return
            except Exception:
                time.sleep(1)
        raise TimeoutError("Timeout excedido aguardando Grafana")
    def get_service_account_id(self) -> Optional[int]:
        r = self._request("GET", "/api/serviceaccounts/search", params={'query': self.config['sa_name']})
        for acc in r.json().get('serviceAccounts', []):
            if acc.get("name") == self.config['sa_name']:
                return acc.get("id")
        return None
    def create_service_account(self) -> int:
        print(f"📌 Verificando service account: {self.config['sa_name']}")
        self.sa_id = self.get_service_account_id()
        if self.sa_id:
            print(f"ℹ️ Service account já existe (ID: {self.sa_id})")
            return self.sa_id
        r = self._request("POST", "/api/serviceaccounts", json={
            'name': self.config['sa_name'], 'role': 'Admin'
        })
        #print("✅ Service account criada com sucesso")
        return r.json()['id']
    def get_existing_token_id(self) -> Optional[int]:
        if not self.sa_id:
            return None
        r = self._request("GET", f"/api/serviceaccounts/{self.sa_id}/tokens")
        for token in r.json():
            if token.get('name') == self.config['token_name']:
                return token.get('id')
        return None
    def _delete_token_by_id(self, token_id: int):
        try:
            self._request("DELETE", f"/api/serviceaccounts/{self.sa_id}/tokens/{token_id}")
            #print(f"♻️ Token removido (ID: {token_id})")
        except Exception as e:
            print(f"⚠️ Erro ao remover token: {e}")
    def _validate_token(self, token: str) -> bool:
        if not token:
            return False
        try:
            test_url = f"{Config_grafana.URL}/api/datasources"
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(test_url, headers=headers, timeout=5)
            return r.status_code == 200
        except Exception:
            return False
    def create_api_token(self) -> str:
        token = self.config.get("api_key")
        if token and self._validate_token(token):
            print("🔁 Usando token existente válido")
            return token

        existing_id = self.get_existing_token_id()
        if existing_id:
            self._delete_token_by_id(existing_id)

        r = self._request("POST", f"/api/serviceaccounts/{self.sa_id}/tokens", json={
            'name': self.config['token_name'], 'role': 'Admin'
        })
        token = r.json().get('key')
        if not self._validate_token(token):
            raise ValueError("Token criado inválido")
        self.update_env_file(token)
        return token
    def update_env_file(self, token: str):
        file_path = Path(self.config['env_file'])
        file_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        if file_path.exists():
            lines = file_path.read_text().splitlines()

        updated = False
        output = []
        for line in lines:
            if line.startswith("GRAFANA_API_KEY="):
                output.append(f"GRAFANA_API_KEY={token}")
                updated = True
            else:
                output.append(line)

        if not updated:
            output.append(f"GRAFANA_API_KEY={token}")

        file_path.write_text("\n".join(output) + "\n")
        print(f"📄 Token atualizado em {file_path.resolve()}")
    def execute_workflow(self) -> str:
        self.wait_for_grafana()
        self.sa_id = self.get_service_account_id() or self.create_service_account()
        token = self.create_api_token()
        self.api_key = token
        print("✅ Token válido disponível")
        return token
if __name__ == "__main__":
    try:
        manager = GrafanaTokenManager()
        token = manager.execute_workflow()
        print(f"🔑 Token: {token[:20]}...")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
