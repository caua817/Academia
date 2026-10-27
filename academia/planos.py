from decimal import Decimal, InvalidOperation

import reflex as rx

from academia.login import LoginState
from academia.services.xano_client import XanoAPIError, XanoClient


def validate_plano_fields(
    nome: str,
    duracao_meses: str,
    valor: str,
) -> str | None:
    if not nome.strip():
        return "O nome do plano é obrigatório."

    try:
        duration = int(duracao_meses.strip())
    except ValueError:
        return "Informe a duração do plano em meses inteiros."
    if duration <= 0:
        return "A duração do plano deve ser maior que zero."

    try:
        price = Decimal(valor.strip().replace(",", "."))
    except InvalidOperation:
        return "Informe um valor válido para o plano."
    if not price.is_finite() or price <= 0:
        return "O valor do plano deve ser maior que zero."
    return None


def format_currency(value: object) -> str:
    amount = Decimal(str(value))
    return f"R$ {amount:.2f}".replace(".", ",")


class PlanosState(rx.State):
    planos: list[dict] = []
    is_loading: bool = False
    is_loading_details: bool = False
    is_saving: bool = False
    is_changing_status: bool = False
    error_message: str = ""
    success_message: str = ""
    form_error: str = ""
    is_form_open: bool = False
    is_editing: bool = False
    plano_id: int = 0
    form_nome: str = ""
    form_descricao: str = ""
    form_duracao_meses: str = ""
    form_valor: str = ""

    @rx.var
    def has_planos(self) -> bool:
        return bool(self.planos)

    def _api_error_message(self, error: XanoAPIError, action: str) -> str:
        if error.status_code == 401:
            return "Sua sessão expirou. Faça login novamente."
        if error.status_code == 403:
            return "Você não tem permissão para acessar a gestão de planos."
        if error.status_code in (400, 409):
            return str(error)
        if error.status_code is not None:
            return (
                f"Não foi possível {action}. "
                f"A API respondeu com HTTP {error.status_code}."
            )
        return f"Não foi possível {action}. Verifique a conexão e tente novamente."

    def _reload_planos(self, token: str, action: str) -> bool:
        try:
            planos = XanoClient.get_planos(token)
        except XanoAPIError as error:
            self.planos = []
            self.error_message = self._api_error_message(error, action)
            return error.status_code == 401

        self.planos = [
            {**plano, "valor_formatado": format_currency(plano.get("valor"))}
            for plano in planos
        ]
        self.error_message = ""
        return False

    def _reset_form(self):
        self.plano_id = 0
        self.form_nome = ""
        self.form_descricao = ""
        self.form_duracao_meses = ""
        self.form_valor = ""
        self.form_error = ""

    def _clear_sensitive_data(self):
        self.planos = []
        self.is_loading = False
        self.is_loading_details = False
        self.is_saving = False
        self.is_changing_status = False
        self.error_message = ""
        self.success_message = ""
        self.is_form_open = False
        self.is_editing = False
        self._reset_form()

    @rx.event
    def clear_data(self):
        self._clear_sensitive_data()

    @rx.event
    async def load_planos(self):
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

        expired = self._reload_planos(
            login_state.auth_token,
            "carregar os planos",
        )
        self.is_loading = False
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")

    @rx.event
    def set_is_form_open(self, is_open: bool):
        self.is_form_open = is_open
        if not is_open:
            self._reset_form()

    @rx.event
    def set_form_nome(self, value: str):
        self.form_nome = value

    @rx.event
    def set_form_descricao(self, value: str):
        self.form_descricao = value

    @rx.event
    def set_form_duracao_meses(self, value: str):
        self.form_duracao_meses = value

    @rx.event
    def set_form_valor(self, value: str):
        self.form_valor = value

    @rx.event
    def open_new_plano(self):
        self._reset_form()
        self.is_editing = False
        self.success_message = ""
        self.is_form_open = True

    @rx.event
    async def edit_plano(self, plano_id: int):
        self.error_message = ""
        self.form_error = ""
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
            plano = XanoClient.get_plano(login_state.auth_token, plano_id)
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "carregar os dados do plano",
            )
            if error.status_code == 401:
                from academia.session_state import clear_app_session

                await clear_app_session(self)
                yield rx.redirect("/login")
        else:
            self._reset_form()
            self.plano_id = plano_id
            self.form_nome = str(plano.get("nome") or "")
            self.form_descricao = str(plano.get("descricao") or "")
            self.form_duracao_meses = str(plano.get("duracao_meses") or "")
            self.form_valor = str(plano.get("valor") or "")
            self.is_editing = True
            self.is_form_open = True
        finally:
            self.is_loading_details = False

    @rx.event
    async def save_plano(self):
        validation_error = validate_plano_fields(
            self.form_nome,
            self.form_duracao_meses,
            self.form_valor,
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
            "nome": self.form_nome.strip(),
            "descricao": self.form_descricao.strip() or None,
            "duracao_meses": int(self.form_duracao_meses.strip()),
            "valor": float(
                Decimal(self.form_valor.strip().replace(",", "."))
            ),
        }

        try:
            if self.is_editing:
                XanoClient.update_plano(
                    login_state.auth_token,
                    self.plano_id,
                    payload,
                )
            else:
                XanoClient.create_plano(login_state.auth_token, payload)
        except XanoAPIError as error:
            self.form_error = self._api_error_message(error, "salvar o plano")
            self.is_saving = False
            if error.status_code == 401:
                from academia.session_state import clear_app_session

                await clear_app_session(self)
                yield rx.redirect("/login")
            return

        self.is_saving = False
        self.is_form_open = False
        self.success_message = (
            "Plano atualizado com sucesso."
            if self.is_editing
            else "Plano cadastrado com sucesso."
        )
        self._reset_form()
        expired = self._reload_planos(
            login_state.auth_token,
            "atualizar a lista de planos",
        )
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")

    @rx.event
    async def change_status(self, plano_id: int):
        self.error_message = ""
        self.success_message = ""
        self.is_changing_status = True
        yield

        login_state = await self.get_state(LoginState)
        if not login_state.auth_token:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            self.is_changing_status = False
            yield rx.redirect("/login")
            return

        plano = next(
            (item for item in self.planos if item.get("id") == plano_id),
            None,
        )
        if plano is None:
            self.error_message = "Plano não encontrado na lista atual."
            self.is_changing_status = False
            return

        is_active = plano.get("situacao") == "Ativo"
        try:
            if is_active:
                XanoClient.deactivate_plano(login_state.auth_token, plano_id)
            else:
                XanoClient.reactivate_plano(login_state.auth_token, plano_id)
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "alterar a situação do plano",
            )
            self.is_changing_status = False
            if error.status_code == 401:
                from academia.session_state import clear_app_session

                await clear_app_session(self)
                yield rx.redirect("/login")
            return

        self.is_changing_status = False
        self.success_message = (
            "Plano descontinuado com sucesso."
            if is_active
            else "Plano reativado com sucesso."
        )
        expired = self._reload_planos(
            login_state.auth_token,
            "atualizar a lista de planos",
        )
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")


