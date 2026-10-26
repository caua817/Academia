import reflex as rx

from academia.alunos import AlunosState, student_management_content
from academia.login import LoginState, login_page
from academia.matriculas import MatriculasState, matriculas_page
from academia.planos import PlanosState, planos_page
from academia.session_state import clear_app_session
from academia.services.xano_client import XanoAPIError, XanoClient


class DashboardState(rx.State):
    alunos: list[dict] = []
    is_loading: bool = False
    error_message: str = ""
    search_query: str = ""

    @rx.var
    def filtered_alunos(self) -> list[dict]:
        query = self.search_query.strip().casefold()
        if not query:
            return self.alunos

        return [
            aluno
            for aluno in self.alunos
            if query
            in " ".join(
                str(aluno.get(field) or "")
                for field in ("nome", "contato", "email")
            ).casefold()
        ]

    @rx.var
    def active_count(self) -> int:
        return sum(
            1
            for aluno in self.alunos
            if str(aluno.get("situacao", aluno.get("status", "Ativo"))).casefold()
            == "ativo"
        )

    @rx.var
    def inactive_count(self) -> int:
        return len(self.alunos) - self.active_count

    @rx.var
    def has_alunos(self) -> bool:
        return bool(self.filtered_alunos)

    async def load_alunos(self):
        self.is_loading = True
        self.error_message = ""
        yield

        login_state = await self.get_state(LoginState)
        if not login_state.auth_token:
            await clear_app_session(self)
            self.is_loading = False
            yield rx.redirect("/login")
            return

        try:
            self.alunos = XanoClient.get_alunos(login_state.auth_token)
        except XanoAPIError as error:
            self.alunos = []
            if error.status_code == 401:
                await clear_app_session(self)
                yield rx.redirect("/login")
            elif error.status_code == 403:
                self.error_message = "Você não tem permissão para acessar os alunos."
            else:
                self.error_message = (
                    "Não foi possível carregar os alunos. Verifique a conexão "
                    "e tente novamente."
                )
        finally:
            self.is_loading = False

    @rx.event
    def clear_data(self):
        self.alunos = []
        self.search_query = ""
        self.error_message = ""

    @rx.event
    async def logout(self):
        await clear_app_session(self)
        yield rx.redirect("/login")

    def set_search_query(self, value: str):
        self.search_query = value


def aluno_row(aluno: dict) -> rx.Component:
    status = aluno.get("situacao", aluno.get("status", "Ativo"))
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.box(
                    rx.icon("user-round", size=17, color="#93c5fd"),
                    background="#1e3a5f",
                    padding="2",
                    border_radius="full",
                ),
                rx.vstack(
                    rx.text(aluno.get("nome", "Nome não informado"), weight="medium"),
                    rx.text(
                        aluno.get("contato", aluno.get("email", "Sem contato")),
                        size="1",
                        color="var(--gray-9)",
                    ),
                    spacing="1",
                    align="start",
                ),
                spacing="3",
                align="center",
            )
        ),
        rx.table.cell(
            rx.badge(
                status,
                color_scheme=rx.cond(
                    (status == "Ativo") | (status == "ativo"),
                    "green",
                    "gray",
                ),
                variant="soft",
            )
        ),
    )


def nav_link(label: str, icon: str, href: str, active: bool = False) -> rx.Component:
    return rx.link(
        rx.button(
            rx.icon(icon, size=18),
            label,
            variant="soft" if active else "ghost",
            color_scheme="blue" if active else "gray",
            width="100%",
            justify="start",
            size="3",
        ),
        href=href,
        width="100%",
        underline="none",
    )


