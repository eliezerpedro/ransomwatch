# Ransomwatch

## Visão geral

Esse projeto acessa os links onlines do site https://cti.fyi/ e checa informações publicadas em um dado periodo de tempo


## Variáveis

 

- Days

  

## Desafio

  

Esse desafio usa bibliotecas como BeautifulSoup, requests e pandas para coletar os dados dos sites disponibilizados no período estabelecido.

  

1. Configura um ambiente que possibilita o acesso à rede TOR usando Docker
2. Acessa o site https://cti.fyi/
3. Faz uma requisição para cada blog disponível, coleta os links online, adiciona todos esses links em um dicionário e salva no arquivo groups.json
4. Faz uma requisição para cada link online, caso a conexão seja bem sucedida, pesquisa no response.text datas no período estabelecido e salva todos os dados em um dataframe
5. Prepara o DataFrame filtrando apenas os grupos que possuem publicações no período estabelecido
6. Coleta de cada site data, titulo, site (se disponível) e salva em uma lista de dicionários
7. Gera o arquivo ransomscraper.pdf com as informações coletadas
8. Envia por email os arquivos groups.json e ransomscraper.pdf

  

## Dependências

  



- Python 3.x
- beautifulsoup4
- python-dotenv
- pandas
- requests
- reportlab
  

## Como usar

  

1. Clone the repository.
2. Crie a imagem Docker e execute o container
```bash

cd tor-docker
docker build -t meu_tor_container .
docker run -d --name meu_container_tor meu_tor_container

```

3. Instale as dependencias usando o pip
 

```bash

pip install -r requirements.txt

```
4. Crie um arquivo .env com as variáveis abaixo

```bash

BASE_URL=https://cti.fyi/

DAYS=(periodo em dias)

PROXY_HOST=host

PROXY_PORT=porta

EMAIL_USER=email do usuário

EMAIL_PASS=senha do usuário

EMAIL_SENDER=email do usuário

EMAIL_RECIPIENT=email do destinatário

```

5. Execute o script

  

```bash

python  main.py

```


5. Quando a execução do script acabar, os arquivos groups.json e ransomscraper.pdf encontrados na raiz do projeto, são enviados por email para o destinatário definido no arquivo .env.


---