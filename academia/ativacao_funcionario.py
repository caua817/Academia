from typing import Any
from urllib.parse import parse_qsl
from urllib.parse import unquote

import reflex as rx

from academia.services.auth_client import (
    AuthenticationAPIError,
    AuthenticationClient,
    validate_new_password,
)

_PASSWORD_FIELD_ID = "employee-invitation-password"
_PASSWORD_CONFIRMATION_FIELD_ID = "employee-invitation-password-confirmation"


def parse_invitation_fragment(fragment: str) -> tuple[str, str] | None:
    if not fragment:
        return None
    try:
        if "%" in unquote(fragment, errors="strict"):
            return None
        values = parse_qsl(fragment, keep_blank_values=True, strict_parsing=True)
    except (UnicodeDecodeError, ValueError):
        return None

    if len(values) != 2 or {key for key, _ in values} != {"email", "token"}:
        return None

    fields = dict(values)
    email = fields["email"].strip().lower()
    token = fields["token"].strip()
    if not email or not token or "@" not in email:
        return None
    return email, token


def validate_invitation_password(
    password: str, password_confirmation: str
) -> str | None:
    return validate_new_password(password, password_confirmation)


class EmployeeInvitationActivationState(rx.State):
    has_valid_invitation: bool = False
    error_message: str = ""
    is_loading: bool = False

    _email: str = ""
    _token: str = ""
    _activation_succeeded: bool = False

    @rx.event
    def load_invitation(self):
        self._email = ""
        self._token = ""
        self._activation_succeeded = False
        invitation = parse_invitation_fragment(self.router.url.fragment)
        if invitation is None:
            self.has_valid_invitation = False
            self.error_message = (
                "Este link de convite está incompleto ou inválido. "
                "Solicite um novo convite ao administrador."
            )
        else:
            self._email, self._token = invitation
            self.has_valid_invitation = True
            self.error_message = ""

        return rx.call_script(
            "window.history.replaceState(null, document.title, "
            "window.location.pathname + window.location.search);"
        )

    @rx.event
    def activate(self, form_data: dict[str, Any]):
        if self.is_loading or self._activation_succeeded:
            return

        password = form_data.get("password", "")
        password_confirmation = form_data.get("password_confirmation", "")
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            if not self.has_valid_invitation or not self._email or not self._token:
                self.error_message = (
                    "Este link de convite não é válido. "
                    "Solicite um novo convite ao administrador."
                )
            else:
                validation_error = validate_invitation_password(
                    password, password_confirmation
                )
                if validation_error:
                    self.error_message = validation_error
                else:
                    try:
                        AuthenticationClient.accept_employee_invitation(
                            self._email,
                            self._token,
                            password,
                            password_confirmation,
                        )
                    except AuthenticationAPIError as error:
                        if error.status_code in (401, 403, 404, 409, 410):
                            self._token = ""
                            self._email = ""
                            self.has_valid_invitation = False
                            self.error_message = (
                                "O convite não é mais válido. "
                                "Solicite um novo convite ao administrador."
                            )
                        else:
                            self.error_message = (
                                "Não foi possível ativar a conta. "
                                "Tente novamente."
                            )
                    else:
                        self._activation_succeeded = True
                        self.has_valid_invitation = False
                        self._email = ""
                        self._token = ""
        finally:
            self.is_loading = False
            yield rx.set_value(_PASSWORD_FIELD_ID, "")
            yield rx.set_value(_PASSWORD_CONFIRMATION_FIELD_ID, "")

        if self._activation_succeeded:
            yield rx.redirect("/login")


def employee_invitation_activation_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                rx.icon("dumbbell", size=28, color="var(--blue-9)"),
                rx.heading(
                    "Ativar conta de funcionário",
                    size="6",
                    color="white",
                    text_align="center",
                ),
                rx.text(
                    "Defina uma senha para acessar o sistema.",
                    color="var(--gray-9)",
                    text_align="center",
                ),
                rx.cond(
                    EmployeeInvitationActivationState.error_message != "",
                    rx.callout(
                        EmployeeInvitationActivationState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.cond(
                    EmployeeInvitationActivationState.has_valid_invitation,
                    rx.form.root(
                        rx.vstack(
                            rx.vstack(
                                rx.text(
                                    "Nova senha",
                                    size="2",
                                    weight="medium",
                                    color="white",
                                ),
                                rx.input(
                                    id=_PASSWORD_FIELD_ID,
                                    name="password",
                                    type="password",
                                    auto_complete=True,
                                    aria_label="Nova senha",
                                    required=True,
                                    min_length=8,
                                    disabled=EmployeeInvitationActivationState.is_loading,
                                    width="100%",
                                ),
                                width="100%",
                                align="stretch",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Confirme a senha",
                                    size="2",
                                    weight="medium",
                                    color="white",
                                ),
                                rx.input(
                                    id=_PASSWORD_CONFIRMATION_FIELD_ID,
                                    name="password_confirmation",
                                    type="password",
                                    auto_complete=True,
                                    aria_label="Confirme a senha",
                                    required=True,
                                    min_length=8,
                                    disabled=EmployeeInvitationActivationState.is_loading,
                                    width="100%",
                                ),
                                width="100%",
                                align="stretch",
                            ),
                            rx.text(
                                "Use pelo menos 8 caracteres, incluindo uma letra e um número.",
                                size="1",
                                color="var(--gray-9)",
                            ),
                            rx.button(
                                "Ativar conta",
                                type="submit",
                                loading=EmployeeInvitationActivationState.is_loading,
                                disabled=EmployeeInvitationActivationState.is_loading,
                                color_scheme="blue",
                                size="3",
                                width="100%",
                            ),
                            spacing="4",
                            width="100%",
                            align="stretch",
                        ),
                        on_submit=EmployeeInvitationActivationState.activate,
                        reset_on_submit=False,
                        width="100%",
                    ),
                    rx.text(
                        "Peça ao administrador para enviar um novo convite.",
                        role="status",
                        color="var(--gray-9)",
                    ),
                ),
                rx.link("Voltar ao login", href="/login", color="var(--blue-9)"),
                align="stretch",
                spacing="5",
                padding="clamp(1.5rem, 5vw, 2.75rem)",
                border_radius="20px",
                background="rgba(20, 20, 23, 0.96)",
                box_shadow="0 24px 60px rgba(0, 0, 0, 0.35)",
                max_width="440px",
                width="min(100% - 2rem, 440px)",
                border="1px solid rgba(255, 255, 255, 0.12)",
            ),
            min_height="100vh",
            padding_y="6",
        ),
        background="#0b0d11",
        min_height="100vh",
        width="100%",
        on_mount=EmployeeInvitationActivationState.load_invitation,
    )
