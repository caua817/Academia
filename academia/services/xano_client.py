import os
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:sGd5fzIy")

class XanoClient:
    @staticmethod
    def get_alunos(token: str = None) -> list:
        """Procura a lista de alunos na API do Xano."""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{API_BASE_URL}/alunos", headers=headers)
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception:
            return []