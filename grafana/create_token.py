import os
from typing import Dict, Any, Optional
from dontenv import load_dotenv
from pathlib import Path
from requests.exceptions import RequestException,HTTPError
from requests import Session, RequestException, Response

class GrafanaTokenManager:
    """Gerencia tokens de service accounts no Grafana com atualização segura do .env"""

    def __init__(self):
        load_dotenv()
        self.config: Dict[str, Any] = {
            'grafana_url': os.getenv("GRAFANA_URL", "http://dashboard:3000"),
            'admin_user': os.getenv("GF_SECURITY_ADMIN_USER", "admin"),
            'admin_pass': os.getenv("GF_SECURITY_ADMIN_PASSWORD", "admin"),
            'sa_name': os.getenv("GRAFANA_SA_NAME", "dashboards-service-v2"),
            'token_name': os.getenv("GRAFANA_TOKEN_NAME", "dashboard-token"),
            'max_wait': int(os.getenv("GRAFANA_WAIT_TIMEOUT", "60")),
            'api_key': os.getenv("GRAFANA_API_KEY"),
            'env_file': os.getenv("ENV_FILE_PATH", ".env"),
            'backend_url': os.getenv("BACKEND_URL"),
            "host_db": os.getenv("HOST_DB"),
            "ports_db": os.getenv("PORTS_POSTGRES"),
            "postgres_database": os.getenv("POSTGRES_DB"),
            "postgres_user": os.getenv("POSTGRES_USER"),
            "postgres_password": os.getenv("POSTGRES_PASSWORD")

            
            

        }
      

        self.session = Session()
        self.session.auth = (self.config['admin_user'], self.config['admin_pass'])
        self.session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})

    def _request(self, method: str, path: str, **kwargs) -> Response:
        """Faz uma requisição HTTP com tratamento de erro"""
        url = f"{self.config['grafana_url']}{path}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def wait_for_grafana(self) -> None:
        logger.info("⏳ Aguardando inicialização do Grafana...")
        for attempt in range(1, self.config['max_wait'] + 1):
            try:
                response = self._request("GET", "/api/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Grafana está operacional")
                    return
            except RequestException:
                time.sleep(1)
        raise TimeoutError("Timeout excedido ao aguardar pelo Grafana")

    def get_service_account_id(self) -> Optional[int]:
        try:
            response = self._request("GET", "/api/serviceaccounts/search", params={'query': self.config['sa_name']})
            for acc in response.json().get('serviceAccounts', []):
                if acc.get("name") == self.config['sa_name']:
                    return acc.get("id")
        except Exception as e:
            logger.warning(f"Erro ao buscar service account: {e}")
        return None

    def create_service_account(self) -> Optional[int]:
        logger.info(f"📌 Verificando service account: {self.config['sa_name']}")
        self.sa_id = self.get_service_account_id()
        if self.sa_id:
            logger.info(f"ℹ️ Service account já existe (ID: {self.sa_id})")
            return self.sa_id

        try:
            response = self._request("POST", "/api/serviceaccounts", json={
                'name': self.config['sa_name'], 'role': 'Admin'
            })
            logger.info("✅ Service account criada com sucesso")
            return response.json()['id']
        except RequestException as e:
            if e.response is not None and e.response.status_code == 400 and 'already exists' in e.response.text:
                logger.info("ℹ️ Service account foi criada concorrentemente")
                return self.get_service_account_id()
            raise

    def get_existing_token_id(self) -> Optional[int]:
        try:
            response = self._request("GET", f"/api/serviceaccounts/{self.sa_id}/tokens")
            for token in response.json():
                if token.get('name') == self.config['token_name']:
                    return token.get('id')
        except Exception as e:
            logger.warning(f"Erro ao buscar token existente: {e}")
        return None

    def _is_valid_token(self, token: str) -> bool:
        return bool(re.fullmatch(r"glsa_[\w\-]{20,}", token))

    def _delete_token_by_id(self, token_id: int) -> bool:
        try:
            self._request("DELETE", f"/api/serviceaccounts/{self.sa_id}/tokens/{token_id}")
            #logger.info(f"♻️ Token removido (ID: {token_id})")
            return True
        except Exception as e:
            logger.warning(f"Falha ao remover token: {e}")
            return False

    def create_api_token(self) -> str:
        token = self.config.get("api_key")
        logger.debug(f"♻️ ♻️ ♻️ ♻️ ♻️ ♻️ ♻️ ♻️ ♻️ ♻️ ♻️ {token}")

        # se ja existe um token valido, reutiliza
        if token and self._is_valid_token(token):
            logger.info("🔁 Usando token existente do .env")
            return token 
        existing_id = self.get_existing_token_id()
        if existing_id:
            logger.info(f"♻️ Removendo token antigo (ID: {existing_id})")
            self._delete_token_by_id(existing_id)

        response = self._request("POST", f"/api/serviceaccounts/{self.sa_id}/tokens", json={
            'name': self.config['token_name'], 'role': 'Admin'
        })
        #logger.debug(f"🔐 Token bruto: {token}")
        token = response.json().get('key')
        if not self._is_valid_token(token):
            raise ValueError("Token criado é inválido")
        self.config['api_key'] = token
        return token 

    def update_env_file(self, token: str) -> None:
        env_path = Path(self.config['env_file'])
        env_path.touch(exist_ok=True)
        content = env_path.read_text()
        lines = content.splitlines()
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

        final = "\n".join(output) + ("\n" if content.endswith("\n") else "")
        tmp = env_path.with_suffix(".tmp")
        tmp.write_text(final)
        tmp.replace(env_path)
        #logger.info(f"📄 .env atualizado com segurança em {env_path}")
    def _validate_existing_token(self, token: str) -> bool:
        """Verifica se o token atual é válido"""
        try:
            test_url = f"{self.config['grafana_url']}/api/datasources"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            response = requests.get(test_url, headers=headers, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    def execute_workflow(self) -> None:
        try:
            self.wait_for_grafana()
            
            # 1. Service Account
            self.sa_id = self.get_service_account_id() or self.create_service_account()
            
            # 2. Validação do Token Existente
            current_token = self.config.get("api_key")
            if current_token and self._validate_existing_token(current_token):
                logger.info("🔁 Usando token existente válido")
                self.api_key = current_token
                return  # Token válido, aborta fluxo
            
            # 3. Criação de Novo Token
            new_token = self.create_api_token()
            self.config["api_key"] = new_token
            self.api_key = new_token
            self.update_env_file(new_token)
            logger.info("✅ Novo token criado e armazenado")
        except Exception as e:
            logger.error(f"❌ Falha crítica: {e}")
            raise
