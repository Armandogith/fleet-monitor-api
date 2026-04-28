tee /root/app/app/services/email.py > /dev/null << 'EOF'
import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

class EmailService:
    async def send_alert(self, to_email: str, driver_name: str, doc_type: str, days_remaining: int):
        if not to_email or not resend.api_key:
            return
        try:
            resend.Emails.send({
                "from": "AlertaFrota <onboarding@resend.dev>",
                "to": to_email,
                "subject": f"⚠️ Alerta: {doc_type} de {driver_name} vence em {days_remaining} dias",
                "html": f"""
                <h2>⚠️ Alerta de Vencimento</h2>
                <p>O documento <strong>{doc_type}</strong> do motorista <strong>{driver_name}</strong>
                vencerá em <strong>{days_remaining} dias</strong>.</p>
                <p>Providencie a renovação com urgência.</p>
                <hr><small>AlertaFrota</small>
                """
            })
            print(f"✅ Email enviado para {to_email}")
        except Exception as e:
            print(f"❌ Erro email: {e}")

email_service = EmailService()
EOF