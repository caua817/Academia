import reflex as rx

from academia.access_control import begin_admin_check, require_admin
from academia.login import LoginState
from academia.planos import format_currency
from academia.services.xano_client import XanoAPIError, XanoClient


class FinanceiroState(rx.State):
    mensalidades: list[dict] = []
    pagamentos: list[dict] = []
    is_loading: bool = False
    is_saving: bool = False
    is_correcting: bool = False
    is_correction_open: bool = False
    error_message: str = ""
    success_message: str = ""
    form_error: str = ""
    forma_pagamento: str = "PIX"
    pagamento_id: int = 0
    tipo_correcao: str = "Cancelado"
    motivo_correcao: str = ""

    @rx.var
    def has_mensalidades(self) -> bool:
        return bool(self.mensalidades)

    @rx.var
    def has_pagamentos(self) -> bool:
        return bool(self.pagamentos)

    def _api_error_message(self, error: XanoAPIError, action: str) -> str:
        if error.status_code == 401:
            return "Sua sessão expirou. Faça login novamente."
        if error.status_code == 403:
            return "Você não tem permissão para acessar a gestão financeira."
        if error.status_code in (400, 409):
            return str(error)
        if error.status_code is not None:
            return (
                f"Não foi possível {action}. "
                f"A API respondeu com HTTP {error.status_code}."
            )
        return f"Não foi possível {action}. Verifique a conexão e tente novamente."

    def _clear_sensitive_data(self):
        self.mensalidades = []
        self.pagamentos = []
        self.is_loading = False
        self.is_saving = False
        self.is_correcting = False
        self.is_correction_open = False
        self.error_message = ""
        self.success_message = ""
        self.form_error = ""
        self.forma_pagamento = "PIX"
        self.pagamento_id = 0
        self.tipo_correcao = "Cancelado"
        self.motivo_correcao = ""

    @rx.event
    def clear_data(self):
        self._clear_sensitive_data()

    def _reload(self, token: str, action: str) -> bool:
        try:
            mensalidades = XanoClient.get_mensalidades(token)
            pagamentos = XanoClient.get_pagamentos(token)
        except XanoAPIError as error:
            self.mensalidades = []
            self.pagamentos = []
            self.error_message = self._api_error_message(error, action)
            return error.status_code == 401

        self.mensalidades = [
            {
                **mensalidade,
                "valor_formatado": format_currency(mensalidade.get("valor")),
            }
            for mensalidade in mensalidades
        ]
        self.pagamentos = [
            {
                **pagamento,
                "valor_formatado": format_currency(pagamento.get("valor")),
            }
            for pagamento in pagamentos
        ]
        self.error_message = ""
        return False

    @rx.event
    async def load_financeiro(self):
        await begin_admin_check(self)
        self.is_loading = True
        self.error_message = ""
        yield

        token, should_redirect = await require_admin(self, "financeiro")
        if not token:
            self.is_loading = False
            if should_redirect:
                yield rx.redirect("/login")
            return

        expired = self._reload(
            token,
            "carregar os dados financeiros",
        )
        self.is_loading = False
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")

    @rx.event
    def set_forma_pagamento(self, value: str):
        self.forma_pagamento = value

    @rx.event
    def set_is_correction_open(self, is_open: bool):
        self.is_correction_open = is_open
        if not is_open:
            self.pagamento_id = 0
            self.motivo_correcao = ""
            self.form_error = ""

    @rx.event
    def set_tipo_correcao(self, value: str):
        self.tipo_correcao = value

    @rx.event
    def set_motivo_correcao(self, value: str):
        self.motivo_correcao = value

    @rx.event
    async def registrar_pagamento(self, mensalidade_id: int):
        self.error_message = ""
        self.success_message = ""
        self.form_error = ""
        mensalidade = next(
            (
                item
                for item in self.mensalidades
                if item.get("id") == mensalidade_id
            ),
            None,
        )
        if mensalidade is None:
            self.error_message = (
                "A mensalidade não está mais disponível. Atualize a lista."
            )
            return

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
            "mensalidade_id": mensalidade_id,
            "valor": float(mensalidade.get("valor", 0)),
            "forma_pagamento": self.forma_pagamento,
        }
        try:
            XanoClient.create_pagamento(login_state.auth_token, payload)
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "registrar o pagamento",
            )
            self.is_saving = False
            if error.status_code == 401:
                from academia.session_state import clear_app_session

                await clear_app_session(self)
                yield rx.redirect("/login")
            return

        self.is_saving = False
        self.success_message = "Pagamento registrado com sucesso."
        expired = self._reload(
            login_state.auth_token,
            "atualizar o histórico financeiro",
        )
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")

    @rx.event
    def abrir_correcao(self, pagamento_id: int, tipo_correcao: str):
        self.error_message = ""
        self.form_error = ""
        self.pagamento_id = pagamento_id
        self.tipo_correcao = tipo_correcao
        self.motivo_correcao = ""
        self.is_correction_open = True

    @rx.event
    async def corrigir_pagamento(self):
        if not self.motivo_correcao.strip():
            self.form_error = "Informe o motivo da correção."
            return

        self.is_correcting = True
        self.error_message = ""
        self.form_error = ""
        yield

        login_state = await self.get_state(LoginState)
        if not login_state.auth_token:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            self.is_correcting = False
            yield rx.redirect("/login")
            return

        payload = {
            "tipo_correcao": self.tipo_correcao,
            "motivo": self.motivo_correcao.strip(),
        }
        try:
            XanoClient.correct_pagamento(
                login_state.auth_token,
                self.pagamento_id,
                payload,
            )
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "corrigir o pagamento",
            )
            self.is_correcting = False
            if error.status_code == 401:
                from academia.session_state import clear_app_session

                await clear_app_session(self)
                yield rx.redirect("/login")
            return

        self.is_correcting = False
        self.is_correction_open = False
        self.pagamento_id = 0
        self.motivo_correcao = ""
        self.success_message = "Correção registrada no histórico."
        expired = self._reload(
            login_state.auth_token,
            "atualizar o histórico financeiro",
        )
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")


