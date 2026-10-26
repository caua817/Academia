import reflex as rx

from academia.login import LoginState
from academia.services.xano_client import XanoAPIError, XanoClient


def filter_alunos(alunos: list[dict], query: str) -> list[dict]:
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return alunos

    return [
        aluno
        for aluno in alunos
        if normalized_query
        in " ".join(
            str(aluno.get(field) or "") for field in ("nome", "contato", "email")
        ).casefold()
    ]


def validate_nome(nome: str) -> str | None:
    if not nome.strip():
        return "O nome do aluno é obrigatório."
    return None


class AlunosState(rx.State):
    alunos: list[dict] = []
    search_query: str = ""
    is_loading: bool = False
    is_loading_details: bool = False
    is_saving: bool = False
    is_deactivating: bool = False
    error_message: str = ""
    success_message: str = ""
    form_error: str = ""
    is_form_open: bool = False
    is_editing: bool = False
    aluno_id: int = 0
    form_nome: str = ""
    form_cpf: str = ""
    form_data_nascimento: str = ""
    form_contato: str = ""
    form_email: str = ""
    form_endereco: str = ""
    is_deactivate_dialog_open: bool = False
    aluno_id_to_deactivate: int = 0

    @rx.var
    def filtered_alunos(self) -> list[dict]:
        return filter_alunos(self.alunos, self.search_query)

    @rx.var
    def has_alunos(self) -> bool:
        return bool(self.filtered_alunos)

    async def _auth_token(self) -> str:
        login_state = await self.get_state(LoginState)
        return login_state.auth_token

    async def _clear_login(self) -> None:
        from academia.session_state import clear_app_session

        await clear_app_session(self)

    def _clear_sensitive_data(self):
        self.alunos = []
        self.search_query = ""
        self.is_loading = False
        self.is_loading_details = False
        self.is_saving = False
        self.is_deactivating = False
        self.error_message = ""
        self.success_message = ""
        self._reset_form()
        self.is_form_open = False
        self.is_deactivate_dialog_open = False
        self.aluno_id_to_deactivate = 0

    def _api_error_message(self, error: XanoAPIError, action: str) -> str:
        if error.status_code == 401:
            return "Sua sessão expirou. Faça login novamente."
        if error.status_code == 403:
            return "Você não tem permissão para acessar a gestão de alunos."
        if error.status_code is not None:
            return (
                f"Não foi possível {action}. "
                f"A API respondeu com HTTP {error.status_code}."
            )
        return f"Não foi possível {action}. Verifique a conexão e tente novamente."

    async def _reload_alunos(self, token: str, action: str) -> bool:
        try:
            self.alunos = XanoClient.get_alunos(token)
            self.error_message = ""
        except XanoAPIError as error:
            self.alunos = []
            self.error_message = self._api_error_message(error, action)
            if error.status_code == 401:
                await self._clear_login()
                return True
        return False

    @rx.event
    async def load_alunos(self):
        self.is_loading = True
        self.error_message = ""
        yield

        token = await self._auth_token()
        if not token:
            self.alunos = []
            self.is_loading = False
            await self._clear_login()
            yield rx.redirect("/login")
            return

        try:
            expired = await self._reload_alunos(token, "carregar os alunos")
            if expired:
                yield rx.redirect("/login")
        finally:
            self.is_loading = False

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value

    @rx.event
    def set_form_nome(self, value: str):
        self.form_nome = value

    @rx.event
    def set_form_cpf(self, value: str):
        self.form_cpf = value

    @rx.event
    def set_form_data_nascimento(self, value: str):
        self.form_data_nascimento = value

    @rx.event
    def set_form_contato(self, value: str):
        self.form_contato = value

    @rx.event
    def set_form_email(self, value: str):
        self.form_email = value

    @rx.event
    def set_form_endereco(self, value: str):
        self.form_endereco = value

    @rx.event
    def set_is_form_open(self, value: bool):
        self.is_form_open = value
        if not value:
            self._reset_form()

    @rx.event
    def set_is_deactivate_dialog_open(self, value: bool):
        self.is_deactivate_dialog_open = value
        if not value:
            self.aluno_id_to_deactivate = 0

    def _reset_form(self):
        self.aluno_id = 0
        self.form_nome = ""
        self.form_cpf = ""
        self.form_data_nascimento = ""
        self.form_contato = ""
        self.form_email = ""
        self.form_endereco = ""
        self.form_error = ""

    @rx.event
    def open_new_aluno(self):
        self.success_message = ""
        self._reset_form()
        self.is_editing = False
        self.is_form_open = True

    @rx.event
    async def edit_aluno(self, aluno_id: int):
        self.error_message = ""
        self.form_error = ""
        self.is_loading_details = True
        yield

        token = await self._auth_token()
        if not token:
            self.is_loading_details = False
            await self._clear_login()
            yield rx.redirect("/login")
            return

        try:
            aluno = XanoClient.get_aluno(token, aluno_id)
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "carregar os dados do aluno",
            )
            if error.status_code == 401:
                await self._clear_login()
                yield rx.redirect("/login")
        else:
            self._reset_form()
            self.aluno_id = aluno_id
            self.form_nome = str(aluno.get("nome") or "")
            self.form_cpf = str(aluno.get("cpf") or "")
            self.form_data_nascimento = str(
                aluno.get("data_nascimento") or ""
            )[:10]
            self.form_contato = str(aluno.get("contato") or "")
            self.form_email = str(aluno.get("email") or "")
            self.form_endereco = str(aluno.get("endereco") or "")
            self.is_editing = True
            self.is_form_open = True
        finally:
            self.is_loading_details = False

    @rx.event
    async def save_aluno(self):
        nome = self.form_nome.strip()
        validation_error = validate_nome(nome)
        if validation_error:
            self.form_error = validation_error
            return

        self.form_error = ""
        self.is_saving = True
        yield

        token = await self._auth_token()
        if not token:
            self.is_saving = False
            await self._clear_login()
            yield rx.redirect("/login")
            return

        payload = {
            "nome": nome,
            "cpf": self.form_cpf.strip() or None,
            "data_nascimento": self.form_data_nascimento or None,
            "contato": self.form_contato.strip() or None,
            "email": self.form_email.strip() or None,
            "endereco": self.form_endereco.strip() or None,
        }

        try:
            if self.is_editing:
                XanoClient.update_aluno(token, self.aluno_id, payload)
            else:
                XanoClient.create_aluno(token, payload)
        except XanoAPIError as error:
            self.form_error = self._api_error_message(error, "salvar o aluno")
            self.is_saving = False
            if error.status_code == 401:
                self.alunos = []
                await self._clear_login()
                yield rx.redirect("/login")
            return

        self.is_saving = False
        self.is_form_open = False
        self.success_message = (
            "Aluno atualizado com sucesso."
            if self.is_editing
            else "Aluno cadastrado com sucesso."
        )
        self._reset_form()
        expired = await self._reload_alunos(token, "atualizar a lista")
        if expired:
            yield rx.redirect("/login")

    @rx.event
    def request_deactivation(self, aluno_id: int):
        self.aluno_id_to_deactivate = aluno_id
        self.is_deactivate_dialog_open = True
        self.error_message = ""
        self.success_message = ""

    @rx.event
    def clear_data(self):
        self._clear_sensitive_data()

    @rx.event
    def cancel_deactivation(self):
        self.is_deactivate_dialog_open = False
        self.aluno_id_to_deactivate = 0

    @rx.event
    async def confirm_deactivation(self):
        if self.aluno_id_to_deactivate <= 0:
            self.error_message = "Selecione um aluno para desativar."
            self.is_deactivate_dialog_open = False
            return

        self.is_deactivating = True
        yield

        token = await self._auth_token()
        if not token:
            self.is_deactivating = False
            await self._clear_login()
            yield rx.redirect("/login")
            return

        try:
            XanoClient.deactivate_aluno(token, self.aluno_id_to_deactivate)
        except XanoAPIError as error:
            self.error_message = self._api_error_message(error, "desativar o aluno")
            self.is_deactivating = False
            if error.status_code == 401:
                self.alunos = []
                await self._clear_login()
                yield rx.redirect("/login")
            return

        self.is_deactivating = False
        self.is_deactivate_dialog_open = False
        self.success_message = "Aluno desativado com sucesso."
        self.aluno_id_to_deactivate = 0
        expired = await self._reload_alunos(token, "atualizar a lista")
        if expired:
            yield rx.redirect("/login")


