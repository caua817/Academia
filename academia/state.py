import reflex as rx
from academia.services.xano_client import check_xano_connection, API_BASE_URL

class ConnectionState(rx.State):
    is_checking: bool = False
    is_connected: bool = False
    status_message: str = "Aguardando verificação de conexão..."
    api_url: str = API_BASE_URL
    details: dict = {}

    async def verify_connection(self):
        self.is_checking = True
        self.status_message = "Conectando ao Xano..."
        yield

        success, message, details = await check_xano_connection()
        
        self.is_connected = success
        self.status_message = message
        self.details = details
        self.is_checking = False