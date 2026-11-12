import re

import reflex as rx

from academia.access_control import AdminAccessState, begin_admin_check
from academia.login import LoginState
from academia.services.xano_client import XanoAPIError, XanoClient

EMPLOYEE_ROLES = ("admin", "recepcionista", "instrutor")


async def update_admin_access(
    state: rx.State,
    is_admin: bool,
    error_message: str = "",
    route: str = "",
) -> None:
    if not hasattr(state, "get_state"):
        return
    access_state = await state.get_state(AdminAccessState)
    access_state.is_admin = is_admin
    access_state.is_verifying = False
    access_state.error_message = error_message
    access_state.authorized_route = route if is_admin else ""


def filter_funcionarios(
    funcionarios: list[dict],
    query: str,
) -> list[dict]:
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return funcionarios

    return [
        funcionario
        for funcionario in funcionarios
        if normalized_query
        in " ".join(
            str(funcionario.get(field) or "")
            for field in ("name", "email", "role", "situacao", "status_convite")
        ).casefold()
    ]


def validate_funcionario_fields(
    name: str,
    email: str,
    role: str,
) -> str | None:
    if not name.strip():
        return "O nome do funcionário é obrigatório."
    normalized_email = email.strip()
    if not normalized_email:
        return "O e-mail do funcionário é obrigatório."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized_email):
        return "Informe um e-mail válido."
    if role not in EMPLOYEE_ROLES:
        return "Selecione um perfil válido."
    return None


