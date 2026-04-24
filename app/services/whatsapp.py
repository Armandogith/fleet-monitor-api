import httpx
from app.core.config import settings

class WhatsAppService:
    async def send_alert(self, phone: str, driver_name: str, doc_type: str, days_remaining: int):
        # Remove símbolos do telefone (+, -, espaços)
        clean_phone = "".join(filter(str.isdigit, phone))
        
        # Se for ambiente de teste/mock, não bate na API real ainda
        if settings.WHATSAPP_API_TOKEN == "mock-token":
            print(f"[MOCK] 📱 Mensagem para {clean_phone}: {driver_name}, {doc_type} vence em {days_remaining} dias.")
            return {"status": "success", "id": "mock_id"}

        # API REAL DA META
        url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Payload exigido pela Meta para Templates Utility
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": "document_expiration_alert", # NOME EXATO DO TEMPLATE CRIADO NA META
                "language": {"code": "pt_BR"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": driver_name},
                            {"type": "text", "text": doc_type},
                            {"type": "text", "text": str(days_remaining)}
                        ]
                    }
                ]
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

whatsapp_service = WhatsAppService()