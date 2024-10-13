import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)


class SendEmail:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASS')
        self.sender_email = os.getenv('EMAIL_SENDER')
        self.recipient_email = os.getenv('EMAIL_RECIPIENT')

    def send_email(self, pdf_file, json_file):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = "Relatório e Dados Anexados"

        body = "Segue em anexo o relatório em PDF e os dados em JSON."
        msg.attach(MIMEText(body, 'plain'))

        with open(pdf_file, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
            pdf_attachment.add_header(
                'Content-Disposition', f'attachment; filename={os.path.basename(pdf_file)}')
            msg.attach(pdf_attachment)

        with open(json_file, 'rb') as f:
            json_attachment = MIMEApplication(f.read(), _subtype='json')
            json_attachment.add_header(
                'Content-Disposition', f'attachment; filename={os.path.basename(json_file)}')
            msg.attach(json_attachment)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)

            logging.info("Email enviado com sucesso!")
        except Exception as e:
            logging.error(f"Erro ao enviar email: {e}")