class CheckinsState(rx.State):
    alunos_ativos: list[dict[str, str]] = []
    checkins: list[dict] = []
    is_loading: bool = False
    is_saving: bool = False
    error_message: str = ""
    success_message: str = ""
    aluno_id: str = ""

    @rx.var
    def has_checkins(self) -> bool:
        return bool(self.checkins)

    def _clear_sensitive_data(self):
        self.alunos_ativos = []
        self.checkins = []
        self.is_loading = False
        self.is_saving = False
        self.error_message = ""
        self.success_message = ""
        self.aluno_id = ""

    @rx.event
    def clear_data(self):
        self._clear_sensitive_data()

    def _api_error_message(self, error: XanoAPIError, action: str) -> str:
        if error.status_code == 401:
            return "Sua sessão expirou. Faça login novamente."
        if error.status_code == 403:
            return "Você não tem permissão para acessar os check-ins."
        if error.status_code in (400, 409):
            return str(error)
        if error.status_code is not None:
            return (
                f"Não foi possível {action}. "
                f"A API respondeu com HTTP {error.status_code}."
            )
        return f"Não foi possível {action}. Verifique a conexão e tente novamente."

    def _reload(self, token: str, action: str) -> bool:
        try:
            alunos = XanoClient.get_checkin_alunos(token)
            checkins = XanoClient.get_checkins(token)
        except XanoAPIError as error:
            self.alunos_ativos = []
            self.checkins = []
            self.error_message = self._api_error_message(error, action)
            return error.status_code == 401

        self.alunos_ativos = [
            {"id": str(aluno.get("id", "")), "nome": str(aluno.get("nome", ""))}
            for aluno in alunos
        ]
        self.checkins = checkins
        self.error_message = ""
        return False

    @rx.event
    async def load_checkins(self):
        await begin_admin_check(self)
        self.is_loading = True
        self.error_message = ""
        yield

        token, should_redirect = await require_admin(self, "checkins")
        if not token:
            self.is_loading = False
            if should_redirect:
                yield rx.redirect("/login")
            return

        expired = self._reload(
            token,
            "carregar os check-ins",
        )
        self.is_loading = False
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")

    @rx.event
    def set_aluno_id(self, value: str):
        self.aluno_id = value

    @rx.event
    async def registrar_checkin(self):
        self.error_message = ""
        self.success_message = ""
        try:
            aluno_id = int(self.aluno_id)
        except ValueError:
            self.error_message = "Selecione um aluno ativo."
            return
        if aluno_id <= 0:
            self.error_message = "Selecione um aluno ativo."
            return

        self.is_saving = True
        yield

        login_state = await self.get_state(LoginState)
        if not login_state.auth_token:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            self.is_saving = False
            yield rx.redirect("/login")
            return

        try:
            XanoClient.create_checkin(
                login_state.auth_token,
                {"aluno_id": aluno_id},
            )
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "registrar o check-in",
            )
            self.is_saving = False
            if error.status_code == 401:
                from academia.session_state import clear_app_session

                await clear_app_session(self)
                yield rx.redirect("/login")
            return

        self.is_saving = False
        self.aluno_id = ""
        self.success_message = "Check-in registrado com sucesso."
        expired = self._reload(
            login_state.auth_token,
            "atualizar o histórico de check-ins",
        )
        if expired:
            from academia.session_state import clear_app_session

            await clear_app_session(self)
            yield rx.redirect("/login")