def sidebar(active_page: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.box(
                rx.icon("dumbbell", size=22, color="white"),
                background="#2563eb",
                padding="2",
                border_radius="12px",
            ),
            rx.vstack(
                rx.heading("ACADEMIA", size="3", weight="bold", color="white"),
                rx.text("GESTÃO FITNESS", size="1", color="var(--gray-9)"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        rx.text(
            "MENU PRINCIPAL",
            size="1",
            weight="bold",
            color="var(--gray-9)",
            width="100%",
            margin_top="8",
        ),
        rx.vstack(
            nav_link("Visão geral", "layout-dashboard", "/", active_page == "dashboard"),
            nav_link("Alunos", "users-round", "/alunos", active_page == "alunos"),
            nav_link("Planos", "credit-card", "/planos", active_page == "planos"),
            nav_link(
                "Matrículas",
                "clipboard-list",
                "/matriculas",
                active_page == "matriculas",
            ),
            spacing="2",
            width="100%",
        ),
        rx.spacer(),
        rx.callout(
            "Área administrativa",
            icon="shield-check",
            color_scheme="blue",
            size="1",
            width="100%",
        ),
        rx.button(
            rx.icon("log-out", size=18),
            "Sair",
            variant="ghost",
            color_scheme="gray",
            width="100%",
            justify="start",
            on_click=DashboardState.logout,
        ),
        width=["100%", "260px"],
        min_width=["100%", "260px"],
        height=["auto", "100vh"],
        padding="6",
        background="#111318",
        border_right=["none", "1px solid rgba(255, 255, 255, 0.08)"],
        border_bottom=["1px solid rgba(255, 255, 255, 0.08)", "none"],
        align="start",
    )


def metric_card(
    label: str,
    value: rx.Var,
    icon: str,
    color: str,
    description: str,
) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(label, size="2", color="var(--gray-9)"),
                rx.heading(value, size="7", weight="bold", color="white"),
                rx.text(description, size="1", color="var(--gray-9)"),
                spacing="2",
                align="start",
            ),
            rx.spacer(),
            rx.box(
                rx.icon(icon, size=21, color=color),
                background=f"{color}22",
                padding="3",
                border_radius="12px",
                align_self="start",
            ),
            width="100%",
            align="start",
        ),
        background="#15171d",
        border="1px solid rgba(255, 255, 255, 0.08)",
        width="100%",
        padding="5",
    )


def aluno_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ALUNO"),
                rx.table.column_header_cell("SITUAÇÃO"),
            )
        ),
        rx.table.body(rx.foreach(DashboardState.filtered_alunos, aluno_row)),
        width="100%",
        variant="surface",
    )


def alunos_content(show_search: bool = False) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        "Alunos cadastrados",
                        size="4",
                        weight="bold",
                        color="white",
                    ),
                    rx.text(
                        "Acompanhe a situação e os dados de contato dos alunos.",
                        size="2",
                        color="var(--gray-9)",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.cond(
                    show_search,
                    rx.input(
                        rx.input.slot(rx.icon("search", size=16)),
                        placeholder="Buscar por nome ou contato",
                        value=DashboardState.search_query,
                        on_change=DashboardState.set_search_query,
                        width=["100%", "320px"],
                        size="3",
                    ),
                    rx.link(
                        rx.button(
                            "Ver todos",
                            rx.icon("arrow-right", size=16),
                            variant="soft",
                            color_scheme="blue",
                        ),
                        href="/alunos",
                    ),
                ),
                width="100%",
                align="center",
                flex_wrap="wrap",
                spacing="4",
            ),
            rx.cond(
                DashboardState.error_message != "",
                rx.callout(
                    DashboardState.error_message,
                    icon="triangle-alert",
                    color_scheme="red",
                    width="100%",
                ),
                rx.cond(
                    DashboardState.is_loading,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Carregando alunos...", color="var(--gray-9)"),
                            spacing="3",
                            align="center",
                        ),
                        min_height="220px",
                        width="100%",
                    ),
                    rx.cond(
                        DashboardState.has_alunos,
                        rx.box(
                            aluno_table(),
                            overflow_x="auto",
                            width="100%",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.box(
                                    rx.icon(
                                        "users-round",
                                        size=24,
                                        color="var(--gray-9)",
                                    ),
                                    background="#20232b",
                                    padding="4",
                                    border_radius="full",
                                ),
                                rx.heading(
                                    "Nenhum aluno encontrado",
                                    size="4",
                                    color="white",
                                ),
                                rx.text(
                                    rx.cond(
                                        DashboardState.search_query != "",
                                        "Tente ajustar sua busca.",
                                        "Os alunos cadastrados aparecerão aqui.",
                                    ),
                                    size="2",
                                    color="var(--gray-9)",
                                ),
                                spacing="3",
                                align="center",
                                text_align="center",
                            ),
                            min_height="240px",
                            width="100%",
                        ),
                    ),
                ),
            ),
            rx.cond(
                DashboardState.error_message != "",
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        rx.icon("refresh-cw", size=16),
                        "Tentar novamente",
                        on_click=DashboardState.load_alunos,
                        loading=DashboardState.is_loading,
                        variant="soft",
                    ),
                    width="100%",
                ),
            ),
            width="100%",
            spacing="5",
            align="stretch",
        ),
        background="#15171d",
        border="1px solid rgba(255, 255, 255, 0.08)",
        width="100%",
        padding="5",
    )