class FuncionariosState(rx.State):
    funcionarios: list[dict] = []
    user_role: str = ""
    search_query: str = ""
    is_admin: bool = False
    is_loading: bool = False
    is_loading_details: bool = False
    is_saving: bool = False
    is_changing_status: bool = False
    error_message: str = ""
    success_message: str = ""
    form_error: str = ""
    is_form_open: bool = False
    is_editing: bool = False
    funcionario_id: int = 0
    form_name: str = ""
    form_email: str = ""
    form_role: str = "recepcionista"
    is_status_dialog_open: bool = False
    funcionario_id_to_change: int = 0
    is_reactivating: bool = False

    @rx.var
    def filtered_funcionarios(self) -> list[dict]:
        return filter_funcionarios(self.funcionarios, self.search_query)

    @rx.var
    def has_funcionarios(self) -> bool:
        return bool(self.filtered_funcionarios)

    async def _auth_token(self) -> str:
        login_state = await self.get_state(LoginState)
        return login_state.auth_token

    async def _clear_login(self) -> None:
        from academia.session_state import clear_app_session

        await clear_app_session(self)

    def _clear_sensitive_data(self) -> None:
        self.funcionarios = []
        self.user_role = ""
        self.search_query = ""
        self.is_admin = False
        self.is_loading = False
        self.is_loading_details = False
        self.is_saving = False
        self.is_changing_status = False
        self.error_message = ""
        self.success_message = ""
        self.is_form_open = False
        self.is_editing = False
        self._reset_form()
        self.is_status_dialog_open = False
        self.funcionario_id_to_change = 0
        self.is_reactivating = False

    def _api_error_message(self, error: XanoAPIError, action: str) -> str:
        if error.status_code == 401:
            return "Sua sessão expirou. Faça login novamente."
        if error.status_code == 403:
            return "Você não tem permissão para acessar a gestão de funcionários."
        if error.status_code in (400, 409):
            return str(error)
        if error.status_code is not None:
            return (
                f"Não foi possível {action}. "
                f"A API respondeu com HTTP {error.status_code}."
            )
        return f"Não foi possível {action}. Verifique a conexão e tente novamente."

    async def _reload_funcionarios(self, token: str, action: str) -> bool:
        try:
            funcionarios = XanoClient.get_funcionarios(token)
        except XanoAPIError as error:
            self.funcionarios = []
            if error.status_code == 403:
                self._clear_sensitive_data()
            self.error_message = self._api_error_message(error, action)
            return error.status_code == 401

        self.funcionarios = funcionarios
        self.error_message = ""
        return False

    def _reset_form(self) -> None:
        self.funcionario_id = 0
        self.form_name = ""
        self.form_email = ""
        self.form_role = "recepcionista"
        self.form_error = ""

    def _require_admin(self) -> bool:
        if self.is_admin:
            return True
        self._clear_sensitive_data()
        self.error_message = (
            "Você não tem permissão para acessar a gestão de funcionários."
        )
        return False

    @rx.event
    async def load_funcionarios(self):
        await begin_admin_check(self)
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            token = await self._auth_token()
            if not token:
                self._clear_sensitive_data()
                await self._clear_login()
                yield rx.redirect("/login")
                return

            try:
                identity = XanoClient.get_current_user(token)
            except XanoAPIError as error:
                self._clear_sensitive_data()
                self.error_message = self._api_error_message(
                    error,
                    "verificar seu acesso",
                )
                await update_admin_access(
                    self,
                    False,
                    self.error_message,
                )
                if error.status_code == 401:
                    await self._clear_login()
                    yield rx.redirect("/login")
                return

            self.user_role = str(identity.get("role") or "")
            self.is_admin = self.user_role == "admin"
            if not self.is_admin:
                self._clear_sensitive_data()
                self.error_message = (
                    "Você não tem permissão para acessar a gestão de funcionários."
                )
                await update_admin_access(self, False, self.error_message)
                return
            await update_admin_access(self, True, route="funcionarios")

            expired = await self._reload_funcionarios(
                token,
                "carregar os funcionários",
            )
            if expired:
                await self._clear_login()
                yield rx.redirect("/login")
        finally:
            await update_admin_access(
                self,
                self.is_admin,
                self.error_message if not self.is_admin else "",
                route="funcionarios",
            )
            self.is_loading = False

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value

    @rx.event
    def set_form_name(self, value: str):
        self.form_name = value

    @rx.event
    def set_form_email(self, value: str):
        self.form_email = value

    @rx.event
    def set_form_role(self, value: str):
        self.form_role = value

    @rx.event
    def set_is_form_open(self, is_open: bool):
        self.is_form_open = is_open
        if not is_open:
            self._reset_form()

    @rx.event
    def set_is_status_dialog_open(self, is_open: bool):
        self.is_status_dialog_open = is_open
        if not is_open:
            self.funcionario_id_to_change = 0

    @rx.event
    def open_new_funcionario(self):
        if not self._require_admin():
            return
        self._reset_form()
        self.is_editing = False
        self.error_message = ""
        self.success_message = ""
        self.is_form_open = True

    @rx.event
    async def edit_funcionario(self, funcionario_id: int):
        if not self._require_admin():
            return
        if funcionario_id <= 0:
            self.error_message = "Selecione um funcionário válido."
            return

        self.error_message = ""
        self.form_error = ""
        self.is_loading_details = True
        yield

        try:
            token = await self._auth_token()
            if not token:
                await self._clear_login()
                yield rx.redirect("/login")
                return

            try:
                funcionario = XanoClient.get_funcionario(token, funcionario_id)
            except XanoAPIError as error:
                error_message = self._api_error_message(
                    error,
                    "carregar os dados do funcionário",
                )
                if error.status_code == 401:
                    await self._clear_login()
                    yield rx.redirect("/login")
                elif error.status_code == 403:
                    self._clear_sensitive_data()
                    self.error_message = error_message
                else:
                    self.error_message = error_message
                return

            self._reset_form()
            self.funcionario_id = funcionario_id
            self.form_name = str(funcionario.get("name") or "")
            self.form_email = str(funcionario.get("email") or "")
            self.form_role = str(funcionario.get("role") or "")
            self.is_editing = True
            self.is_form_open = True
        finally:
            self.is_loading_details = False

    @rx.event
    async def save_funcionario(self):
        if not self._require_admin():
            return

        validation_error = validate_funcionario_fields(
            self.form_name,
            self.form_email,
            self.form_role,
        )
        if validation_error:
            self.form_error = validation_error
            return

        was_editing = self.is_editing
        self.form_error = ""
        self.is_saving = True
        yield

        try:
            token = await self._auth_token()
            if not token:
                await self._clear_login()
                yield rx.redirect("/login")
                return

            payload = {
                "name": self.form_name.strip(),
                "email": self.form_email.strip().lower(),
                "role": self.form_role,
            }
            try:
                if was_editing:
                    XanoClient.update_funcionario(
                        token,
                        self.funcionario_id,
                        payload,
                    )
                else:
                    XanoClient.invite_funcionario(token, payload)
            except XanoAPIError as error:
                self.form_error = self._api_error_message(
                    error,
                    "salvar o funcionário",
                )
                if error.status_code == 401:
                    await self._clear_login()
                    yield rx.redirect("/login")
                elif error.status_code == 403:
                    self._clear_sensitive_data()
                    self.error_message = self._api_error_message(
                        error,
                        "salvar o funcionário",
                    )
                return

            self.is_form_open = False
            self.success_message = (
                "Funcionário atualizado com sucesso."
                if was_editing
                else "Convite enviado com sucesso."
            )
            self.is_editing = False
            self._reset_form()
            expired = await self._reload_funcionarios(
                token,
                "atualizar a lista de funcionários",
            )
            if expired:
                await self._clear_login()
                yield rx.redirect("/login")
        finally:
            self.is_saving = False

    @rx.event
    def request_status_change(self, funcionario_id: int):
        if not self._require_admin():
            return
        funcionario = next(
            (
                item
                for item in self.funcionarios
                if str(item.get("id")) == str(funcionario_id)
            ),
            None,
        )
        if funcionario is None:
            self.error_message = "Funcionário não encontrado."
            return

        status = str(funcionario.get("situacao") or "").casefold()
        if status not in {"ativo", "inativo"}:
            self.error_message = "A situação do funcionário é inválida."
            return

        self.error_message = ""
        self.success_message = ""
        self.funcionario_id_to_change = funcionario_id
        self.is_reactivating = status == "inativo"
        self.is_status_dialog_open = True

    @rx.event
    def cancel_status_change(self):
        self.is_status_dialog_open = False
        self.funcionario_id_to_change = 0

    @rx.event
    async def confirm_status_change(self):
        if not self._require_admin():
            return
        if self.funcionario_id_to_change <= 0:
            self.error_message = "Selecione um funcionário para alterar."
            self.is_status_dialog_open = False
            return

        self.is_changing_status = True
        yield

        try:
            token = await self._auth_token()
            if not token:
                await self._clear_login()
                yield rx.redirect("/login")
                return

            try:
                if self.is_reactivating:
                    XanoClient.activate_funcionario(
                        token,
                        self.funcionario_id_to_change,
                    )
                else:
                    XanoClient.deactivate_funcionario(
                        token,
                        self.funcionario_id_to_change,
                    )
            except XanoAPIError as error:
                self.error_message = self._api_error_message(
                    error,
                    "alterar a situação do funcionário",
                )
                if error.status_code == 401:
                    await self._clear_login()
                    yield rx.redirect("/login")
                elif error.status_code == 403:
                    self._clear_sensitive_data()
                    self.error_message = self._api_error_message(
                        error,
                        "alterar a situação do funcionário",
                    )
                return

            self.is_status_dialog_open = False
            self.success_message = (
                "Funcionário ativado com sucesso."
                if self.is_reactivating
                else "Funcionário desativado com sucesso."
            )
            self.funcionario_id_to_change = 0
            expired = await self._reload_funcionarios(
                token,
                "atualizar a lista de funcionários",
            )
            if expired:
                await self._clear_login()
                yield rx.redirect("/login")
        finally:
            self.is_changing_status = False