def mensalidade_row(mensalidade: dict) -> rx.Component:
    status = mensalidade.get("situacao", "Pendente")
    return rx.table.row(
        rx.table.cell(mensalidade.get("aluno_nome", "Aluno")),
        rx.table.cell(mensalidade.get("competencia", "")),
        rx.table.cell(mensalidade.get("data_vencimento", "")),
        rx.table.cell(mensalidade.get("valor_formatado", "Valor indisponível")),
        rx.table.cell(
            rx.badge(
                status,
                color_scheme=rx.cond(
                    status == "Paga",
                    "green",
                    rx.cond(status == "Atrasada", "red", "gray"),
                ),
                variant="soft",
            )
        ),
        rx.table.cell(
            rx.cond(
                status != "Paga",
                rx.button(
                    "Registrar pagamento",
                    on_click=FinanceiroState.registrar_pagamento(
                        mensalidade.get("id", 0)
                    ),
                    loading=FinanceiroState.is_saving,
                    disabled=FinanceiroState.is_saving,
                    size="2",
                    color_scheme="blue",
                    variant="soft",
                ),
                rx.text(
                    mensalidade.get("forma_pagamento", ""),
                    size="2",
                    color="var(--gray-9)",
                ),
            )
        ),
    )


def pagamento_row(pagamento: dict) -> rx.Component:
    status = pagamento.get("situacao", "Registrado")
    return rx.table.row(
        rx.table.cell(pagamento.get("aluno_nome", "Aluno")),
        rx.table.cell(pagamento.get("competencia", "")),
        rx.table.cell(pagamento.get("valor_formatado", "Valor indisponível")),
        rx.table.cell(pagamento.get("forma_pagamento", "")),
        rx.table.cell(
            rx.vstack(
                rx.badge(
                    status,
                    color_scheme=rx.cond(status == "Registrado", "green", "gray"),
                    variant="soft",
                ),
                rx.cond(
                    pagamento.get("motivo_correcao"),
                    rx.text(
                        pagamento.get("motivo_correcao", ""),
                        size="1",
                        color="var(--gray-9)",
                    ),
                ),
                align="start",
                spacing="1",
            )
        ),
        rx.table.cell(
            rx.cond(
                status == "Registrado",
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        on_click=FinanceiroState.abrir_correcao(
                            pagamento.get("id", 0),
                            "Cancelado",
                        ),
                        variant="soft",
                        color_scheme="gray",
                        size="1",
                        disabled=FinanceiroState.is_correcting,
                    ),
                    rx.button(
                        "Estornar",
                        on_click=FinanceiroState.abrir_correcao(
                            pagamento.get("id", 0),
                            "Estornado",
                        ),
                        variant="soft",
                        color_scheme="red",
                        size="1",
                        disabled=FinanceiroState.is_correcting,
                    ),
                    spacing="2",
                    flex_wrap="wrap",
                ),
                rx.text("—", color="var(--gray-9)"),
            )
        ),
    )


