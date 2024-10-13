import os
import json
import logging
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


class GetOnlineUrls:
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def fetch_page_content(self, url):
        """Fetch the HTML content from the given URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    def generate_groups_dict(self):
        """Generate a dictionary of groups with their URLs."""
        html_content = self.fetch_page_content(self.base_url)
        if not html_content:
            return {}

        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all('tr')
        groups = {}

        for row in rows:
            td = row.find('td')
            if td and td.string == '🟢':
                th = row.find('th')
                if th:
                    a_tag = th.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        group_name = a_tag.text.strip()
                        group_url = self.base_url + a_tag['href']
                        groups[group_name] = {
                            'group_link': group_url,
                            'online_links': []
                        }
        return groups

    def extract_online_links(self, groups):
        """Extract online links for each group."""
        for group, info in groups.items():
            self.logger.info(f"Processing group: {group}")
            group_url = info['group_link']
            self.logger.info(f"Group URL: {group_url}")

            html_content = self.fetch_page_content(group_url)
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
                        self.logger.info(f"Online link found: {link}")
                        info['online_links'].append(link)
        return groups

    def save_to_json(self, data, file_path='groups.json'):
        """Save the group data to a JSON file."""
        try:
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            self.logger.info(f"Data successfully saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving data to {file_path}: {e}")

    def get_online_urls_and_save(self):
        """Main method to get groups, extract links, and save them to a JSON file."""
        groups = self.generate_groups_dict()
        groups_with_links = self.extract_online_links(groups)
        self.save_to_json(groups_with_links)


if __name__ == "__main__":
    BASE_URL = os.getenv('BASE_URL')

    if BASE_URL:
        url_scraper = GetOnlineUrls(BASE_URL)
        url_scraper.get_online_urls_and_save()
    else:
        logging.error("BASE_URL not found in .env file")