def employee_row(funcionario: dict) -> rx.Component:
    status = funcionario.get("situacao", "Desconhecido")
    is_active = (status == "Ativo") | (status == "ativo")
    invite_status = funcionario.get("status_convite", "")
    return rx.table.row(
        rx.table.cell(
            rx.vstack(
                rx.text(
                    funcionario.get("name", "Nome não informado"),
                    weight="medium",
                ),
                rx.text(
                    funcionario.get("email", "E-mail não informado"),
                    size="1",
                    color="var(--gray-9)",
                ),
                spacing="1",
                align="start",
            )
        ),
        rx.table.cell(funcionario.get("role", "—")),
        rx.table.cell(
            rx.badge(
                status,
                color_scheme=rx.cond(is_active, "green", "gray"),
                variant="soft",
            )
        ),
        rx.table.cell(rx.cond(invite_status, invite_status, "—")),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("pencil", size=15),
                    "Editar",
                    variant="soft",
                    on_click=FuncionariosState.edit_funcionario(
                        funcionario.get("id", 0)
                    ),
                    disabled=FuncionariosState.is_loading_details,
                ),
                rx.button(
                    rx.icon(
                        rx.cond(
                            is_active,
                            "user-round-x",
                            "user-round-check",
                        ),
                        size=15,
                    ),
                    rx.cond(is_active, "Desativar", "Ativar"),
                    variant="soft",
                    color_scheme=rx.cond(is_active, "red", "green"),
                    on_click=FuncionariosState.request_status_change(
                        funcionario.get("id", 0)
                    ),
                    disabled=FuncionariosState.is_changing_status,
                ),
                spacing="2",
                flex_wrap="wrap",
            )
        ),
    )