def plan_row(plano: dict) -> rx.Component:
    status = plano.get("situacao", "Ativo")
    return rx.table.row(
        rx.table.cell(
            rx.vstack(
                rx.text(plano.get("nome", "Plano sem nome"), weight="medium"),
                rx.text(
                    rx.cond(
                        plano.get("descricao"),
                        plano.get("descricao"),
                        "Sem descrição",
                    ),
                    size="1",
                    color="var(--gray-9)",
                ),
                spacing="1",
                align="start",
            )
        ),
        rx.table.cell(plano.get("duracao_meses", 0), " meses"),
        rx.table.cell(plano.get("valor_formatado", "Valor indisponível")),
        rx.table.cell(
            rx.badge(
                status,
                color_scheme=rx.cond(status == "Ativo", "green", "gray"),
                variant="soft",
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("pencil", size=15),
                    "Editar",
                    variant="soft",
                    on_click=PlanosState.edit_plano(plano.get("id", 0)),
                    disabled=PlanosState.is_loading_details,
                ),
                rx.button(
                    rx.icon(
                        rx.cond(status == "Ativo", "ban", "circle-check"),
                        size=15,
                    ),
                    rx.cond(status == "Ativo", "Descontinuar", "Reativar"),
                    variant="soft",
                    color_scheme=rx.cond(status == "Ativo", "red", "green"),
                    on_click=PlanosState.change_status(plano.get("id", 0)),
                    disabled=PlanosState.is_changing_status,
                ),
                spacing="2",
                flex_wrap="wrap",
            )
        ),
    )


