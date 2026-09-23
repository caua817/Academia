import os
import httpx
from typing import Dict, Any, Tuple

API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")

async def check_xano_connection() -> Tuple[bool, str, Dict[str, Any]]:
    if not API_BASE_URL:
        return False, "Erro: API_BASE_URL não configurada no arquivo .env", {}

    url = f"{API_BASE_URL}/auth/me"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            
            if response.status_code in (200, 401, 403):
                return True, f"Conexão estabelecida com sucesso com o Xano! (HTTP {response.status_code})", {
                    "status_code": response.status_code,
                    "url": url
                }
            else:
                return False, f"Resposta inesperada do Xano: HTTP {response.status_code}", {
                    "status_code": response.status_code
                }
    except httpx.ConnectError:
        return False, "Falha ao conectar no backend Xano. Verifique se o servidor está online ou se a URL está correta.", {}
    except httpx.TimeoutException:
        return False, "Tempo limite esgotado (timeout) ao tentar conectar ao Xano.", {}
    except Exception as e:
        return False, f"Erro inesperado de conexão: {str(e)}", {}