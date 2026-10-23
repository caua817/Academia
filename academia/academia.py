import reflex as rx
from academia.login import login_page
from academia.services.xano_client import XanoClient


class DashboardState(rx.State):
    alunos: list[dict] = []
    is_loading: bool = False

    def load_alunos(self):
        """Carrega a lista de alunos do Xano ao abrir a página."""
        self.is_loading = True
        yield
        token = self.get_value("auth_token")
        self.alunos = XanoClient.get_alunos(token)
        self.is_loading = False


def aluno_row(aluno: dict) -> rx.Component:
    """Renderiza cada linha de aluno na tabela."""
    return rx.table.row(
        rx.table.cell(aluno.get("nome", "Sem Nome")),
        rx.table.cell(aluno.get("email", "-")),
        rx.table.cell(aluno.get("plano", "Padrão")),
        rx.table.cell(
            rx.badge(
                aluno.get("status", "Ativo"),
                color_scheme=rx.cond(
                    aluno.get("status") == "Ativo",
                    "green",
                    "red",
                ),
            )
        ),
    )


def dashboard_page() -> rx.Component:
    return rx.box(
        rx.hstack(
            # Sidebar / Menu Lateral
            rx.vstack(
                rx.vstack(
                    rx.heading("ACADEMIA", size="6", weight="bold", color="white"),
                    rx.text("Painel de Gestão", size="2", color="var(--gray-9)"),
                    align="start",
                    spacing="1",
                ),
                rx.divider(color_scheme="gray"),
                rx.vstack(
                    rx.button(
                        rx.icon("layout-dashboard", size=18),
                        "Dashboard",
                        variant="soft",
                        color_scheme="blue",
                        width="100%",
                        justify="start",
                    ),
                    rx.button(
                        rx.icon("users", size=18),
                        "Alunos",
                        variant="ghost",
                        color_scheme="gray",
                        width="100%",
                        justify="start",
                    ),
                    rx.button(
                        rx.icon("credit-card", size=18),
                        "Planos",
                        variant="ghost",
                        color_scheme="gray",
                        width="100%",
                        justify="start",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("log-out", size=18),
                    "Sair",
                    variant="surface",
                    color_scheme="red",
                    width="100%",
                    on_click=rx.redirect("/login"),
                ),
                width="250px",
                height="100vh",
                padding="6",
                background="#121215",
                border_right="1px solid rgba(255, 255, 255, 0.08)",
            ),
            # Conteúdo Principal
            rx.box(
                rx.vstack(
                    # Cabeçalho Superior
                    rx.hstack(
                        rx.heading("Visão Geral & Alunos", size="7", weight="bold", color="white"),
                        rx.spacer(),
                        rx.button(
                            rx.icon("refresh-cw", size=16),
                            "Atualizar",
                            on_click=DashboardState.load_alunos,
                            loading=DashboardState.is_loading,
                            variant="surface",
                        ),
                        width="100%",
                        align="center",
                        margin_bottom="6",
                    ),
                    # Tabela de Alunos vindos do Xano
                    rx.card(
                        rx.vstack(
                            rx.heading("Lista de Alunos Cadastrados", size="4", weight="bold", color="white"),
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Nome"),
                                        rx.table.column_header_cell("E-mail"),
                                        rx.table.column_header_cell("Plano"),
                                        rx.table.column_header_cell("Status"),
                                    ),
                                ),
                                rx.table.body(
                                    rx.foreach(DashboardState.alunos, aluno_row)
                                ),
                                width="100%",
                            ),
                            width="100%",
                            spacing="4",
                        ),
                        variant="surface",
                        width="100%",
                        padding="6",
                    ),
                    width="100%",
                    max_width="1200px",
                ),
                padding="8",
                width="100%",
                background="#0A0A0C",
                min_height="100vh",
            ),
            width="100%",
            spacing="0",
        ),
        width="100%",
        min_height="100vh",
        on_mount=DashboardState.load_alunos,
    )


app = rx.App(theme=rx.theme(appearance="dark"))
app.add_page(dashboard_page, route="/")
app.add_page(login_page, route="/login")