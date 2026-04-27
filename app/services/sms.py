import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

SMSDEV_URL = "https://api.smsdev.com.br/v1/send"

def format_phone(phone: str) -> str:
    # Remove tudo que não é número
    digits = ''.join(filter(str.isdigit, phone))
    # Adiciona DDI 55 se não tiver
    if not digits.startswith('55'):
        digits = '55' + digits
    return digits

class SMSService:
    async def send_alert(self, phone, driver_name, doc_type, days_remaining):
        formatted_phone = format_phone(phone)
        message = (
            f"Fleet Monitor: Ola {driver_name}, "
            f"seu(sua) {doc_type} vence em {days_remaining} dia(s). "
            f"Providencie a renovacao."
        )
        payload = {
            "key": settings.SMSDEV_API_KEY,
            "type": 9,
            "number": formatted_phone,
            "msg": message,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(SMSDEV_URL, json=payload)
        data = response.json()
        if response.status_code not in (200, 201) or data.get("situacao") != "OK":
            raise Exception(f"Erro SMS para {formatted_phone}: [{response.status_code}] {data}")
        logger.info(f"SMS enviado para {formatted_phone} | ID: {data.get('id')}")
        return data

sms_service = SMSService()