def plan_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(PlanosState.is_editing, "Editar plano", "Cadastrar plano"),
                color="white",
            ),
            rx.dialog.description(
                "Defina o nome, a duração em meses e o valor do plano.",
                color="var(--gray-9)",
            ),
            rx.cond(
                PlanosState.form_error != "",
                rx.callout(
                    PlanosState.form_error,
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
                        value=PlanosState.form_nome,
                        on_change=PlanosState.set_form_nome,
                        placeholder="Ex.: Plano mensal",
                        max_length=120,
                        disabled=PlanosState.is_saving,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Descrição", size="2", weight="medium"),
                    rx.text_area(
                        value=PlanosState.form_descricao,
                        on_change=PlanosState.set_form_descricao,
                        placeholder="Detalhes opcionais do plano",
                        disabled=PlanosState.is_saving,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Duração (meses) *", size="2", weight="medium"),
                        rx.input(
                            type="number",
                            min="1",
                            step="1",
                            value=PlanosState.form_duracao_meses,
                            on_change=PlanosState.set_form_duracao_meses,
                            placeholder="1",
                            disabled=PlanosState.is_saving,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Valor do plano (R$) *", size="2", weight="medium"),
                        rx.input(
                            type="number",
                            min="0.01",
                            step="0.01",
                            value=PlanosState.form_valor,
                            on_change=PlanosState.set_form_valor,
                            placeholder="99.90",
                            disabled=PlanosState.is_saving,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    columns="repeat(auto-fit, minmax(200px, 1fr))",
                    spacing="4",
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=PlanosState.set_is_form_open(False),
                        )
                    ),
                    rx.button(
                        "Salvar plano",
                        on_click=PlanosState.save_plano,
                        loading=PlanosState.is_saving,
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
        open=PlanosState.is_form_open,
        on_open_change=PlanosState.set_is_form_open,
    )


def planos_content() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Planos cadastrados", size="4", color="white"),
                rx.text(
                    "Gerencie valores e disponibilidade para novas matrículas.",
                    size="2",
                    color="var(--gray-9)",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=17),
                "Novo plano",
                color_scheme="blue",
                on_click=PlanosState.open_new_plano,
            ),
            width="100%",
            flex_wrap="wrap",
            spacing="3",
        ),
        rx.cond(
            PlanosState.error_message != "",
            rx.callout(
                PlanosState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                role="alert",
                width="100%",
            ),
        ),
        rx.cond(
            PlanosState.success_message != "",
            rx.callout(
                PlanosState.success_message,
                icon="circle-check",
                color_scheme="green",
                role="status",
                width="100%",
            ),
        ),
        rx.cond(
            PlanosState.is_loading,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Carregando planos...", color="var(--gray-9)"),
                    spacing="3",
                    align="center",
                ),
                min_height="220px",
                width="100%",
            ),
            rx.cond(
                PlanosState.has_planos,
                rx.card(
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("PLANO"),
                                    rx.table.column_header_cell("DURAÇÃO"),
                                    rx.table.column_header_cell("VALOR"),
                                    rx.table.column_header_cell("SITUAÇÃO"),
                                    rx.table.column_header_cell("AÇÕES"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(PlanosState.planos, plan_row)
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
                    PlanosState.error_message != "",
                    rx.box(min_height="220px", width="100%"),
                    rx.center(
                        rx.vstack(
                            rx.box(
                                rx.icon(
                                    "credit-card",
                                    size=24,
                                    color="var(--gray-9)",
                                ),
                                background="#20232b",
                                padding="4",
                                border_radius="full",
                            ),
                            rx.heading(
                                "Nenhum plano cadastrado",
                                size="4",
                                color="white",
                            ),
                            rx.text(
                                "Os planos cadastrados aparecerão nesta lista.",
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
        plan_form_dialog(),
        width="100%",
        spacing="5",
        align="stretch",
    )


def planos_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "planos",
        "Gestão de planos",
        "Cadastre e mantenha os planos oferecidos pela academia.",
        planos_content(),
    )
