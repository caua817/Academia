from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import reflex as rx

from academia.access_control import begin_admin_check, require_admin
from academia.services.xano_client import XanoAPIError, XanoClient

SAO_PAULO = timezone(timedelta(hours=-3))


def validate_date_range(data_inicio: str, data_fim: str) -> str | None:
    try:
        start = date.fromisoformat(data_inicio)
        end = date.fromisoformat(data_fim)
    except ValueError:
        return "Informe um intervalo de datas válido."
    if start > end:
        return "A data inicial deve ser anterior ou igual à data final."
    return None


def validate_modalidade_fields(nome: str) -> str | None:
    if not nome.strip():
        return "O nome da modalidade é obrigatório."
    return None


def active_student_options(alunos: list[dict]) -> list[dict[str, str]]:
    return [
        {
            "id": str(aluno.get("id", "")),
            "label": str(aluno.get("nome") or "Aluno sem nome"),
        }
        for aluno in alunos
        if str(aluno.get("situacao", "")).casefold() == "ativo"
    ]


def to_api_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SAO_PAULO)
    return (
        parsed.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def validate_sessao_fields(
    modalidade_id: str,
    instrutor_id: str,
    inicio: str,
    termino: str,
    capacidade: str,
    now: datetime | None = None,
) -> str | None:
    try:
        parsed_modality_id = int(modalidade_id)
        parsed_instructor_id = int(instrutor_id)
        parsed_capacity = int(capacidade)
        start = datetime.fromisoformat(inicio)
        end = datetime.fromisoformat(termino)
    except ValueError:
        return "Preencha modalidade, instrutor, horários e capacidade válidos."
    if min(parsed_modality_id, parsed_instructor_id) <= 0:
        return "Informe identificadores válidos para modalidade e instrutor."
    if parsed_capacity <= 0:
        return "A capacidade deve ser maior que zero."
    current_time = now or datetime.now(SAO_PAULO)
    if start.tzinfo is None:
        start = start.replace(tzinfo=SAO_PAULO)
    if end.tzinfo is None:
        end = end.replace(tzinfo=SAO_PAULO)
    if start <= current_time:
        return "A sessão deve começar no futuro."
    if end <= start:
        return "O término deve ser posterior ao início."
    return None


def _session_times(session: dict) -> tuple[datetime | None, datetime | None]:
    try:
        start = datetime.fromisoformat(
            str(session.get("inicio", "")).replace("Z", "+00:00")
        )
        end = datetime.fromisoformat(
            str(session.get("termino", "")).replace("Z", "+00:00")
        )
    except ValueError:
        return None, None
    if start.tzinfo is None:
        start = start.replace(tzinfo=SAO_PAULO)
    if end.tzinfo is None:
        end = end.replace(tzinfo=SAO_PAULO)
    return start, end


class OperacaoState(rx.State):
    modalidades: list[dict] = []
    modalidade_options: list[dict[str, str]] = []
    sessoes: list[dict] = []
    sessao_options: list[dict[str, str]] = []
    reservas: list[dict] = []
    aluno_options: list[dict[str, str]] = []
    resumo_reservas: dict = {}
    relatorio: dict = {}
    report_metrics: list[dict[str, str]] = []
    selected_sessao: dict = {}
    selected_sessao_id: str = ""
    data_inicio: str = ""
    data_fim: str = ""
    is_loading: bool = False
    is_saving: bool = False
    is_changing_status: bool = False
    error_message: str = ""
    success_message: str = ""
    form_error: str = ""

    modalidade_id: int = 0
    modalidade_nome: str = ""
    modalidade_descricao: str = ""
    modalidade_editing: bool = False

    sessao_id: int = 0
    sessao_modalidade_id: str = ""
    sessao_instrutor_id: str = ""
    sessao_inicio: str = ""
    sessao_termino: str = ""
    sessao_capacidade: str = ""
    sessao_local: str = ""
    sessao_editing: bool = False

    reserva_aluno_id: str = ""

    @rx.var
    def has_modalidades(self) -> bool:
        return bool(self.modalidades)

    @rx.var
    def has_sessoes(self) -> bool:
        return bool(self.sessoes)

    @rx.var
    def has_reservas(self) -> bool:
        return bool(self.reservas)

    @rx.var
    def has_report(self) -> bool:
        return bool(self.relatorio)

    @rx.var
    def is_report_empty(self) -> bool:
        return bool(self.relatorio) and all(
            Decimal(str(self.relatorio.get(key, 0) or 0)) == 0
            for key in (
                "matriculas_ativas",
                "pagamentos_quantidade",
                "pagamentos_valor",
                "mensalidades_atrasadas_quantidade",
                "mensalidades_atrasadas_valor",
                "checkins_quantidade",
                "sessoes_quantidade",
                "capacidade_total",
                "reservas_nao_canceladas",
                "ocupacao_percentual",
            )
        )

    def _clear_sensitive_data(self) -> None:
        self.modalidades = []
        self.modalidade_options = []
        self.sessoes = []
        self.sessao_options = []
        self.reservas = []
        self.aluno_options = []
        self.resumo_reservas = {}
        self.relatorio = {}
        self.report_metrics = []
        self.selected_sessao = {}
        self.selected_sessao_id = ""
        self.is_loading = False
        self.is_saving = False
        self.is_changing_status = False
        self.error_message = ""
        self.success_message = ""
        self.form_error = ""
        self._reset_modalidade_form()
        self._reset_sessao_form()
        self.reserva_aluno_id = ""

    def _reset_modalidade_form(self) -> None:
        self.modalidade_id = 0
        self.modalidade_nome = ""
        self.modalidade_descricao = ""
        self.modalidade_editing = False
        self.form_error = ""

    def _reset_sessao_form(self) -> None:
        self.sessao_id = 0
        self.sessao_modalidade_id = ""
        self.sessao_instrutor_id = ""
        self.sessao_inicio = ""
        self.sessao_termino = ""
        self.sessao_capacidade = ""
        self.sessao_local = ""
        self.sessao_editing = False
        self.form_error = ""

    def _api_error_message(self, error: XanoAPIError, action: str) -> str:
        if error.status_code == 401:
            return "Sua sessão expirou. Faça login novamente."
        if error.status_code == 403:
            return "Você não tem permissão para acessar esta área."
        if error.status_code in (400, 409):
            return str(error)
        if error.status_code is not None:
            return f"Não foi possível {action}. A API respondeu com HTTP {error.status_code}."
        return f"Não foi possível {action}. Verifique a conexão e tente novamente."

    async def _admin_token(self, route: str):
        return await require_admin(self, route)

    async def _redirect_if_expired(self, error: XanoAPIError):
        if error.status_code != 401:
            return False
        from academia.session_state import clear_app_session

        await clear_app_session(self)
        return True

    def _date_filters(self) -> tuple[str, str]:
        today = date.today()
        if not self.data_inicio:
            self.data_inicio = today.isoformat()
        if not self.data_fim:
            self.data_fim = (today + timedelta(days=14)).isoformat()
        return self.data_inicio, self.data_fim

    def _prepare_sessions(self) -> None:
        now = datetime.now(timezone.utc)
        prepared = []
        for session in self.sessoes:
            item = dict(session)
            start, _ = _session_times(item)
            can_change = bool(
                item.get("situacao") == "Agendada"
                and start is not None
                and start > now
            )
            item["can_edit"] = can_change
            item["can_cancel"] = can_change
            prepared.append(item)
        self.sessoes = prepared
        self.sessao_options = [
            {
                "id": str(session.get("id", "")),
                "label": (
                    f"{session.get('modalidade_nome', 'Sessão')} · "
                    f"{session.get('inicio', '')} · "
                    f"{session.get('situacao', '')}"
                ),
            }
            for session in self.sessoes
        ]

    def _prepare_modality_options(self) -> None:
        self.modalidade_options = [
            {
                "id": str(modality.get("id", "")),
                "label": str(modality.get("nome") or "Modalidade"),
            }
            for modality in self.modalidades
            if str(modality.get("situacao", "")).casefold() == "ativo"
        ]

    def _prepare_report_metrics(self) -> None:
        metric_labels = (
            ("Matrículas ativas", "matriculas_ativas", False),
            ("Pagamentos", "pagamentos_quantidade", False),
            ("Valor pago", "pagamentos_valor", True),
            (
                "Mensalidades em atraso",
                "mensalidades_atrasadas_quantidade",
                False,
            ),
            ("Valor em atraso", "mensalidades_atrasadas_valor", True),
            ("Check-ins", "checkins_quantidade", False),
            ("Sessões", "sessoes_quantidade", False),
            ("Capacidade total", "capacidade_total", False),
            ("Reservas não canceladas", "reservas_nao_canceladas", False),
            ("Ocupação", "ocupacao_percentual", False),
        )
        self.report_metrics = []
        for label, key, currency in metric_labels:
            value = Decimal(str(self.relatorio.get(key, 0) or 0))
            formatted = f"{value:.2f}" if currency else f"{value:g}"
            if currency:
                formatted = f"R$ {formatted.replace('.', ',')}"
            elif key == "ocupacao_percentual":
                formatted = f"{formatted}%"
            self.report_metrics.append({"label": label, "value": formatted})

    @rx.event
    async def load_modalidades(self):
        await begin_admin_check(self)
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        yield
        token, should_redirect = await self._admin_token("modalidades")
        if not token:
            self.modalidades = []
            self.is_loading = False
            if should_redirect:
                yield rx.redirect("/login")
            return
        try:
            self.modalidades = XanoClient.get_modalidades(token)
            self._prepare_modality_options()
        except XanoAPIError as error:
            self.modalidades = []
            self.modalidade_options = []
            self.error_message = self._api_error_message(
                error,
                "carregar modalidades",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_loading = False

    @rx.event
    def set_modalidade_nome(self, value: str):
        self.modalidade_nome = value

    @rx.event
    def set_modalidade_descricao(self, value: str):
        self.modalidade_descricao = value

    @rx.event
    def edit_modalidade(self, modalidade_id: int):
        modalidade = next(
            (
                item
                for item in self.modalidades
                if int(item.get("id", 0)) == modalidade_id
            ),
            None,
        )
        if modalidade is None:
            self.error_message = "A modalidade não está mais disponível."
            return
        self.modalidade_id = modalidade_id
        self.modalidade_nome = str(modalidade.get("nome") or "")
        self.modalidade_descricao = str(modalidade.get("descricao") or "")
        self.modalidade_editing = True
        self.form_error = ""
        self.error_message = ""
        self.success_message = ""

    @rx.event
    def cancel_modalidade_edit(self):
        self._reset_modalidade_form()

    @rx.event
    async def save_modalidade(self):
        self.error_message = ""
        self.success_message = ""
        self.form_error = validate_modalidade_fields(self.modalidade_nome) or ""
        if self.form_error:
            return
        token, should_redirect = await self._admin_token("modalidades")
        if not token:
            if should_redirect:
                yield rx.redirect("/login")
            return
        self.is_saving = True
        yield
        payload = {
            "nome": self.modalidade_nome.strip(),
            "descricao": self.modalidade_descricao.strip() or None,
        }
        try:
            if self.modalidade_editing:
                XanoClient.update_modalidade(token, self.modalidade_id, payload)
                action = "Modalidade atualizada com sucesso."
            else:
                XanoClient.create_modalidade(token, payload)
                action = "Modalidade cadastrada com sucesso."
            self.modalidades = XanoClient.get_modalidades(token)
            self._reset_modalidade_form()
            self.success_message = action
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "salvar a modalidade",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_saving = False

    @rx.event
    async def deactivate_modalidade(self, modalidade_id: int):
        token, should_redirect = await self._admin_token("modalidades")
        if not token:
            if should_redirect:
                yield rx.redirect("/login")
            return
        self.is_changing_status = True
        self.error_message = ""
        self.success_message = ""
        yield
        try:
            XanoClient.deactivate_modalidade(token, modalidade_id)
            self.modalidades = XanoClient.get_modalidades(token)
            self.success_message = "Modalidade desativada sem apagar o histórico."
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "desativar a modalidade",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_changing_status = False

    @rx.event
    def set_data_inicio(self, value: str):
        self.data_inicio = value

    @rx.event
    def set_data_fim(self, value: str):
        self.data_fim = value

    @rx.event
    def set_sessao_modalidade_id(self, value: str):
        self.sessao_modalidade_id = value

    @rx.event
    def set_sessao_instrutor_id(self, value: str):
        self.sessao_instrutor_id = value

    @rx.event
    def set_sessao_inicio(self, value: str):
        self.sessao_inicio = value

    @rx.event
    def set_sessao_termino(self, value: str):
        self.sessao_termino = value

    @rx.event
    def set_sessao_capacidade(self, value: str):
        self.sessao_capacidade = value

    @rx.event
    def set_sessao_local(self, value: str):
        self.sessao_local = value

    @rx.event
    async def load_sessoes(self):
        await begin_admin_check(self)
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        yield
        token, should_redirect = await self._admin_token("sessoes")
        if not token:
            self.sessoes = []
            self.is_loading = False
            if should_redirect:
                yield rx.redirect("/login")
            return
        error = validate_date_range(*self._date_filters())
        if error:
            self.sessoes = []
            self.error_message = error
            self.is_loading = False
            return
        try:
            start, end = self._date_filters()
            self.modalidades = XanoClient.get_modalidades(token)
            self._prepare_modality_options()
            self.sessoes = XanoClient.get_sessoes(token, start, end)
            self._prepare_sessions()
        except XanoAPIError as api_error:
            self.sessoes = []
            self.error_message = self._api_error_message(
                api_error,
                "carregar sessões",
            )
            if await self._redirect_if_expired(api_error):
                yield rx.redirect("/login")
        finally:
            self.is_loading = False

    @rx.event
    def edit_sessao(self, sessao_id: int):
        session = next(
            (
                item
                for item in self.sessoes
                if int(item.get("id", 0)) == sessao_id
            ),
            None,
        )
        if session is None:
            self.error_message = "A sessão não está mais disponível."
            return
        self.sessao_id = sessao_id
        self.sessao_modalidade_id = str(session.get("modalidade_id") or "")
        self.sessao_instrutor_id = str(session.get("instrutor_id") or "")
        start, end = _session_times(session)
        if start is not None:
            self.sessao_inicio = start.astimezone(SAO_PAULO).strftime(
                "%Y-%m-%dT%H:%M"
            )
        if end is not None:
            self.sessao_termino = end.astimezone(SAO_PAULO).strftime(
                "%Y-%m-%dT%H:%M"
            )
        self.sessao_capacidade = str(session.get("capacidade") or "")
        self.sessao_local = str(session.get("local") or "")
        self.sessao_editing = True
        self.error_message = ""
        self.success_message = ""
        self.form_error = ""

    @rx.event
    def cancel_sessao_edit(self):
        self._reset_sessao_form()

    @rx.event
    async def save_sessao(self):
        self.error_message = ""
        self.success_message = ""
        self.form_error = validate_sessao_fields(
            self.sessao_modalidade_id,
            self.sessao_instrutor_id,
            self.sessao_inicio,
            self.sessao_termino,
            self.sessao_capacidade,
        ) or ""
        if self.form_error:
            return
        token, should_redirect = await self._admin_token("sessoes")
        if not token:
            if should_redirect:
                yield rx.redirect("/login")
            return
        self.is_saving = True
        yield
        payload = {
            "modalidade_id": int(self.sessao_modalidade_id),
            "instrutor_id": int(self.sessao_instrutor_id),
            "inicio": to_api_timestamp(self.sessao_inicio),
            "termino": to_api_timestamp(self.sessao_termino),
            "capacidade": int(self.sessao_capacidade),
            "local": self.sessao_local.strip() or None,
        }
        try:
            if self.sessao_editing:
                XanoClient.update_sessao(token, self.sessao_id, payload)
                message = "Sessão atualizada com sucesso."
            else:
                XanoClient.create_sessao(token, payload)
                message = "Sessão criada com sucesso."
            start, end = self._date_filters()
            self.modalidades = XanoClient.get_modalidades(token)
            self._prepare_modality_options()
            self.sessoes = XanoClient.get_sessoes(token, start, end)
            self._prepare_sessions()
            self._reset_sessao_form()
            self.success_message = message
        except XanoAPIError as error:
            self.error_message = self._api_error_message(error, "salvar a sessão")
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_saving = False

    @rx.event
    async def cancel_sessao(self, sessao_id: int):
        token, should_redirect = await self._admin_token("sessoes")
        if not token:
            if should_redirect:
                yield rx.redirect("/login")
            return
        self.is_changing_status = True
        self.error_message = ""
        self.success_message = ""
        yield
        try:
            XanoClient.cancel_sessao(token, sessao_id)
            start, end = self._date_filters()
            self.modalidades = XanoClient.get_modalidades(token)
            self._prepare_modality_options()
            self.sessoes = XanoClient.get_sessoes(token, start, end)
            self._prepare_sessions()
            self.success_message = "Sessão cancelada; o histórico foi preservado."
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "cancelar a sessão",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_changing_status = False

    async def _load_reservas_summary(self, token: str, sessao_id: int) -> None:
        self.resumo_reservas = XanoClient.get_reservas(token, sessao_id)
        self.reservas = self.resumo_reservas["reservas"]
        self.selected_sessao = next(
            (
                session
                for session in self.sessoes
                if int(session.get("id", 0)) == sessao_id
            ),
            {},
        )
        self.selected_sessao = dict(self.selected_sessao)
        start, end = _session_times(self.selected_sessao)
        now = datetime.now(timezone.utc)
        session_is_scheduled = (
            self.selected_sessao.get("situacao") == "Agendada"
        )
        available_spaces = int(
            self.resumo_reservas.get("vagas_disponiveis", 0) or 0
        )
        self.selected_sessao["can_reserve"] = bool(
            session_is_scheduled and start is not None and start > now
            and available_spaces > 0
        )
        for reservation in self.reservas:
            reservation["can_cancel"] = bool(
                session_is_scheduled
                and reservation.get("situacao") == "Confirmada"
                and start is not None
                and start > now
            )
            reservation["can_set_result"] = bool(
                session_is_scheduled
                and reservation.get("situacao") == "Confirmada"
                and end is not None
                and end <= now
            )

    @rx.event
    async def load_reservas_page(self):
        await begin_admin_check(self)
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        yield
        token, should_redirect = await self._admin_token("reservas")
        if not token:
            self.sessoes = []
            self.reservas = []
            self.resumo_reservas = {}
            self.is_loading = False
            if should_redirect:
                yield rx.redirect("/login")
            return
        error = validate_date_range(*self._date_filters())
        if error:
            self.error_message = error
            self.is_loading = False
            return
        try:
            start, end = self._date_filters()
            self.modalidades = XanoClient.get_modalidades(token)
            self._prepare_modality_options()
            self.sessoes = XanoClient.get_sessoes(token, start, end)
            self.aluno_options = active_student_options(
                XanoClient.get_alunos(token)
            )
            self._prepare_sessions()
            available_ids = [
                str(session["id"])
                for session in self.sessoes
            ]
            if self.selected_sessao_id not in available_ids:
                self.selected_sessao_id = available_ids[0] if available_ids else ""
            if self.selected_sessao_id:
                await self._load_reservas_summary(
                    token,
                    int(self.selected_sessao_id),
                )
            else:
                self.reservas = []
                self.resumo_reservas = {}
                self.selected_sessao = {}
        except XanoAPIError as error:
            self.sessoes = []
            self.aluno_options = []
            self.reservas = []
            self.resumo_reservas = {}
            self.error_message = self._api_error_message(
                error,
                "carregar reservas",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_loading = False

    @rx.event
    async def select_sessao(self, value: str):
        self.selected_sessao_id = value
        self.error_message = ""
        self.success_message = ""
        if not value:
            self.selected_sessao = {}
            self.reservas = []
            self.resumo_reservas = {}
            return
        token, should_redirect = await self._admin_token("reservas")
        if not token:
            if should_redirect:
                yield rx.redirect("/login")
            return
        self.is_loading = True
        yield
        try:
            await self._load_reservas_summary(token, int(value))
        except XanoAPIError as error:
            self.reservas = []
            self.resumo_reservas = {}
            self.error_message = self._api_error_message(
                error,
                "carregar reservas",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_loading = False

    @rx.event
    def set_reserva_aluno_id(self, value: str):
        self.reserva_aluno_id = value

    @rx.event
    async def create_reserva(self):
        try:
            aluno_id = int(self.reserva_aluno_id)
        except ValueError:
            self.form_error = "Informe um identificador válido de aluno."
            return
        if aluno_id <= 0 or not self.selected_sessao_id:
            self.form_error = "Selecione uma sessão e informe o aluno."
            return
        if not self.selected_sessao.get("can_reserve", False):
            self.form_error = "A sessão não está disponível para novas reservas."
            return
        token, should_redirect = await self._admin_token("reservas")
        if not token:
            if should_redirect:
                yield rx.redirect("/login")
            return
        self.form_error = ""
        self.error_message = ""
        self.success_message = ""
        self.is_saving = True
        yield
        try:
            XanoClient.create_reserva(
                token,
                {
                    "sessao_aula_id": int(self.selected_sessao_id),
                    "aluno_id": aluno_id,
                },
            )
            await self._load_reservas_summary(
                token,
                int(self.selected_sessao_id),
            )
            self.reserva_aluno_id = ""
            self.success_message = "Reserva confirmada com sucesso."
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "criar a reserva",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_saving = False

    @rx.event
    async def cancel_reserva(self, reserva_id: int):
        token, should_redirect = await self._admin_token("reservas")
        if not token:
            if should_redirect:
                yield rx.redirect("/login")
            return
        self.is_changing_status = True
        self.error_message = ""
        self.success_message = ""
        yield
        try:
            XanoClient.cancel_reserva(token, reserva_id)
            await self._load_reservas_summary(
                token,
                int(self.selected_sessao_id),
            )
            self.success_message = "Reserva cancelada; a vaga foi liberada."
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "cancelar a reserva",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_changing_status = False

    @rx.event
    async def set_reserva_resultado(self, reserva_id: int, resultado: str):
        if resultado not in {"Presente", "Falta"}:
            self.error_message = "Selecione um resultado válido."
            return
        token, should_redirect = await self._admin_token("reservas")
        if not token:
            if should_redirect:
                yield rx.redirect("/login")
            return
        self.is_changing_status = True
        self.error_message = ""
        self.success_message = ""
        yield
        try:
            XanoClient.set_reserva_resultado(token, reserva_id, resultado)
            await self._load_reservas_summary(
                token,
                int(self.selected_sessao_id),
            )
            self.success_message = "Resultado da reserva registrado."
        except XanoAPIError as error:
            self.error_message = self._api_error_message(
                error,
                "registrar presença ou falta",
            )
            if await self._redirect_if_expired(error):
                yield rx.redirect("/login")
        finally:
            self.is_changing_status = False

    @rx.event
    async def load_relatorios(self):
        await begin_admin_check(self)
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        self.relatorio = {}
        self.report_metrics = []
        yield
        token, should_redirect = await self._admin_token("relatorios")
        if not token:
            self.relatorio = {}
            self.is_loading = False
            if should_redirect:
                yield rx.redirect("/login")
            return
        error = validate_date_range(*self._date_filters())
        if error:
            self.relatorio = {}
            self.error_message = error
            self.is_loading = False
            return
        try:
            start, end = self._date_filters()
            self.relatorio = XanoClient.get_relatorio_operacao(
                token,
                start,
                end,
            )
            self._prepare_report_metrics()
        except XanoAPIError as api_error:
            self.relatorio = {}
            self.error_message = self._api_error_message(
                api_error,
                "carregar os relatórios",
            )
            if await self._redirect_if_expired(api_error):
                yield rx.redirect("/login")
        finally:
            self.is_loading = False


def _message_area() -> rx.Component:
    return rx.vstack(
        rx.cond(
            OperacaoState.error_message != "",
            rx.callout(
                OperacaoState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                width="100%",
                role="alert",
            ),
        ),
        rx.cond(
            OperacaoState.success_message != "",
            rx.callout(
                OperacaoState.success_message,
                icon="circle-check",
                color_scheme="green",
                width="100%",
                role="status",
            ),
        ),
        spacing="3",
        width="100%",
    )


def _loading_or_empty(
    loading_message: str,
    has_items: rx.Var,
    list_content: rx.Component,
    empty_message: str,
) -> rx.Component:
    return rx.cond(
        OperacaoState.error_message != "",
        rx.fragment(),
        rx.cond(
            OperacaoState.is_loading,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text(loading_message, color="var(--gray-9)"),
                    align="center",
                    spacing="3",
                ),
                min_height="180px",
                width="100%",
            ),
            rx.cond(
                has_items,
                list_content,
                rx.center(
                    rx.text(empty_message, color="var(--gray-9)"),
                    min_height="150px",
                    width="100%",
                ),
            ),
        ),
    )


def _modalidade_row(modalidade: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(modalidade.get("nome", "—")),
        rx.table.cell(
            rx.cond(
                modalidade.get("descricao") != None,
                modalidade.get("descricao"),
                "Sem descrição",
            )
        ),
        rx.table.cell(
            rx.badge(
                modalidade.get("situacao", "—"),
                color_scheme=rx.cond(
                    modalidade.get("situacao") == "Ativo",
                    "green",
                    "gray",
                ),
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    "Editar",
                    size="1",
                    variant="soft",
                    on_click=OperacaoState.edit_modalidade(modalidade.get("id")),
                ),
                rx.cond(
                    modalidade.get("situacao") == "Ativo",
                    rx.button(
                        "Desativar",
                        size="1",
                        color_scheme="red",
                        variant="soft",
                        loading=OperacaoState.is_changing_status,
                        on_click=OperacaoState.deactivate_modalidade(
                            modalidade.get("id")
                        ),
                    ),
                ),
                spacing="2",
            )
        ),
    )


def _modalidades_table() -> rx.Component:
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("MODALIDADE"),
                    rx.table.column_header_cell("DESCRIÇÃO"),
                    rx.table.column_header_cell("SITUAÇÃO"),
                    rx.table.column_header_cell("AÇÕES"),
                )
            ),
            rx.table.body(rx.foreach(OperacaoState.modalidades, _modalidade_row)),
            width="100%",
            variant="surface",
        ),
        overflow_x="auto",
        width="100%",
    )


