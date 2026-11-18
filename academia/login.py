from typing import Any

import reflex as rx

from academia.services.auth_client import (
    AuthenticationAPIError,
    AuthenticationClient,
    LoginResult,
    validate_login_fields,
    validate_new_password,
)
from academia.services.xano_client import XanoAPIError, XanoClient

LANDING_ROUTE_BY_ROLE = {
    "admin": "/",
    "recepcionista": "/alunos",
    "instrutor": "/alunos",
}
TEMPORARY_PASSWORD_FIELD_ID = "temporary-login-password"
NEW_PASSWORD_FIELD_ID = "temporary-login-new-password"
NEW_PASSWORD_CONFIRMATION_FIELD_ID = (
    "temporary-login-new-password-confirmation"
)
LOGIN_PASSWORD_FIELD_ID = "login-password"


class LoginState(rx.State):
    # Estado do Login
    email: str = ""
    password_visible: bool = False
    auth_token: str = ""
    error_message: str = ""
    success_message: str = ""
    requires_password_change: bool = False
    is_loading: bool = False

    @rx.event
    def set_email_val(self, val: str):
        self.email = val

    @rx.event
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible

    @rx.event
    def handle_login(self, form_data: dict[str, Any]):
        """Valida as credenciais, abre uma sessão e encaminha para a aplicação."""
        if self.is_loading:
            yield rx.set_value(LOGIN_PASSWORD_FIELD_ID, "")
            return

        self.error_message = ""
        self.success_message = ""
        self.requires_password_change = False
        password_value = form_data.get("password", "")
        password = password_value if isinstance(password_value, str) else ""
        validation_error = validate_login_fields(self.email, password)
        if validation_error:
            self.error_message = validation_error
            yield rx.set_value(LOGIN_PASSWORD_FIELD_ID, "")
            return

        normalized_email = self.email.strip().lower()
        self.is_loading = True
        self.auth_token = ""
        yield

        try:
            login_result: LoginResult = AuthenticationClient.login(
                normalized_email,
                password,
            )
        except AuthenticationAPIError as error:
            if error.status_code in (401, 403):
                self.error_message = "E-mail ou senha incorretos."
            else:
                self.error_message = str(error)
        else:
            if login_result.requires_password_change:
                self.auth_token = ""
                self.email = normalized_email
                self.password_visible = False
                if login_result.temporary_password_expired:
                    self.error_message = (
                        "A senha temporária expirou. Solicite uma nova ao "
                        "administrador."
                    )
                else:
                    self.requires_password_change = True
                return

            token = login_result.token
            if not token:
                self.error_message = (
                    "O servidor não retornou uma sessão válida."
                )
                return
            try:
                identity = XanoClient.get_current_user(token)
            except XanoAPIError:
                self.error_message = (
                    "Não foi possível verificar seu perfil. Tente novamente."
                )
            else:
                route = LANDING_ROUTE_BY_ROLE.get(identity.get("role"))
                if route is None:
                    self.error_message = (
                        "Sua conta não possui um perfil autorizado para acessar "
                        "o aplicativo."
                    )
                else:
                    self.auth_token = token
                    self.email = normalized_email
                    self.password_visible = False
                    yield rx.redirect(route)
        finally:
            self.is_loading = False
            yield rx.set_value(LOGIN_PASSWORD_FIELD_ID, "")

    @rx.event
    async def change_temporary_password(
        self,
        form_data: dict[str, Any],
    ):
        if self.is_loading:
            yield rx.set_value(TEMPORARY_PASSWORD_FIELD_ID, "")
            yield rx.set_value(NEW_PASSWORD_FIELD_ID, "")
            yield rx.set_value(NEW_PASSWORD_CONFIRMATION_FIELD_ID, "")
            return

        if not self.requires_password_change or not self.email:
            self.error_message = (
                "A troca de senha não está disponível. Faça login novamente."
            )
            yield rx.set_value(TEMPORARY_PASSWORD_FIELD_ID, "")
            yield rx.set_value(NEW_PASSWORD_FIELD_ID, "")
            yield rx.set_value(NEW_PASSWORD_CONFIRMATION_FIELD_ID, "")
            return

        temporary_password_value = form_data.get("temporary_password", "")
        password_value = form_data.get("password", "")
        password_confirmation_value = form_data.get(
            "password_confirmation",
            "",
        )
        temporary_password = (
            temporary_password_value
            if isinstance(temporary_password_value, str)
            else ""
        )
        password = password_value if isinstance(password_value, str) else ""
        password_confirmation = (
            password_confirmation_value
            if isinstance(password_confirmation_value, str)
            else ""
        )
        self.error_message = ""
        self.success_message = ""
        self.is_loading = True
        yield

        try:
            validation_error = validate_new_password(
                password,
                password_confirmation,
            )
            if validation_error:
                self.error_message = validation_error
                return

            try:
                AuthenticationClient.change_temporary_password(
                    self.email,
                    temporary_password,
                    password,
                    password_confirmation,
                )
            except AuthenticationAPIError as error:
                if error.status_code in (401, 403, 404, 410):
                    self.requires_password_change = False
                    self.error_message = (
                        "A senha temporária está incorreta ou expirou. "
                        "Solicite uma nova ao administrador."
                    )
                else:
                    self.error_message = (
                        "Não foi possível trocar a senha. Tente novamente."
                    )
            else:
                self.requires_password_change = False
                self.auth_token = ""
                self.password_visible = False
                self.success_message = (
                    "Senha alterada. Faça login novamente com sua nova senha."
                )
        finally:
            self.is_loading = False
            yield rx.set_value(TEMPORARY_PASSWORD_FIELD_ID, "")
            yield rx.set_value(NEW_PASSWORD_FIELD_ID, "")
            yield rx.set_value(NEW_PASSWORD_CONFIRMATION_FIELD_ID, "")

    @rx.event
    async def logout(self):
        from academia.session_state import clear_app_session

        await clear_app_session(self)
        return rx.redirect("/login")

