FROM debian:latest

# Instalar dependências
RUN apt-get update && \
    apt-get install -y tor curl && \
    apt-get clean

# Iniciar o Tor
CMD ["tor"]