def correction_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Corrigir pagamento", color="white"),
            rx.dialog.description(
                "A correção será registrada no histórico, sem excluir o lançamento.",
                color="var(--gray-9)",
            ),
            rx.cond(
                FinanceiroState.form_error != "",
                rx.callout(
                    FinanceiroState.form_error,
                    icon="triangle-alert",
                    color_scheme="red",
                    role="alert",
                    width="100%",
                ),
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Tipo de correção", size="2", weight="medium"),
                    rx.select.root(
                        rx.select.trigger(width="100%"),
                        rx.select.content(
                            rx.select.item("Cancelamento", value="Cancelado"),
                            rx.select.item("Estorno contábil", value="Estornado"),
                        ),
                        value=FinanceiroState.tipo_correcao,
                        on_change=FinanceiroState.set_tipo_correcao,
                        disabled=FinanceiroState.is_correcting,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Motivo *", size="2", weight="medium"),
                    rx.text_area(
                        value=FinanceiroState.motivo_correcao,
                        on_change=FinanceiroState.set_motivo_correcao,
                        max_length=500,
                        disabled=FinanceiroState.is_correcting,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Voltar",
                            variant="soft",
                            color_scheme="gray",
                            disabled=FinanceiroState.is_correcting,
                        )
                    ),
                    rx.button(
                        "Confirmar correção",
                        on_click=FinanceiroState.corrigir_pagamento,
                        loading=FinanceiroState.is_correcting,
                        color_scheme="red",
                    ),
                    justify="end",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            background="#121215",
            border="1px solid rgba(255, 255, 255, 0.15)",
            border_radius="16px",
            max_width="520px",
            padding="6",
        ),
        open=FinanceiroState.is_correction_open,
        on_open_change=FinanceiroState.set_is_correction_open,
    )


def financeiro_content() -> rx.Component:
    return rx.vstack(
        rx.cond(
            FinanceiroState.error_message != "",
            rx.callout(
                FinanceiroState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                role="alert",
                width="100%",
            ),
        ),
        rx.cond(
            FinanceiroState.success_message != "",
            rx.callout(
                FinanceiroState.success_message,
                icon="circle-check",
                color_scheme="green",
                role="status",
                width="100%",
            ),
        ),
        rx.cond(
            FinanceiroState.is_loading,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Carregando dados financeiros...", color="var(--gray-9)"),
                    spacing="3",
                    align="center",
                ),
                min_height="220px",
                width="100%",
            ),
            rx.vstack(
                rx.card(
                    rx.vstack(
                        rx.heading("Mensalidades", size="4", color="white"),
                        rx.text(
                            "O atraso é calculado após o vencimento. Matrículas anteriores à implantação não geram parcelas retroativas.",
                            size="2",
                            color="var(--gray-9)",
                        ),
                        rx.vstack(
                            rx.text("Forma de pagamento", size="2", weight="medium"),
                            rx.select.root(
                                rx.select.trigger(width="100%"),
                                rx.select.content(
                                    rx.select.item("PIX", value="PIX"),
                                    rx.select.item("Cartão", value="Cartão"),
                                ),
                                value=FinanceiroState.forma_pagamento,
                                on_change=FinanceiroState.set_forma_pagamento,
                                disabled=FinanceiroState.is_saving,
                            ),
                            spacing="1",
                            width=["100%", "260px"],
                            align="start",
                        ),
                        rx.cond(
                            FinanceiroState.has_mensalidades,
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("ALUNO"),
                                            rx.table.column_header_cell("COMPETÊNCIA"),
                                            rx.table.column_header_cell("VENCIMENTO"),
                                            rx.table.column_header_cell("VALOR"),
                                            rx.table.column_header_cell("SITUAÇÃO"),
                                            rx.table.column_header_cell("AÇÃO"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            FinanceiroState.mensalidades,
                                            mensalidade_row,
                                        )
                                    ),
                                    width="100%",
                                    variant="surface",
                                ),
                                overflow_x="auto",
                                width="100%",
                            ),
                            rx.center(
                                rx.text(
                                    "Nenhuma mensalidade foi gerada. Matrículas anteriores à implantação permanecem sem parcelas.",
                                    color="var(--gray-9)",
                                    text_align="center",
                                ),
                                min_height="120px",
                                width="100%",
                            ),
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
                rx.card(
                    rx.vstack(
                        rx.heading("Histórico de pagamentos", size="4", color="white"),
                        rx.cond(
                            FinanceiroState.has_pagamentos,
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("ALUNO"),
                                            rx.table.column_header_cell("COMPETÊNCIA"),
                                            rx.table.column_header_cell("VALOR"),
                                            rx.table.column_header_cell("FORMA"),
                                            rx.table.column_header_cell("SITUAÇÃO / MOTIVO"),
                                            rx.table.column_header_cell("CORREÇÃO"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            FinanceiroState.pagamentos,
                                            pagamento_row,
                                        )
                                    ),
                                    width="100%",
                                    variant="surface",
                                ),
                                overflow_x="auto",
                                width="100%",
                            ),
                            rx.center(
                                rx.text(
                                    "Nenhum pagamento registrado.",
                                    color="var(--gray-9)",
                                ),
                                min_height="100px",
                                width="100%",
                            ),
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
                spacing="5",
                width="100%",
            ),
        ),
        rx.cond(
            FinanceiroState.error_message != "",
            rx.button(
                rx.icon("refresh-cw", size=16),
                "Tentar novamente",
                on_click=FinanceiroState.load_financeiro,
                loading=FinanceiroState.is_loading,
                variant="soft",
            ),
        ),
        correction_dialog(),
        width="100%",
        spacing="5",
        align="stretch",
    )


