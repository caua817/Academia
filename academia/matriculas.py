from datetime import date, datetime

import reflex as rx

from academia.login import LoginState
from academia.planos import format_currency
from academia.services.xano_client import XanoAPIError, XanoClient


def validate_matricula_fields(
    aluno_id: str,
    plano_id: str,
    data_inicio: str,
    today: date | None = None,
) -> str | None:
    try:
        parsed_aluno_id = int(aluno_id)
        parsed_plano_id = int(plano_id)
    except ValueError:
        return "Selecione um aluno e um plano."
    if parsed_aluno_id <= 0 or parsed_plano_id <= 0:
        return "Selecione um aluno e um plano."

    try:
        start_date = date.fromisoformat(data_inicio)
    except ValueError:
        return "Informe uma data de início válida."

    current_date = today or datetime.now().date()
    if start_date > current_date:
        return "A data de início não pode ser futura."
    return None


class MatriculasState(rx.State):
    matriculas: list[dict] = []
    alunos_ativos: list[dict[str, str]] = []
    planos_ativos: list[dict[str, str]] = []
    is_loading: bool = False
    is_saving: bool = False
    is_loading_details: bool = False
    is_detail_open: bool = False
    error_message: str = ""
    success_message: str = ""
    form_error: str = ""
    selected_aluno_id: str = ""
    selected_plano_id: str = ""
    data_inicio: str = ""
    matricula_details: dict = {}

    @rx.var
    def has_matriculas(self) -> bool:
        return bool(self.matriculas)

    def _api_error_message(self, error: XanoAPIError, action: str) -> str:
        if error.status_code == 401:
            return "Sua sessão expirou. Faça login novamente."
        if error.status_code == 403:
            return "Você não tem permissão para acessar a gestão de matrículas."
        if error.status_code in (400, 409):
            return str(error)
        if error.status_code is not None:
            return (
                f"Não foi possível {action}. "
                f"A API respondeu com HTTP {error.status_code}."
            )
        return f"Não foi possível {action}. Verifique a conexão e tente novamente."

    def _clear_sensitive_data(self):
        self.matriculas = []
        self.alunos_ativos = []
        self.planos_ativos = []
        self.is_loading = False
        self.is_saving = False
        self.is_loading_details = False
        self.error_message = ""
        self.success_message = ""
        self.form_error = ""
        self.selected_aluno_id = ""
        self.selected_plano_id = ""
        self.data_inicio = ""
        self.matricula_details = {}
        self.is_detail_open = False

    @rx.event
    def clear_data(self):
        self._clear_sensitive_data()

    def _reload_matriculas(self, token: str, action: str) -> bool:
        try:
            alunos = XanoClient.get_alunos(token)
            planos = XanoClient.get_planos(token)
            matriculas = XanoClient.get_matriculas(token)
        except XanoAPIError as error:
            self.matriculas = []
            self.alunos_ativos = []
            self.planos_ativos = []
            self.error_message = self._api_error_message(error, action)
            return error.status_code == 401

        self.alunos_ativos = [
            {
                "id": str(aluno.get("id", "")),
                "nome": str(aluno.get("nome") or "Aluno sem nome"),
            }
            for aluno in alunos
            if str(aluno.get("situacao", "")).casefold() == "ativo"
        ]
        self.planos_ativos = [
            {
                "id": str(plano.get("id", "")),
                "label": (
                    f"{plano.get('nome', 'Plano sem nome')} · "
                    f"{plano.get('duracao_meses', 0)} meses · "
                    f"{format_currency(plano.get('valor'))}"
                ),
            }
            for plano in planos
            if plano.get("situacao") == "Ativo"
        ]
        self.matriculas = [
            {
                **matricula,
                "valor_formatado": format_currency(
                    matricula.get("valor_contratado")
                ),
            }
            for matricula in matriculas
        ]
        self.error_message = ""
        return False

    @rx.event
    async def load_matriculas(self):
        self.is_loading = True
        self.error_message = ""
        yield

        login_state = await self.get_state(LoginState)
        if not login_state.auth_token:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            self.is_loading = False
            yield rx.redirect("/login")
            return

        expired = self._reload_matriculas(
            login_state.auth_token,
            "carregar as matrículas",
        )
        self.is_loading = False
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")

    @rx.event
    def set_selected_aluno_id(self, value: str):
        self.selected_aluno_id = value

    @rx.event
    def set_selected_plano_id(self, value: str):
        self.selected_plano_id = value

    @rx.event
    def set_data_inicio(self, value: str):
        self.data_inicio = value

    @rx.event
    async def create_matricula(self):
        validation_error = validate_matricula_fields(
            self.selected_aluno_id,
            self.selected_plano_id,
            self.data_inicio,
        )
        if validation_error:
            self.form_error = validation_error
            return

        self.form_error = ""
        self.is_saving = True
        yield

        login_state = await self.get_state(LoginState)
        if not login_state.auth_token:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            self.is_saving = False
            yield rx.redirect("/login")
            return

        payload = {
            "aluno_id": int(self.selected_aluno_id),
            "plano_id": int(self.selected_plano_id),
            "data_inicio": self.data_inicio,
        }

        try:
            XanoClient.create_matricula(login_state.auth_token, payload)
        except XanoAPIError as error:
            self.form_error = self._api_error_message(
                error,
                "criar a matrícula",
            )
            self.is_saving = False
            if error.status_code == 401:
                from academia.session_state import clear_app_session

                await clear_app_session(self)
                yield rx.redirect("/login")
            return

        self.is_saving = False
        self.selected_aluno_id = ""
        self.selected_plano_id = ""
        self.data_inicio = ""
        self.success_message = "Matrícula criada com sucesso."
        expired = self._reload_matriculas(
            login_state.auth_token,
            "atualizar a lista de matrículas",
        )
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")

    @rx.event
    def set_is_detail_open(self, is_open: bool):
        self.is_detail_open = is_open
        if not is_open:
            self.matricula_details = {}

    @rx.event
    async def view_matricula(self, matricula_id: int):
        self.error_message = ""
        self.is_loading_details = True
        yield

        login_state = await self.get_state(LoginState)
        if not login_state.auth_token:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            self.is_loading_details = False
            yield rx.redirect("/login")
            return

        try:
            matricula = XanoClient.get_matricula(
                login_state.auth_token,
                matricula_id,
            )
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "carregar os dados da matrícula",
            )
            if error.status_code == 401:
                from academia.session_state import clear_app_session

                await clear_app_session(self)
                yield rx.redirect("/login")
        else:
            matricula["valor_formatado"] = format_currency(
                matricula.get("valor_contratado")
            )
            self.matricula_details = matricula
            self.is_detail_open = True
        finally:
            self.is_loading_details = False


