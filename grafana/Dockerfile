FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt from python-app directory
COPY python-app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts from grafana directory
COPY grafana/create_service_account.py .
COPY config.py .
COPY grafana/grafana_api_key.txt .

CMD ["python", "create_service_account.py"]