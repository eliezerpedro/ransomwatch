import logging
import os
from time import sleep

from dotenv import load_dotenv

from grupos import Grupos
from get_html import GetHtml
from get_url import GetOnlineUrls
from save_pdf import DataFrameToMarkdownPDF
from send_email import SendEmail


class Main:
    def __init__(self):
        # Carregar variáveis de ambiente
        load_dotenv()
        self.BASE_URL = os.getenv('BASE_URL')
        self.DAYS = self.load_days()

        # Inicializar classes
        self.url_scraper = GetOnlineUrls(self.BASE_URL)
        self.grupos = Grupos(self.DAYS)
        self.pdf_generator = DataFrameToMarkdownPDF(
            pdf_filename='ransomscraper.pdf')
        self.get_html = GetHtml()

    def load_days(self):
        """Carrega e valida a variável DAYS do ambiente."""
        days = os.getenv('DAYS')
        try:
            return int(days)
        except (ValueError, TypeError):
            logging.error("DAYS must be an integer.")
            raise

    def run(self):
        """Executa o fluxo principal da aplicação."""
        self.scrape_urls()
        df = self.get_html.run()
        df_to_analyze = self.prepare_dataframe(df)
        data = self.processar_grupos(df_to_analyze)

        # Gerar PDF
        self.pdf_generator.generate_pdf(data, df)

        # Enviar email com os arquivos gerados
        self.send_email()

    def scrape_urls(self):
        """Obtém as URLs online e as salva."""
        if self.BASE_URL:
            self.url_scraper.get_online_urls_and_save()
        else:
            logging.error("BASE_URL not found in .env file")

    def prepare_dataframe(self, df):
        """Prepara o DataFrame filtrando os dados disponíveis."""
        df_disponivel = df[df['infos'] == True]
        df_to_analyze = df_disponivel.drop_duplicates(subset='html')
        df_to_analyze = df_to_analyze.drop_duplicates(subset='grupo')
        df_to_analyze.reset_index(drop=True, inplace=True)
        return df_to_analyze

    def processar_grupos(self, df_to_analyze):
        """Processa os grupos e retorna os resultados."""
        resultados = []

        for index, row in df_to_analyze.iterrows():
            grupo = row['grupo']
            html_content = row['html']
            try:
                result = self.scrape_group(grupo, html_content)
                for item in result:
                    item['grupo'] = grupo
                    resultados.append(item)
            except Exception as e:
                logging.error(f"Erro ao processar o grupo '{grupo}': {e}")

        return resultados

    def scrape_group(self, grupo, html_content):
        """Chama o método correspondente para cada grupo."""
        scraper_methods = {
            'ransomhouse': self.grupos.ransomhouse,
            'monti': self.grupos.monti,
            'play': self.grupos.play,
            'handala': self.grupos.handala,
            'blackbyte': self.grupos.blackbyte,
        }

        if grupo in scraper_methods:
            return scraper_methods[grupo](html_content)
        else:
            logging.warning(
                f"Grupo '{grupo}' ainda não possui um scraper específico.")
            return []

    def send_email(self):
        """Envia um e-mail com os arquivos PDF e JSON."""
        sleep(10)  # Atraso opcional, se necessário
        pdf_file_path = os.path.join(os.getcwd(), 'ransomscraper.pdf')
        json_file_path = os.path.join(os.getcwd(), 'groups.json')

        email_sender = SendEmail()
        email_sender.send_email(pdf_file_path, json_file_path)


if __name__ == "__main__":
    main_app = Main()
    main_app.run()
