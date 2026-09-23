import reflex as rx
from academia.state import ConnectionState

def connection_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Diagnóstico de Conexão: Reflex ↔ Xano", size="5"),
            rx.divider(),
            
            rx.hstack(
                rx.text("URL Base do Xano: ", weight="bold"),
                rx.code(
                    rx.cond(
                        ConnectionState.api_url != "",
                        ConnectionState.api_url,
                        "Não configurada"
                    )
                ),
                align="center",
            ),
            
            rx.hstack(
                rx.text("Status da Conexão: ", weight="bold"),
                rx.cond(
                    ConnectionState.is_checking,
                    rx.badge("Verificando...", color_scheme="yellow"),
                    rx.cond(
                        ConnectionState.is_connected,
                        rx.badge("Conectado", color_scheme="green"),
                        rx.badge("Desconectado / Erro", color_scheme="red"),
                    ),
                ),
                align="center",
            ),
            
            rx.callout(
                ConnectionState.status_message,
                icon="info",
                color_scheme=rx.cond(ConnectionState.is_connected, "green", "red"),
                role="status",
                width="100%",
            ),

            rx.button(
                "Testar Conexão Novamente",
                on_click=ConnectionState.verify_connection,
                loading=ConnectionState.is_checking,
                color_scheme="blue",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        max_width="600px",
    )

def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Sistema de Gestão de Academia", size="8"),
            rx.text("Fundação técnica - Verificação de integração com o backend", color_scheme="gray"),
            connection_card(),
            spacing="6",
            align="center",
            justify="center",
            min_height="80vh",
        ),
        on_mount=ConnectionState.verify_connection,
    )

app = rx.App()
app.add_page(index, title="Academia - Conexão Xano")