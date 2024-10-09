import os
import json
import logging

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

BASE_URL = os.getenv('BASE_URL')

def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Erro ao acessar {url}: {e}")
        return None

def groups_dic_generator(base_url):
    html_content = fetch_page_content(base_url)
    if not html_content:
        return {}

    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr')
    grupos = {}

    for row in rows:
        td = row.find('td')
        if td and td.string == '🟢':
            th = row.find('th')
            if th:
                a_tag = th.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    group_name = a_tag.text.strip()
                    group_url = base_url + a_tag['href']
                    grupos[group_name] = {
                        'link_grupo': group_url,
                        'links_online': []
                    }
    return grupos

def get_links_online(base_url):
    grupos = groups_dic_generator(base_url)
    
    for grupo, info in grupos.items():
        logger.info(f"Grupo: {grupo}")
        group_url = info['link_grupo']
        logger.info(f"Link do Grupo: {group_url}")

        html_content = fetch_page_content(group_url)
        if not html_content:
            continue
        
        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all('tr')

        for row in rows:
            td = row.find_all('td')
            if len(td) > 1 and td[1].text == '🟢':
                code_tag = td[0].find('code')
                if code_tag:
                    link = code_tag.text.strip()
                    logger.info(f"Link online encontrado: {link}")
                    info['links_online'].append(link)

    return grupos

if __name__ == "__main__":
    if BASE_URL:
        grupos = get_links_online(BASE_URL)
        with open('grupos.json', 'w') as json_file:
            json.dump(grupos, json_file, indent=4, ensure_ascii=False)
        
    else:
        logger.error("BASE_URL não encontrada no arquivo .env")


    
