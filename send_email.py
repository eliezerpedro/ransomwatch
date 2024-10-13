import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

class SendEmail:
    def __init__(self):
        # Carregar variáveis de ambiente do arquivo .env
        load_dotenv()
        self.username = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASS')
        self.sender_email = os.getenv('EMAIL_SENDER')
        self.recipient_email = os.getenv('EMAIL_RECIPIENT')
    
    def send_email(self, subject, body, pdf_file, json_file):
        # Criar a mensagem do e-mail
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = subject
        
        # Adicionar o corpo do e-mail
        msg.attach(MIMEText(body, 'plain'))

        # Adicionar o arquivo PDF
        with open(pdf_file, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_file)}')
            msg.attach(pdf_attachment)

        # Adicionar o arquivo JSON
        with open(json_file, 'rb') as f:
            json_attachment = MIMEApplication(f.read(), _subtype='json')
            json_attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(json_file)}')
            msg.attach(json_attachment)

        # Configurar conexão segura com o Gmail
        context = ssl.create_default_context()
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls(context=context)  # Conexão segura
            server.login(self.username, self.password)  # Login
            server.send_message(msg)  # Enviar e-mail

        print("Email enviado com sucesso!")