def employee_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    FuncionariosState.is_editing,
                    "Editar funcionário",
                    "Convidar funcionário",
                ),
                color="white",
            ),
            rx.dialog.description(
                "Informe os dados operacionais. A senha é definida pelo próprio funcionário.",
                color="var(--gray-9)",
            ),
            rx.cond(
                FuncionariosState.form_error != "",
                rx.callout(
                    FuncionariosState.form_error,
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
                        value=FuncionariosState.form_name,
                        on_change=FuncionariosState.set_form_name,
                        placeholder="Nome completo",
                        max_length=200,
                        disabled=FuncionariosState.is_saving,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("E-mail *", size="2", weight="medium"),
                    rx.input(
                        type="email",
                        value=FuncionariosState.form_email,
                        on_change=FuncionariosState.set_form_email,
                        placeholder="funcionario@academia.com",
                        max_length=254,
                        disabled=FuncionariosState.is_saving,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Perfil *", size="2", weight="medium"),
                    rx.select.root(
                        rx.select.trigger(
                            placeholder="Selecione um perfil",
                            width="100%",
                        ),
                        rx.select.content(
                            rx.select.group(
                                rx.select.item("Administrador", value="admin"),
                                rx.select.item(
                                    "Recepcionista",
                                    value="recepcionista",
                                ),
                                rx.select.item("Instrutor", value="instrutor"),
                            )
                        ),
                        value=FuncionariosState.form_role,
                        on_change=FuncionariosState.set_form_role,
                        disabled=FuncionariosState.is_saving,
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
                            disabled=FuncionariosState.is_saving,
                        )
                    ),
                    rx.button(
                        rx.cond(
                            FuncionariosState.is_editing,
                            "Salvar alterações",
                            "Enviar convite",
                        ),
                        on_click=FuncionariosState.save_funcionario,
                        loading=FuncionariosState.is_saving,
                        color_scheme="blue",
                    ),
                    justify="end",
                    width="100%",
                    margin_top="4",
                ),
                spacing="4",
                width="100%",
                margin_top="4",
            ),
            background="#121215",
            border="1px solid rgba(255, 255, 255, 0.15)",
            border_radius="16px",
            max_width="560px",
            padding="6",
        ),
        open=FuncionariosState.is_form_open,
        on_open_change=FuncionariosState.set_is_form_open,
    )


