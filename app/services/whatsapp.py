import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

SMSDEV_URL = "https://api.smsdev.com.br/v1/send"

class SMSService:
    """
    Integração com a API da SMSDev para envio de alertas via SMS.
    Documentação: https://www.smsdev.com.br/
    """

    async def send_alert(
        self,
        phone: str,
        driver_name: str,
        doc_type: str,
        days_remaining: int
    ) -> dict:
        """
        Envia alerta de vencimento de documento via SMS.

        Args:
            phone: Número no formato nacional sem '+' e sem '-' (ex: 11999999999)
            driver_name: Nome do motorista
            doc_type: Tipo do documento (CNH, CRLV, etc)
            days_remaining: Dias restantes para o vencimento
        """
        message = (
            f"⚠️ Fleet Monitor: Olá {driver_name}, "
            f"seu(sua) {doc_type} vence em {days_remaining} dia(s). "
            f"Providencie a renovação o quanto antes."
        )

        payload = {
            "key": settings.SMSDEV_API_KEY,
            "type": 9,           # tipo 9 = SMS padrão
            "number": phone,
            "msg": message,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(SMSDEV_URL, json=payload)

        data = response.json()

        # SMSDev retorna situacao "OK" em caso de sucesso
        if response.status_code not in (200, 201) or data.get("situacao") != "OK":
            raise Exception(
                f"Erro ao enviar SMS para {phone}: "
                f"[{response.status_code}] {data}"
            )

        logger.info(f"SMS enviado para {phone} | ID: {data.get('id')}")
        return data

# Instância global usada em nodes.py
sms_service = SMSService()