def dashboard_page() -> rx.Component:
    return app_shell(
        "dashboard",
        "Visão geral",
        "Acompanhe o movimento da sua academia em um só lugar.",
        rx.vstack(
            rx.grid(
                metric_card(
                    "Total de alunos",
                    DashboardState.alunos.length(),
                    "users-round",
                    "#60a5fa",
                    "Cadastros encontrados",
                ),
                metric_card(
                    "Alunos ativos",
                    DashboardState.active_count,
                    "user-round-check",
                    "#4ade80",
                    "Com situação ativa",
                ),
                metric_card(
                    "Inativos",
                    DashboardState.inactive_count,
                    "user-round-x",
                    "#fbbf24",
                    "Cadastros desativados",
                ),
                columns="repeat(auto-fit, minmax(220px, 1fr))",
                spacing="4",
                width="100%",
            ),
            alunos_content(),
            width="100%",
            spacing="5",
            align="stretch",
        ),
    )


def alunos_page() -> rx.Component:
    return app_shell(
        "alunos",
        "Gestão de alunos",
        "Cadastre, consulte e mantenha os registros da academia.",
        student_management_content(),
    )


def app_shell(
    active_page: str,
    title: str,
    subtitle: str,
    content: rx.Component,
) -> rx.Component:
    load_event = {
        "dashboard": DashboardState.load_alunos,
        "alunos": AlunosState.load_alunos,
        "planos": PlanosState.load_planos,
        "matriculas": MatriculasState.load_matriculas,
    }[active_page]
    is_loading = {
        "dashboard": DashboardState.is_loading,
        "alunos": AlunosState.is_loading,
        "planos": PlanosState.is_loading,
        "matriculas": MatriculasState.is_loading,
    }[active_page]
    return rx.flex(
        sidebar(active_page),
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "PAINEL ADMINISTRATIVO",
                        size="1",
                        weight="bold",
                        color="var(--gray-9)",
                        letter_spacing="0.08em",
                    ),
                    rx.heading(title, size="7", weight="bold", color="white"),
                    rx.text(subtitle, size="2", color="var(--gray-9)"),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Atualizar",
                    on_click=load_event,
                    loading=is_loading,
                    variant="surface",
                    color_scheme="gray",
                    size="3",
                ),
                width="100%",
                align="center",
                flex_wrap="wrap",
                spacing="4",
                margin_bottom="6",
            ),
            content,
            width="100%",
            max_width="1440px",
            padding=["5", "8"],
            align="stretch",
        ),
        width="100%",
        min_height="100vh",
        flex_direction=["column", "row"],
        align="stretch",
        background="#0b0d11",
        on_mount=load_event,
    )


app = rx.App(theme=rx.theme(appearance="dark"))
app.add_page(dashboard_page, route="/")
app.add_page(alunos_page, route="/alunos")
app.add_page(planos_page, route="/planos")
app.add_page(matriculas_page, route="/matriculas")
app.add_page(login_page, route="/login")
