import httpx
from app.core.config import settings


class WhatsAppService:
    """
    Integração com a WhatsApp Business Cloud API da Meta.
    Utiliza o template 'hello_world' para testes gratuitos (5 números).
    Para produção, crie templates personalizados no WhatsApp Manager.
    """

    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.token = settings.WHATSAPP_API_TOKEN

    async def send_alert(
        self,
        phone: str,
        driver_name: str,
        doc_type: str,
        days_remaining: int
    ) -> dict:
        """
        Envia alerta de vencimento de documento via WhatsApp.

        Para os 5 números de teste gratuitos usa o template 'hello_world'.
        Para produção, substituir pelo template personalizado abaixo (comentado).

        Args:
            phone: Número no formato internacional sem '+' (ex: 5511999999999)
            driver_name: Nome do motorista
            doc_type: Tipo do documento (CNH, CRLV, etc)
            days_remaining: Dias restantes para o vencimento
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        # ---------------------------------------------------------------
        # MODO TESTE: usa template 'hello_world' (funciona nos 5 números
        # de teste sem custo e sem aprovação de template)
        # ---------------------------------------------------------------
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {"code": "en_US"}
            }
        }

        # ---------------------------------------------------------------
        # MODO PRODUÇÃO: descomente abaixo e comente o bloco acima.
        # Requer template aprovado no WhatsApp Manager com variáveis:
        # {{1}} = nome do motorista
        # {{2}} = tipo do documento
        # {{3}} = dias restantes
        # ---------------------------------------------------------------
        # payload = {
        #     "messaging_product": "whatsapp",
        #     "to": phone,
        #     "type": "template",
        #     "template": {
        #         "name": "alerta_vencimento_cnh",
        #         "language": {"code": "pt_BR"},
        #         "components": [
        #             {
        #                 "type": "body",
        #                 "parameters": [
        #                     {"type": "text", "text": driver_name},
        #                     {"type": "text", "text": doc_type},
        #                     {"type": "text", "text": str(days_remaining)},
        #                 ]
        #             }
        #         ]
        #     }
        # }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code not in (200, 201):
            raise Exception(
                f"Erro ao enviar WhatsApp para {phone}: "
                f"[{response.status_code}] {response.text}"
            )

        return response.json()


# Instância global usada em nodes.py
whatsapp_service = WhatsAppService()