def aluno_management_row(aluno: dict) -> rx.Component:
    status = aluno.get("situacao", "Ativo")
    contact = rx.cond(
        aluno.get("contato"),
        aluno.get("contato"),
        rx.cond(aluno.get("email"), aluno.get("email"), "Sem contato"),
    )
    return rx.table.row(
        rx.table.cell(
            rx.vstack(
                rx.text(aluno.get("nome", "Nome não informado"), weight="medium"),
                rx.text(contact, size="1", color="var(--gray-9)"),
                spacing="1",
                align="start",
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
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("pencil", size=15),
                    "Editar",
                    variant="soft",
                    on_click=AlunosState.edit_aluno(aluno.get("id", 0)),
                    disabled=AlunosState.is_loading_details,
                ),
                rx.button(
                    rx.icon("user-round-x", size=15),
                    "Desativar",
                    variant="soft",
                    color_scheme="red",
                    on_click=AlunosState.request_deactivation(aluno.get("id", 0)),
                    disabled=AlunosState.is_deactivating,
                ),
                spacing="2",
            )
        ),
    )


def aluno_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(AlunosState.is_editing, "Editar aluno", "Cadastrar aluno"),
                color="white",
            ),
            rx.dialog.description(
                "Preencha os dados cadastrais necessários.",
                color="var(--gray-9)",
            ),
            rx.cond(
                AlunosState.form_error != "",
                rx.callout(
                    AlunosState.form_error,
                    icon="triangle-alert",
                    color_scheme="red",
                    role="alert",
                    width="100%",
                ),
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Nome *", size="2", weight="medium"),
                    rx.input(
                        value=AlunosState.form_nome,
                        on_change=AlunosState.set_form_nome,
                        placeholder="Nome completo",
                        max_length=200,
                        disabled=AlunosState.is_saving,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("CPF", size="2", weight="medium"),
                        rx.input(
                            value=AlunosState.form_cpf,
                            on_change=AlunosState.set_form_cpf,
                            placeholder="000.000.000-00",
                            disabled=AlunosState.is_saving,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Data de nascimento", size="2", weight="medium"),
                        rx.input(
                            type="date",
                            value=AlunosState.form_data_nascimento,
                            on_change=AlunosState.set_form_data_nascimento,
                            disabled=AlunosState.is_saving,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    columns="repeat(auto-fit, minmax(220px, 1fr))",
                    spacing="4",
                    width="100%",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Contato", size="2", weight="medium"),
                        rx.input(
                            value=AlunosState.form_contato,
                            on_change=AlunosState.set_form_contato,
                            placeholder="Telefone ou outro contato",
                            disabled=AlunosState.is_saving,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("E-mail", size="2", weight="medium"),
                        rx.input(
                            type="email",
                            value=AlunosState.form_email,
                            on_change=AlunosState.set_form_email,
                            placeholder="aluno@exemplo.com",
                            disabled=AlunosState.is_saving,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    columns="repeat(auto-fit, minmax(220px, 1fr))",
                    spacing="4",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Endereço", size="2", weight="medium"),
                    rx.input(
                        value=AlunosState.form_endereco,
                        on_change=AlunosState.set_form_endereco,
                        placeholder="Endereço do aluno",
                        disabled=AlunosState.is_saving,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            disabled=AlunosState.is_saving,
                        )
                    ),
                    rx.button(
                        rx.cond(AlunosState.is_editing, "Salvar alterações", "Cadastrar"),
                        on_click=AlunosState.save_aluno,
                        loading=AlunosState.is_saving,
                        color_scheme="blue",
                    ),
                    justify="end",
                    width="100%",
                ),
                spacing="4",
                width="100%",
                margin_top="4",
            ),
            background="#121215",
            border="1px solid rgba(255, 255, 255, 0.15)",
            border_radius="16px",
            max_width="680px",
            padding="6",
        ),
        open=AlunosState.is_form_open,
        on_open_change=AlunosState.set_is_form_open,
    )


def deactivate_confirmation_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Desativar aluno?", color="white"),
            rx.dialog.description(
                "O cadastro será mantido e poderá ser consultado posteriormente.",
                color="var(--gray-9)",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=AlunosState.cancel_deactivation,
                    )
                ),
                rx.button(
                    "Confirmar desativação",
                    color_scheme="red",
                    on_click=AlunosState.confirm_deactivation,
                    loading=AlunosState.is_deactivating,
                ),
                justify="end",
                width="100%",
                margin_top="4",
            ),
            background="#121215",
            border="1px solid rgba(255, 255, 255, 0.15)",
            border_radius="16px",
            max_width="480px",
            padding="6",
        ),
        open=AlunosState.is_deactivate_dialog_open,
        on_open_change=AlunosState.set_is_deactivate_dialog_open,
    )