def temporary_password_change_form() -> rx.Component:
    return rx.form.root(
        rx.vstack(
            rx.text(
                "Troca obrigatória de senha",
                size="3",
                weight="bold",
                color="white",
            ),
            rx.text(
                "A credencial temporária é válida por 24 horas. "
                "Defina uma nova senha para continuar.",
                size="2",
                color="var(--gray-9)",
            ),
            rx.text(
                "Conta: ",
                LoginState.email,
                size="2",
                color="white",
            ),
            rx.vstack(
                rx.text(
                    "Senha temporária",
                    size="2",
                    weight="medium",
                    color="white",
                ),
                rx.input(
                    id=TEMPORARY_PASSWORD_FIELD_ID,
                    name="temporary_password",
                    type="password",
                    auto_complete=False,
                    required=True,
                    disabled=LoginState.is_loading,
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                rx.text(
                    "Nova senha",
                    size="2",
                    weight="medium",
                    color="white",
                ),
                rx.input(
                    id=NEW_PASSWORD_FIELD_ID,
                    name="password",
                    type="password",
                    auto_complete=False,
                    required=True,
                    min_length=8,
                    disabled=LoginState.is_loading,
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                rx.text(
                    "Confirme a nova senha",
                    size="2",
                    weight="medium",
                    color="white",
                ),
                rx.input(
                    id=NEW_PASSWORD_CONFIRMATION_FIELD_ID,
                    name="password_confirmation",
                    type="password",
                    auto_complete=False,
                    required=True,
                    min_length=8,
                    disabled=LoginState.is_loading,
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            rx.button(
                "Trocar senha e voltar ao login",
                type="submit",
                size="3",
                width="100%",
                color_scheme="blue",
                loading=LoginState.is_loading,
            ),
            spacing="4",
            width="100%",
        ),
        on_submit=LoginState.change_temporary_password,
        width="100%",
    )


def login_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                rx.vstack(
                    rx.box(
                        rx.icon("dumbbell", size=24, color="var(--blue-9)"),
                        padding="3",
                        border_radius="full",
                        background="rgba(59, 130, 246, 0.12)",
                    ),
                    rx.heading(
                        "SISTEMA ACADEMIA",
                        size="6",
                        weight="bold",
                        color="white",
                        text_align="center",
                    ),
                    rx.text(
                        rx.cond(
                            LoginState.requires_password_change,
                            "Conclua a troca obrigatória de senha",
                            "Acesse sua conta para continuar",
                        ),
                        color="var(--gray-9)",
                        size="3",
                        text_align="center",
                    ),
                    align="center",
                    spacing="3",
                    width="100%",
                ),
                rx.cond(
                    LoginState.error_message != "",
                    rx.callout(
                        LoginState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.cond(
                    LoginState.success_message != "",
                    rx.callout(
                        LoginState.success_message,
                        icon="circle-check",
                        color_scheme="green",
                        role="status",
                        width="100%",
                    ),
                ),
                rx.cond(
                    LoginState.requires_password_change,
                    temporary_password_change_form(),
                    rx.form.root(
                        rx.vstack(
                            rx.vstack(
                                rx.text(
                                    "E-mail",
                                    size="2",
                                    weight="medium",
                                    color="white",
                                ),
                                rx.input(
                                    placeholder="seuemail@academia.com",
                                    type="email",
                                    size="3",
                                    width="100%",
                                    variant="surface",
                                    value=LoginState.email,
                                    on_change=LoginState.set_email_val,
                                    disabled=LoginState.is_loading,
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Senha",
                                    size="2",
                                    weight="medium",
                                    color="white",
                                ),
                                rx.hstack(
                                    rx.input(
                                        id=LOGIN_PASSWORD_FIELD_ID,
                                        name="password",
                                        placeholder="Digite sua senha",
                                        type=rx.cond(
                                            LoginState.password_visible,
                                            "text",
                                            "password",
                                        ),
                                        size="3",
                                        flex="1",
                                        min_width="0",
                                        variant="surface",
                                        auto_complete=False,
                                        disabled=LoginState.is_loading,
                                    ),
                                    rx.button(
                                        rx.cond(
                                            LoginState.password_visible,
                                            rx.icon("eye-off", size=18),
                                            rx.icon("eye", size=18),
                                        ),
                                        type="button",
                                        variant="soft",
                                        color_scheme="gray",
                                        size="3",
                                        aria_label=rx.cond(
                                            LoginState.password_visible,
                                            "Ocultar senha",
                                            "Mostrar senha",
                                        ),
                                        title=rx.cond(
                                            LoginState.password_visible,
                                            "Ocultar senha",
                                            "Mostrar senha",
                                        ),
                                        on_click=(
                                            LoginState.toggle_password_visibility
                                        ),
                                        disabled=LoginState.is_loading,
                                    ),
                                    align="center",
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.button(
                                "Entrar",
                                size="3",
                                width="100%",
                                color_scheme="blue",
                                cursor="pointer",
                                type="submit",
                                loading=LoginState.is_loading,
                            ),
                            spacing="5",
                            width="100%",
                        ),
                        on_submit=LoginState.handle_login,
                        width="100%",
                    ),
                ),
                spacing="6",
                align="center",
                padding="clamp(1.5rem, 5vw, 2.75rem)",
                border_radius="20px",
                background="rgba(20, 20, 23, 0.88)",
                backdrop_filter="blur(16px)",
                box_shadow="0 24px 60px rgba(0, 0, 0, 0.45)",
                max_width="440px",
                width="min(100% - 2rem, 440px)",
                border="1px solid rgba(255, 255, 255, 0.12)",
            ),
            min_height="100vh",
            padding_y="6",
        ),
        background_image=(
            "linear-gradient(rgba(8, 10, 16, 0.72), rgba(8, 10, 16, 0.86)), "
            "url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?"
            "q=80&w=1920&auto=format&fit=crop')"
        ),
        background_size="cover",
        background_position="center",
        min_height="100vh",
        width="100%",
    )