def modalidades_content() -> rx.Component:
    return rx.vstack(
        _message_area(),
        rx.card(
            rx.vstack(
                rx.heading(
                    rx.cond(
                        OperacaoState.modalidade_editing,
                        "Editar modalidade",
                        "Cadastrar modalidade",
                    ),
                    size="4",
                ),
                rx.input(
                    placeholder="Nome da modalidade",
                    value=OperacaoState.modalidade_nome,
                    on_change=OperacaoState.set_modalidade_nome,
                    width="100%",
                ),
                rx.text_area(
                    placeholder="Descrição opcional",
                    value=OperacaoState.modalidade_descricao,
                    on_change=OperacaoState.set_modalidade_descricao,
                    width="100%",
                ),
                rx.cond(
                    OperacaoState.form_error != "",
                    rx.callout(
                        OperacaoState.form_error,
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.hstack(
                    rx.button(
                        rx.cond(
                            OperacaoState.modalidade_editing,
                            "Salvar alterações",
                            "Cadastrar",
                        ),
                        loading=OperacaoState.is_saving,
                        on_click=OperacaoState.save_modalidade,
                    ),
                    rx.cond(
                        OperacaoState.modalidade_editing,
                        rx.button(
                            "Cancelar edição",
                            variant="soft",
                            on_click=OperacaoState.cancel_modalidade_edit,
                        ),
                    ),
                    spacing="3",
                ),
                align="stretch",
                spacing="3",
                width="100%",
            ),
            width="100%",
            background="#15171d",
        ),
        rx.card(
            rx.vstack(
                rx.heading("Modalidades cadastradas", size="4"),
                _loading_or_empty(
                    "Carregando modalidades...",
                    OperacaoState.has_modalidades,
                    _modalidades_table(),
                    "Nenhuma modalidade cadastrada.",
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            width="100%",
            background="#15171d",
        ),
        spacing="5",
        width="100%",
    )


def _session_row(session: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(session.get("modalidade_nome", "Modalidade"), size="4"),
                    rx.text(
                        f"Instrutor: {session.get('instrutor_nome', '—')}",
                        color="var(--gray-9)",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(session.get("situacao", "—")),
                width="100%",
                align="start",
            ),
            rx.text(
                f"Início: {session.get('inicio', '—')} · "
                f"Término: {session.get('termino', '—')}"
            ),
            rx.text(
                f"Ocupação: {session.get('ocupacao', 0)} / "
                f"{session.get('capacidade', 0)} "
                f"({session.get('percentual_ocupacao', 0)}%)"
            ),
            rx.hstack(
                rx.text("Local:"),
                rx.text(
                    rx.cond(
                        session.get("local") != None,
                        session.get("local"),
                        "Não informado",
                    )
                ),
                spacing="1",
            ),
            rx.hstack(
                rx.cond(
                    session.get("can_edit", False),
                    rx.button(
                        "Editar",
                        size="1",
                        variant="soft",
                        on_click=OperacaoState.edit_sessao(session.get("id")),
                    ),
                ),
                rx.cond(
                    session.get("can_cancel", False),
                    rx.button(
                        "Cancelar sessão",
                        size="1",
                        variant="soft",
                        color_scheme="red",
                        loading=OperacaoState.is_changing_status,
                        on_click=OperacaoState.cancel_sessao(session.get("id")),
                    ),
                ),
                spacing="2",
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        width="100%",
        background="#15171d",
    )


def _sessions_list() -> rx.Component:
    return rx.vstack(
        rx.foreach(OperacaoState.sessoes, _session_row),
        align="stretch",
        spacing="3",
        width="100%",
    )


def sessoes_content() -> rx.Component:
    return rx.vstack(
        _message_area(),
        rx.card(
            rx.vstack(
                rx.heading(
                    rx.cond(
                        OperacaoState.sessao_editing,
                        "Editar sessão",
                        "Agendar sessão",
                    ),
                    size="4",
                ),
                rx.text(
                    "Selecione uma modalidade e informe o ID do instrutor. "
                    "O Xano valida situação, agenda e capacidade."
                ),
                rx.select.root(
                    rx.select.trigger(placeholder="Selecione uma modalidade"),
                    rx.select.content(
                        rx.foreach(
                            OperacaoState.modalidade_options,
                            lambda modality: rx.select.item(
                                modality.get("label", "Modalidade"),
                                value=modality.get("id", ""),
                            ),
                        )
                    ),
                    value=OperacaoState.sessao_modalidade_id,
                    on_change=OperacaoState.set_sessao_modalidade_id,
                    width="100%",
                ),
                rx.input(
                    placeholder="ID do instrutor",
                    type="number",
                    value=OperacaoState.sessao_instrutor_id,
                    on_change=OperacaoState.set_sessao_instrutor_id,
                ),
                rx.input(
                    type="datetime-local",
                    value=OperacaoState.sessao_inicio,
                    on_change=OperacaoState.set_sessao_inicio,
                ),
                rx.input(
                    type="datetime-local",
                    value=OperacaoState.sessao_termino,
                    on_change=OperacaoState.set_sessao_termino,
                ),
                rx.input(
                    placeholder="Capacidade",
                    type="number",
                    value=OperacaoState.sessao_capacidade,
                    on_change=OperacaoState.set_sessao_capacidade,
                ),
                rx.input(
                    placeholder="Local (opcional)",
                    value=OperacaoState.sessao_local,
                    on_change=OperacaoState.set_sessao_local,
                ),
                rx.cond(
                    OperacaoState.form_error != "",
                    rx.callout(
                        OperacaoState.form_error,
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.hstack(
                    rx.button(
                        rx.cond(
                            OperacaoState.sessao_editing,
                            "Salvar alterações",
                            "Agendar sessão",
                        ),
                        loading=OperacaoState.is_saving,
                        on_click=OperacaoState.save_sessao,
                    ),
                    rx.cond(
                        OperacaoState.sessao_editing,
                        rx.button(
                            "Cancelar edição",
                            variant="soft",
                            on_click=OperacaoState.cancel_sessao_edit,
                        ),
                    ),
                    spacing="3",
                ),
                align="stretch",
                spacing="3",
                width="100%",
            ),
            width="100%",
            background="#15171d",
        ),
        rx.card(
            rx.vstack(
                rx.heading("Período da agenda", size="4"),
                rx.hstack(
                    rx.input(
                        type="date",
                        value=OperacaoState.data_inicio,
                        on_change=OperacaoState.set_data_inicio,
                    ),
                    rx.input(
                        type="date",
                        value=OperacaoState.data_fim,
                        on_change=OperacaoState.set_data_fim,
                    ),
                    rx.button(
                        "Buscar sessões",
                        on_click=OperacaoState.load_sessoes,
                        loading=OperacaoState.is_loading,
                    ),
                    flex_wrap="wrap",
                    width="100%",
                ),
                _loading_or_empty(
                    "Carregando agenda...",
                    OperacaoState.has_sessoes,
                    _sessions_list(),
                    "Não existem sessões no período selecionado.",
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            width="100%",
            background="#15171d",
        ),
        spacing="5",
        width="100%",
    )


def _reservation_row(reservation: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(reservation.get("aluno_nome", "Aluno")),
        rx.table.cell(reservation.get("situacao", "—")),
        rx.table.cell(reservation.get("reservado_em", "—")),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    reservation.get("can_cancel", False),
                    rx.button(
                        "Cancelar",
                        size="1",
                        color_scheme="red",
                        variant="soft",
                        loading=OperacaoState.is_changing_status,
                        on_click=OperacaoState.cancel_reserva(
                            reservation.get("id")
                        ),
                    ),
                ),
                rx.cond(
                    reservation.get("can_set_result", False),
                    rx.button(
                        "Presente",
                        size="1",
                        color_scheme="green",
                        variant="soft",
                        loading=OperacaoState.is_changing_status,
                        on_click=OperacaoState.set_reserva_resultado(
                            reservation.get("id"),
                            "Presente",
                        ),
                    ),
                ),
                rx.cond(
                    reservation.get("can_set_result", False),
                    rx.button(
                        "Falta",
                        size="1",
                        color_scheme="amber",
                        variant="soft",
                        loading=OperacaoState.is_changing_status,
                        on_click=OperacaoState.set_reserva_resultado(
                            reservation.get("id"),
                            "Falta",
                        ),
                    ),
                ),
                spacing="2",
                flex_wrap="wrap",
            )
        ),
    )


def _reservations_table() -> rx.Component:
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("ALUNO"),
                    rx.table.column_header_cell("SITUAÇÃO"),
                    rx.table.column_header_cell("RESERVADO EM"),
                    rx.table.column_header_cell("AÇÕES"),
                )
            ),
            rx.table.body(rx.foreach(OperacaoState.reservas, _reservation_row)),
            width="100%",
            variant="surface",
        ),
        overflow_x="auto",
        width="100%",
    )


def reservas_content() -> rx.Component:
    return rx.vstack(
        _message_area(),
        rx.card(
            rx.vstack(
                rx.heading("Reservas por sessão", size="4"),
                rx.hstack(
                    rx.input(
                        type="date",
                        value=OperacaoState.data_inicio,
                        on_change=OperacaoState.set_data_inicio,
                    ),
                    rx.input(
                        type="date",
                        value=OperacaoState.data_fim,
                        on_change=OperacaoState.set_data_fim,
                    ),
                    rx.button(
                        "Atualizar sessões",
                        on_click=OperacaoState.load_reservas_page,
                        loading=OperacaoState.is_loading,
                    ),
                    flex_wrap="wrap",
                    width="100%",
                ),
                rx.select.root(
                    rx.select.trigger(placeholder="Selecione uma sessão"),
                    rx.select.content(
                        rx.foreach(
                            OperacaoState.sessao_options,
                            lambda session: rx.select.item(
                                session.get("label", "Sessão"),
                                value=session.get("id", ""),
                            ),
                        )
                    ),
                    value=OperacaoState.selected_sessao_id,
                    on_change=OperacaoState.select_sessao,
                    width="100%",
                ),
                rx.cond(
                    OperacaoState.selected_sessao_id != "",
                    rx.vstack(
                        rx.text(
                            "Ocupação: "
                            f"{OperacaoState.resumo_reservas.get('ocupacao', 0)} / "
                            f"{OperacaoState.resumo_reservas.get('capacidade', 0)} · "
                            f"Vagas disponíveis: "
                            f"{OperacaoState.resumo_reservas.get('vagas_disponiveis', 0)}"
                        ),
                        rx.cond(
                            OperacaoState.selected_sessao.get(
                                "can_reserve",
                                False,
                            ),
                            rx.hstack(
                            rx.select.root(
                                rx.select.trigger(
                                    placeholder="Selecione um aluno ativo"
                                ),
                                rx.select.content(
                                    rx.foreach(
                                        OperacaoState.aluno_options,
                                        lambda student: rx.select.item(
                                            student.get("label", "Aluno"),
                                            value=student.get("id", ""),
                                        ),
                                    )
                                ),
                                value=OperacaoState.reserva_aluno_id,
                                on_change=OperacaoState.set_reserva_aluno_id,
                                width="100%",
                            ),
                            rx.button(
                                "Reservar vaga",
                                loading=OperacaoState.is_saving,
                                on_click=OperacaoState.create_reserva,
                            ),
                            width="100%",
                            flex_wrap="wrap",
                            ),
                            rx.text(
                                "Esta sessão não aceita novas reservas.",
                                color="var(--gray-9)",
                            ),
                        ),
                        rx.cond(
                            OperacaoState.form_error != "",
                            rx.callout(
                                OperacaoState.form_error,
                                color_scheme="red",
                                role="alert",
                            ),
                        ),
                        _loading_or_empty(
                            "Carregando reservas...",
                            OperacaoState.has_reservas,
                            _reservations_table(),
                            "Nenhuma reserva para esta sessão.",
                        ),
                        align="stretch",
                        spacing="4",
                        width="100%",
                    ),
                    rx.text(
                        "Selecione uma sessão para consultar o histórico e a ocupação.",
                        color="var(--gray-9)",
                    ),
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            width="100%",
            background="#15171d",
        ),
        spacing="5",
        width="100%",
    )


def _report_metric(metric: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(metric.get("label", ""), color="var(--gray-9)", size="2"),
            rx.heading(metric.get("value", "0"), size="6"),
            spacing="2",
            align="start",
        ),
        width="100%",
        background="#15171d",
    )


def relatorios_content() -> rx.Component:
    return rx.vstack(
        _message_area(),
        rx.card(
            rx.vstack(
                rx.heading("Relatório operacional", size="4"),
                rx.text(
                    "A inadimplência considera mensalidades vencidas e não pagas "
                    "até a data final."
                ),
                rx.hstack(
                    rx.input(
                        type="date",
                        value=OperacaoState.data_inicio,
                        on_change=OperacaoState.set_data_inicio,
                    ),
                    rx.input(
                        type="date",
                        value=OperacaoState.data_fim,
                        on_change=OperacaoState.set_data_fim,
                    ),
                    rx.button(
                        "Gerar relatório",
                        on_click=OperacaoState.load_relatorios,
                        loading=OperacaoState.is_loading,
                    ),
                    flex_wrap="wrap",
                    width="100%",
                ),
                align="stretch",
                spacing="4",
                width="100%",
            ),
            width="100%",
            background="#15171d",
        ),
        rx.cond(
            OperacaoState.is_loading,
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Carregando relatório...", color="var(--gray-9)"),
                    align="center",
                    spacing="3",
                ),
                min_height="160px",
                width="100%",
            ),
            rx.cond(
                OperacaoState.error_message != "",
                rx.fragment(),
                rx.cond(
                    OperacaoState.has_report,
                    rx.vstack(
                        rx.cond(
                            OperacaoState.is_report_empty,
                            rx.callout(
                                "Não há atividade registrada neste período. "
                                "As métricas abaixo estão zeradas.",
                                icon="info",
                                color_scheme="blue",
                                width="100%",
                            ),
                        ),
                        rx.grid(
                            rx.foreach(
                                OperacaoState.report_metrics,
                                _report_metric,
                            ),
                            columns="repeat(auto-fit, minmax(210px, 1fr))",
                            spacing="4",
                            width="100%",
                        ),
                        align="stretch",
                        spacing="4",
                        width="100%",
                    ),
                    rx.center(
                        rx.text(
                            "Selecione um período e gere o relatório.",
                            color="var(--gray-9)",
                        ),
                        min_height="120px",
                        width="100%",
                    ),
                ),
            ),
        ),
        spacing="5",
        width="100%",
    )


def modalidades_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "modalidades",
        "Gestão de modalidades",
        "Cadastre atividades e preserve o histórico operacional.",
        modalidades_content(),
    )


def sessoes_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "sessoes",
        "Agenda de aulas",
        "Organize sessões, instrutores, horários e capacidade.",
        sessoes_content(),
    )


def reservas_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "reservas",
        "Gestão de reservas",
        "Acompanhe ocupação, cancelamentos e comparecimento.",
        reservas_content(),
    )


def relatorios_page() -> rx.Component:
    from academia.academia import app_shell

    return app_shell(
        "relatorios",
        "Relatórios gerenciais",
        "Consulte métricas agregadas da operação no período.",
        relatorios_content(),
    )