def student_management_content() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.input(
                rx.input.slot(rx.icon("search", size=16)),
                placeholder="Buscar por nome ou contato",
                value=AlunosState.search_query,
                on_change=AlunosState.set_search_query,
                width=["100%", "360px"],
                size="3",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=17),
                "Novo aluno",
                color_scheme="blue",
                on_click=AlunosState.open_new_aluno,
            ),
            width="100%",
            flex_wrap="wrap",
            spacing="3",
        ),
        rx.cond(
            AlunosState.error_message != "",
            rx.callout(
                AlunosState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                role="alert",
                width="100%",
            ),
        ),
        rx.cond(
            AlunosState.success_message != "",
            rx.callout(
                AlunosState.success_message,
                icon="circle-check",
                color_scheme="green",
                role="status",
                width="100%",
            ),
        ),
        rx.cond(
            AlunosState.is_loading,
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
                AlunosState.has_alunos,
                rx.card(
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("ALUNO"),
                                    rx.table.column_header_cell("SITUAÇÃO"),
                                    rx.table.column_header_cell("AÇÕES"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AlunosState.filtered_alunos,
                                    aluno_management_row,
                                )
                            ),
                            width="100%",
                            variant="surface",
                        ),
                        overflow_x="auto",
                        width="100%",
                    ),
                    background="#15171d",
                    border="1px solid rgba(255, 255, 255, 0.08)",
                    width="100%",
                    padding="4",
                ),
                rx.cond(
                    AlunosState.error_message != "",
                    rx.box(min_height="220px", width="100%"),
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
                                    AlunosState.alunos.length() > 0,
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
            AlunosState.error_message != "",
            rx.hstack(
                rx.spacer(),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Tentar novamente",
                    on_click=AlunosState.load_alunos,
                    loading=AlunosState.is_loading,
                    variant="soft",
                ),
                width="100%",
            ),
        ),
        aluno_form_dialog(),
        deactivate_confirmation_dialog(),
        width="100%",
        spacing="5",
        align="stretch",
    )
