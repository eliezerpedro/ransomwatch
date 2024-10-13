from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import json


class Grupos:
    def __init__(self, days):
        self.days = days
        self.hoje = datetime.now()
        self.limite = self.hoje - timedelta(days=self.days)

    def _parse_date(self, date_str, date_format='%Y-%m-%d'):
        """Converte uma string de data em um objeto datetime."""
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            return None

    def _is_date_within_range(self, date_obj):
        """Verifica se a data está dentro do intervalo definido."""
        return self.limite <= date_obj <= self.hoje

    def ransomhouse(self, html_content):
        json_data = json.loads(html_content)
        filtered_data = []

        for entry in json_data.get('data', []):
            if 'actionDate' in entry:
                date_str = entry['actionDate']
                if date_str:
                    date_obj = self._parse_date(date_str, '%d/%m/%Y')
                    if date_obj and self._is_date_within_range(date_obj):
                        filtered_data.append({
                            'title': entry.get('header', ''),
                            'site': entry.get('url', ''),
                            'date': date_str
                        })

        return filtered_data

    def monti(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []

        divs = soup.find_all('div', class_='col-auto published')
        for div in divs:
            data_texto = div.text.strip()
            data_publicacao = self._parse_date(data_texto, '%Y-%m-%d %H:%M:%S')
            if data_publicacao and self._is_date_within_range(data_publicacao):
                h5 = div.find_previous('h5')
                title = h5.text.strip() if h5 else 'Título não encontrado'
                results.append(
                    {'title': title, 'site': '', 'date': data_texto})

        return results

    def play(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        data_rows = []

        for th in soup.find_all('th', class_='News'):
            title = th.contents[0].strip()
            link_div = th.find('i', class_='link')
            link = link_div.next_sibling.strip() if link_div and link_div.next_sibling else None

            publication_date_div = th.find(
                string=lambda text: text and 'publication date:' in text)
            publication_date = publication_date_div.strip().split(
                ':')[-1].strip() if publication_date_div else None

            if publication_date:
                pub_date = self._parse_date(publication_date)
                if pub_date and self._is_date_within_range(pub_date):
                    data_rows.append(
                        {'title': title, 'site': link, 'date': publication_date})

        return data_rows

    def handala(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []

        for li in soup.find_all('li', class_='wp-block-post'):
            title = li.find('h2').find('a').text
            time_tag = li.find('time')
            if time_tag:
                date_str = time_tag.get('datetime').split('T')[0]
                date_obj = self._parse_date(date_str)
                if date_obj and self._is_date_within_range(date_obj):
                    description = li.find(
                        'p', class_='wp-block-post-excerpt__excerpt').text
                    site_match = re.search(
                        r'\b(?:https?://|www\.)?([\w.-]+(?:\.[a-z]{2,}))\b', description)
                    site = site_match.group(0) if site_match else None
                    results.append(
                        {'title': title, 'site': site, 'date': date_str})

        return results

    def blackbyte(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        nome_empresa = soup.find('caption', class_='target-name').get_text()
        resultados = []

        for td in soup.find_all('td'):
            data = self._parse_date(td.get_text(), '%Y-%m-%d %H:%M')
            if data and self._is_date_within_range(data):
                resultados.append(
                    {'title': nome_empresa, 'site': '', 'date': td.get_text()})

        return resultados
