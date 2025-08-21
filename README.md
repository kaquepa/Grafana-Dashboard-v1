# Projeto: Ambiente Docker Compose com Grafana, Python e Postgres

Este projeto utiliza Docker Compose para orquestrar três serviços principais:

- **Postgres**: Banco de dados relacional
- **Grafana**: Visualização de dados
- **Python**: Aplicação de exemplo conectando ao Postgres

## Como usar

1. **Suba os containers:**

```sh
docker-compose up --build
```

2. **Acesse os serviços:**
- Postgres: `localhost:5432` (user: `user`, password: `password`, db: `mydatabase`)
- Grafana: [http://localhost:3000](http://localhost:3000) (usuário/padrão: `admin`/`admin`)
- Python: O container executa `main.py` ao subir e conecta no banco Postgres

3. **Estrutura dos arquivos:**
- `docker-compose.yml`: Orquestra os serviços
- `python-app/`: Código Python de exemplo
- `.github/copilot-instructions.md`: Instruções para automação

## Observações
- Altere as credenciais conforme necessário.
- O Python conecta no Postgres usando a variável de ambiente `DATABASE_URL`.
- O Grafana está configurado para usar o Postgres como backend.

---

> Qualquer dúvida ou necessidade de customização, edite os arquivos conforme seu caso de uso.
