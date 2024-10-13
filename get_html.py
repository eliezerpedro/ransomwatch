import os
import json
import re
import requests
import logging
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GetHtml:
    def __init__(self, json_file='groups.json', days=7):
        self.json_file = json_file
        self.days = days
        self.df = pd.DataFrame()

    def load_data(self):
        """Carrega dados do arquivo JSON e cria um DataFrame."""
        with open(self.json_file, 'r') as file:
            data = json.load(file)

        self.df = pd.DataFrame.from_dict(
            data, orient='index').explode('online_links')
        self.df.reset_index(inplace=True)
        self.df.columns = ['grupo', 'link_grupo', 'links_online']

        self.df['response_status_code'] = None
        self.df['html'] = None
        self.df['infos'] = None
        self.df['datas'] = None
        self.df['qtd_datas'] = None

    @staticmethod
    def extract_dates(html, days):
        """Extrai datas do HTML fornecido, filtrando por um intervalo de dias."""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',           # AAAA-MM-DD
            r'\d{2}/\d{2}/\d{4}',           # DD/MM/AAAA
            r'\d{1,2} de \w+ de \d{4}',     # DD de Mês de AAAA
            r'\d{4}\.\d{2}\.\d{2}',         # AAAA.MM.DD
            r'\w+ \d{1,2}, \d{4}',          # Mês DD, AAAA
            r'\d{2}-\d{2}-\d{4}',           # DD-MM-AAAA
            r'\w{3} \d{1,2}, \d{4}',        # Mês Abreviado DD, AAAA
            r'\d{1,2} \w{3} \d{4}',         # DD Mon AAAA
            r'\d{4}/\d{2}/\d{2}',           # AAAA/MM/DD
            r'\d{8}',                       # AAAAMMDD
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO 8601
            r'\w+ de \d{4}',                # Mês por Extenso e Ano
            r'\w+ \d{1,2}(?:st|nd|rd|th), \d{4}',  # Mês e Dia por Extenso
            r'\d{4}\w{3}\d{2}',             # AAAA-MêsAbreviado-DD
            r'\d{2}/\d{2}/\d{2}',           # Dia/Mês/Ano Abreviado
            r'\w{3}, \d{4}',                # Mês Abreviado e Ano
            r'\d{4}-\d{2}',                 # Ano e Mês
            # Ano, Mês Abreviado e Dia por Extenso
            r'\d{4}, \w{3} \d{1,2}(?:st|nd|rd|th)',
            r'\d{2}\.\d{2}\.\d{4}',         # Formato Alemão
            r'\d{4}年\d{1,2}月\d{1,2}日',   # Formato Chinês
        ]

        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        dates = []
        for pattern in date_patterns:
            found_dates = re.findall(pattern, text)
            dates.extend(found_dates)

        collected_dates = []
        for date_str in dates:
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d de %B de %Y', '%Y.%m.%d', '%B %d, %Y']:
                try:
                    date = datetime.strptime(date_str, fmt)
                    if (datetime.now() - timedelta(days)) <= date <= datetime.now():
                        collected_dates.append(date_str)
                    break
                except ValueError:
                    continue

        return collected_dates

    def fetch_data(self):
        """Faz requisições HTTP para os links no DataFrame e processa os dados."""
        proxies = {
            'http': f"socks5h://{os.getenv('PROXY_HOST')}:{os.getenv('PROXY_PORT')}",
            'https': f"socks5h://{os.getenv('PROXY_HOST')}:{os.getenv('PROXY_PORT')}"
        }

        for index, row in self.df.iterrows():
            url = row['links_online']
            try:
                response = requests.get(url, proxies=proxies, timeout=10)
                self.df.at[index, 'response_status_code'] = response.status_code

                if response.status_code == 200:
                    logger.info(f"Acesso bem-sucedido ao link {url}")
                    self.df.at[index, 'html'] = response.text
                    datas = self.extract_dates(response.text, self.days)
                    self.df.at[index, 'infos'] = bool(datas)
                    self.df.at[index, 'datas'] = datas
                    self.df.at[index, 'qtd_datas'] = len(datas)
                else:
                    logger.warning(
                        f"Status {response.status_code} ao acessar {url}")

            except requests.RequestException as e:
                logger.error(f"Erro ao acessar {url}: {e}")
                self.df.at[index, 'response_status_code'] = 'erro'

    def run(self):
        """Método principal para executar as operações da classe."""
        self.load_data()
        self.fetch_data()
        return self.df