def checkin_option(aluno: dict) -> rx.Component:
    return rx.select.item(
        aluno.get("nome", "Aluno"),
        value=aluno.get("id", ""),
    )


def checkin_row(checkin: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(checkin.get("aluno_nome", "Aluno")),
        rx.table.cell(checkin.get("data_hora", "")),
        rx.table.cell(checkin.get("usuario_nome", "Administrador")),
        rx.table.cell(checkin.get("matricula_id", "")),
    )


def checkins_content() -> rx.Component:
    return rx.vstack(
        rx.cond(
            CheckinsState.error_message != "",
            rx.callout(
                CheckinsState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                role="alert",
                width="100%",
            ),
        ),
        rx.cond(
            CheckinsState.success_message != "",
            rx.callout(
                CheckinsState.success_message,
                icon="circle-check",
                color_scheme="green",
                role="status",
                width="100%",
            ),
        ),
        rx.card(
            rx.vstack(
                rx.heading("Registrar check-in", size="4", color="white"),
                rx.text(
                    "A elegibilidade do aluno e da matrícula é validada pelo backend. Mensalidades atrasadas não impedem a entrada.",
                    size="2",
                    color="var(--gray-9)",
                ),
                rx.hstack(
                    rx.select.root(
                        rx.select.trigger(
                            placeholder="Selecione um aluno ativo",
                            width="100%",
                        ),
                        rx.select.content(
                            rx.select.group(
                                rx.foreach(CheckinsState.alunos_ativos, checkin_option)
                            )
                        ),
                        value=CheckinsState.aluno_id,
                        on_change=CheckinsState.set_aluno_id,
                        disabled=(
                            CheckinsState.is_saving
                            | (CheckinsState.alunos_ativos.length() == 0)
                        ),
                    ),
                    rx.button(
                        rx.icon("scan-line", size=16),
                        "Registrar entrada",
                        on_click=CheckinsState.registrar_checkin,
                        loading=CheckinsState.is_saving,
                        disabled=(
                            CheckinsState.is_saving
                            | (CheckinsState.aluno_id == "")
                        ),
                        color_scheme="blue",
                    ),
                    width="100%",
                    flex_wrap="wrap",
                    spacing="3",
                ),
                rx.cond(
                    CheckinsState.alunos_ativos.length() == 0,
                    rx.text(
                        "Não há alunos ativos disponíveis.",
                        size="2",
                        color="var(--gray-9)",
                    ),
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
            CheckinsState.is_loading,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Carregando histórico...", color="var(--gray-9)"),
                    spacing="3",
                    align="center",
                ),
                min_height="220px",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Histórico de check-ins", size="4", color="white"),
                    rx.cond(
                        CheckinsState.has_checkins,
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("ALUNO"),
                                        rx.table.column_header_cell("DATA E HORA"),
                                        rx.table.column_header_cell("REGISTRADO POR"),
                                        rx.table.column_header_cell("MATRÍCULA"),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(CheckinsState.checkins, checkin_row)
                                ),
                                width="100%",
                                variant="surface",
                            ),
                            overflow_x="auto",
                            width="100%",
                        ),
                        rx.center(
                            rx.text(
                                "Nenhum check-in registrado.",
                                color="var(--gray-9)",
                            ),
                            min_height="120px",
                            width="100%",
                        ),
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
        ),
        rx.cond(
            CheckinsState.error_message != "",
            rx.button(
                rx.icon("refresh-cw", size=16),
                "Tentar novamente",
                on_click=CheckinsState.load_checkins,
                loading=CheckinsState.is_loading,
                variant="soft",
            ),
        ),
        width="100%",
        spacing="5",
        align="stretch",
    )


def financeiro_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "financeiro",
        "Gestão financeira",
        "Acompanhe mensalidades e mantenha o histórico de pagamentos.",
        financeiro_content(),
    )


def checkins_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "checkins",
        "Check-ins",
        "Registre entradas e consulte o histórico de frequência.",
        checkins_content(),
    )
