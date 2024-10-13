FROM debian:latest

RUN apt-get update && \
    apt-get install -y tor curl && \
    apt-get clean

CMD ["tor"]