def aluno_option(aluno: dict) -> rx.Component:
    return rx.select.item(
        aluno.get("nome", "Aluno sem nome"),
        value=aluno.get("id", ""),
    )


def plano_option(plano: dict) -> rx.Component:
    return rx.select.item(
        plano.get("label", "Plano"),
        value=plano.get("id", ""),
    )


def enrollment_row(matricula: dict) -> rx.Component:
    status = matricula.get("situacao", "Encerrada")
    return rx.table.row(
        rx.table.cell(
            rx.vstack(
                rx.text(matricula.get("aluno_nome", "Aluno"), weight="medium"),
                rx.text(
                    matricula.get("plano_nome", "Plano"),
                    size="1",
                    color="var(--gray-9)",
                ),
                spacing="1",
                align="start",
            )
        ),
        rx.table.cell(matricula.get("data_inicio", "")),
        rx.table.cell(matricula.get("data_termino", "")),
        rx.table.cell(
            matricula.get("duracao_contratada_meses", 0),
            " meses",
        ),
        rx.table.cell(matricula.get("valor_formatado", "Valor indisponível")),
        rx.table.cell(
            rx.badge(
                status,
                color_scheme=rx.cond(status == "Ativa", "green", "gray"),
                variant="soft",
            )
        ),
        rx.table.cell(
            rx.button(
                rx.icon("eye", size=15),
                "Detalhes",
                variant="soft",
                on_click=MatriculasState.view_matricula(
                    matricula.get("id", 0)
                ),
                disabled=MatriculasState.is_loading_details,
            )
        ),
    )


