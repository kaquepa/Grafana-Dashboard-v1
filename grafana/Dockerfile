FROM grafana/grafana:latest

# Apenas limpar cache se existir (não tocar nos plugins built-in)
USER root
RUN rm -rf /var/lib/grafana/plugins-cache/* 2>/dev/null || true \
    && rm -rf /var/lib/grafana/tmp/* 2>/dev/null || true

# Voltar para usuário padrão
USER grafana

# Expor porta
EXPOSE 3000