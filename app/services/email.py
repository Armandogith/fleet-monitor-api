import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_USER

    async def send_alert(self, to_email: str, driver_name: str, doc_type: str, days_remaining: int):
        if not to_email or not self.smtp_user:
            return

        subject = f"⚠️ Alerta: {doc_type} de {driver_name} vence em {days_remaining} dias"
        body = f"""
        <html><body>
        <h2>⚠️ Alerta de Vencimento de Documento</h2>
        <p>Prezado responsável,</p>
        <p>O documento <strong>{doc_type}</strong> do motorista <strong>{driver_name}</strong>
        vencerá em <strong>{days_remaining} dias</strong>.</p>
        <p>Por favor, providencie a renovação com urgência.</p>
        <hr>
        <small>Sistema de Monitoramento de Frota</small>
        </body></html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, to_email, msg.as_string())

email_service = EmailService()