def employee_status_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    FuncionariosState.is_reactivating,
                    "Reativar funcionário?",
                    "Desativar funcionário?",
                ),
                color="white",
            ),
            rx.dialog.description(
                "A conta será mantida e poderá ser consultada posteriormente.",
                color="var(--gray-9)",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=FuncionariosState.cancel_status_change,
                    )
                ),
                rx.button(
                    rx.cond(
                        FuncionariosState.is_reactivating,
                        "Confirmar reativação",
                        "Confirmar desativação",
                    ),
                    color_scheme=rx.cond(
                        FuncionariosState.is_reactivating,
                        "green",
                        "red",
                    ),
                    on_click=FuncionariosState.confirm_status_change,
                    loading=FuncionariosState.is_changing_status,
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
        open=FuncionariosState.is_status_dialog_open,
        on_open_change=FuncionariosState.set_is_status_dialog_open,
    )


def employee_management_content() -> rx.Component:
    employee_table = rx.card(
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("FUNCIONÁRIO"),
                        rx.table.column_header_cell("PERFIL"),
                        rx.table.column_header_cell("SITUAÇÃO"),
                        rx.table.column_header_cell("CONVITE"),
                        rx.table.column_header_cell("AÇÕES"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        FuncionariosState.filtered_funcionarios,
                        employee_row,
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
    )
    empty_state = rx.cond(
        FuncionariosState.funcionarios.length() > 0,
        rx.center(
            rx.text(
                "Nenhum funcionário corresponde à pesquisa.",
                color="var(--gray-9)",
            ),
            min_height="220px",
            width="100%",
        ),
        rx.center(
            rx.vstack(
                rx.box(
                    rx.icon("users-round", size=24, color="var(--gray-9)"),
                    background="#20232b",
                    padding="4",
                    border_radius="full",
                ),
                rx.heading("Nenhum funcionário cadastrado", size="4", color="white"),
                rx.text(
                    "Os funcionários convidados aparecerão nesta lista.",
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
    )
    admin_content = rx.vstack(
        rx.hstack(
            rx.input(
                rx.input.slot(rx.icon("search", size=16)),
                placeholder="Buscar por nome, e-mail, perfil ou situação",
                value=FuncionariosState.search_query,
                on_change=FuncionariosState.set_search_query,
                width=["100%", "420px"],
                size="3",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("user-round-plus", size=17),
                "Convidar funcionário",
                color_scheme="blue",
                on_click=FuncionariosState.open_new_funcionario,
            ),
            width="100%",
            flex_wrap="wrap",
            spacing="3",
        ),
        rx.cond(
            FuncionariosState.error_message != "",
            rx.callout(
                FuncionariosState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                role="alert",
                width="100%",
            ),
        ),
        rx.cond(
            FuncionariosState.success_message != "",
            rx.callout(
                FuncionariosState.success_message,
                icon="circle-check",
                color_scheme="green",
                role="status",
                width="100%",
            ),
        ),
        rx.cond(
            FuncionariosState.error_message != "",
            rx.box(min_height="220px", width="100%"),
            rx.cond(
                FuncionariosState.has_funcionarios,
                employee_table,
                empty_state,
            ),
        ),
        employee_form_dialog(),
        employee_status_dialog(),
        width="100%",
        spacing="5",
        align="stretch",
    )
    return rx.cond(
        FuncionariosState.is_loading,
        rx.center(
            rx.vstack(
                rx.spinner(size="3"),
                rx.text(
                    "Verificando acesso e carregando funcionários...",
                    color="var(--gray-9)",
                ),
                spacing="3",
                align="center",
            ),
            min_height="220px",
            width="100%",
        ),
        rx.cond(
            FuncionariosState.is_admin,
            admin_content,
            rx.callout(
                rx.cond(
                    FuncionariosState.error_message != "",
                    FuncionariosState.error_message,
                    "A gestão de funcionários está disponível somente para administradores.",
                ),
                icon="shield-alert",
                color_scheme="red",
                role="alert",
                width="100%",
            ),
        ),
    )


def funcionarios_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "funcionarios",
        "Gestão de funcionários",
        "Convide e mantenha as contas de acesso da academia.",
        employee_management_content(),
    )