def enrollment_detail_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Detalhes da matrícula", color="white"),
            rx.dialog.description(
                "Condições preservadas no momento da contratação.",
                color="var(--gray-9)",
            ),
            rx.grid(
                rx.vstack(
                    rx.text("Aluno", size="1", color="var(--gray-9)"),
                    rx.text(
                        MatriculasState.matricula_details.get("aluno_nome", ""),
                        weight="medium",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Plano", size="1", color="var(--gray-9)"),
                    rx.text(
                        MatriculasState.matricula_details.get("plano_nome", ""),
                        weight="medium",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Início", size="1", color="var(--gray-9)"),
                    rx.text(
                        MatriculasState.matricula_details.get("data_inicio", "")
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Término", size="1", color="var(--gray-9)"),
                    rx.text(
                        MatriculasState.matricula_details.get("data_termino", "")
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Duração contratada", size="1", color="var(--gray-9)"),
                    rx.text(
                        MatriculasState.matricula_details.get(
                            "duracao_contratada_meses",
                            0,
                        ),
                        " meses",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Valor contratado", size="1", color="var(--gray-9)"),
                    rx.text(
                        MatriculasState.matricula_details.get(
                            "valor_formatado",
                            "",
                        )
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Situação", size="1", color="var(--gray-9)"),
                    rx.badge(
                        MatriculasState.matricula_details.get(
                            "situacao",
                            "Encerrada",
                        ),
                        color_scheme=rx.cond(
                            MatriculasState.matricula_details.get("situacao")
                            == "Ativa",
                            "green",
                            "gray",
                        ),
                        variant="soft",
                    ),
                    align="start",
                    spacing="1",
                ),
                columns="repeat(auto-fit, minmax(160px, 1fr))",
                spacing="4",
                width="100%",
                margin_top="4",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Fechar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=MatriculasState.set_is_detail_open(False),
                    )
                ),
                justify="end",
                width="100%",
                margin_top="5",
            ),
            background="#121215",
            border="1px solid rgba(255, 255, 255, 0.15)",
            border_radius="16px",
            max_width="600px",
            padding="6",
        ),
        open=MatriculasState.is_detail_open,
        on_open_change=MatriculasState.set_is_detail_open,
    )


def matriculas_content() -> rx.Component:
    return rx.vstack(
        rx.card(
            rx.vstack(
                rx.vstack(
                    rx.heading("Nova matrícula", size="4", color="white"),
                    rx.text(
                        "Selecione um aluno e um plano ativos e informe o início.",
                        size="2",
                        color="var(--gray-9)",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.cond(
                    MatriculasState.form_error != "",
                    rx.callout(
                        MatriculasState.form_error,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Aluno ativo *", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecione um aluno",
                                width="100%",
                            ),
                            rx.select.content(
                                rx.select.group(
                                    rx.foreach(
                                        MatriculasState.alunos_ativos,
                                        aluno_option,
                                    )
                                )
                            ),
                            value=MatriculasState.selected_aluno_id,
                            on_change=MatriculasState.set_selected_aluno_id,
                            disabled=MatriculasState.is_saving,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Plano ativo *", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecione um plano",
                                width="100%",
                            ),
                            rx.select.content(
                                rx.select.group(
                                    rx.foreach(
                                        MatriculasState.planos_ativos,
                                        plano_option,
                                    )
                                )
                            ),
                            value=MatriculasState.selected_plano_id,
                            on_change=MatriculasState.set_selected_plano_id,
                            disabled=MatriculasState.is_saving,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Data de início *", size="2", weight="medium"),
                        rx.input(
                            type="date",
                            value=MatriculasState.data_inicio,
                            on_change=MatriculasState.set_data_inicio,
                            disabled=MatriculasState.is_saving,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    columns="repeat(auto-fit, minmax(220px, 1fr))",
                    spacing="4",
                    width="100%",
                ),
                rx.cond(
                    MatriculasState.alunos_ativos.length() == 0,
                    rx.callout(
                        "Não há alunos ativos disponíveis para matrícula.",
                        icon="info",
                        color_scheme="gray",
                        width="100%",
                    ),
                ),
                rx.cond(
                    MatriculasState.planos_ativos.length() == 0,
                    rx.callout(
                        "Cadastre ou reative um plano antes de criar matrículas.",
                        icon="info",
                        color_scheme="gray",
                        width="100%",
                    ),
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        rx.icon("user-round-plus", size=16),
                        "Criar matrícula",
                        color_scheme="blue",
                        on_click=MatriculasState.create_matricula,
                        loading=MatriculasState.is_saving,
                        disabled=(
                            (MatriculasState.alunos_ativos.length() == 0)
                            | (MatriculasState.planos_ativos.length() == 0)
                        ),
                    ),
                    width="100%",
                ),
                width="100%",
                spacing="4",
                align="stretch",
            ),
            background="#15171d",
            border="1px solid rgba(255, 255, 255, 0.08)",
            width="100%",
            padding="5",
        ),
        rx.cond(
            MatriculasState.error_message != "",
            rx.callout(
                MatriculasState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                role="alert",
                width="100%",
            ),
        ),
        rx.cond(
            MatriculasState.success_message != "",
            rx.callout(
                MatriculasState.success_message,
                icon="circle-check",
                color_scheme="green",
                role="status",
                width="100%",
            ),
        ),
        rx.cond(
            MatriculasState.is_loading,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Carregando matrículas...", color="var(--gray-9)"),
                    spacing="3",
                    align="center",
                ),
                min_height="220px",
                width="100%",
            ),
            rx.cond(
                MatriculasState.has_matriculas,
                rx.card(
                    rx.vstack(
                        rx.heading("Histórico de matrículas", size="4", color="white"),
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("ALUNO / PLANO"),
                                        rx.table.column_header_cell("INÍCIO"),
                                        rx.table.column_header_cell("TÉRMINO"),
                                        rx.table.column_header_cell("DURAÇÃO"),
                                        rx.table.column_header_cell("VALOR"),
                                        rx.table.column_header_cell("SITUAÇÃO"),
                                        rx.table.column_header_cell("CONSULTA"),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        MatriculasState.matriculas,
                                        enrollment_row,
                                    )
                                ),
                                width="100%",
                                variant="surface",
                            ),
                            overflow_x="auto",
                            width="100%",
                        ),
                        spacing="4",
                        align="stretch",
                        width="100%",
                    ),
                    background="#15171d",
                    border="1px solid rgba(255, 255, 255, 0.08)",
                    width="100%",
                    padding="5",
                ),
                rx.cond(
                    MatriculasState.error_message != "",
                    rx.box(min_height="160px", width="100%"),
                    rx.center(
                        rx.vstack(
                            rx.icon(
                                "clipboard-list",
                                size=24,
                                color="var(--gray-9)",
                            ),
                            rx.heading(
                                "Nenhuma matrícula cadastrada",
                                size="4",
                                color="white",
                            ),
                            rx.text(
                                "As matrículas e seus contratos aparecerão aqui.",
                                size="2",
                                color="var(--gray-9)",
                            ),
                            spacing="3",
                            align="center",
                            text_align="center",
                        ),
                        min_height="220px",
                        width="100%",
                    ),
                ),
            ),
        ),
        enrollment_detail_dialog(),
        width="100%",
        spacing="5",
        align="stretch",
    )


def matriculas_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "matriculas",
        "Gestão de matrículas",
        "Registre contratos e consulte o histórico de cada aluno.",
        matriculas_content(),
    )
