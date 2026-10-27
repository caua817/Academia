import reflex as rx

from academia.services.auth_client import (
    AuthenticationAPIError,
    AuthenticationClient,
    password_requirements,
    validate_login_fields,
    validate_signup_fields,
)


class LoginState(rx.State):
    # Estado do Login
    email: str = ""
    password: str = ""
    password_visible: bool = False
    auth_token: str = ""
    error_message: str = ""
    is_loading: bool = False

    # Estado do Modal de Cadastro
    is_signup_open: bool = False
    signup_name: str = ""
    signup_email: str = ""
    signup_password: str = ""
    signup_password_visible: bool = False
    signup_password_min_length: bool = False
    signup_password_uppercase: bool = False
    signup_password_lowercase: bool = False
    signup_password_number: bool = False
    signup_error: str = ""
    signup_success: str = ""
    is_signup_loading: bool = False

    @rx.event
    def set_email_val(self, val: str):
        self.email = val

    @rx.event
    def set_password_val(self, val: str):
        self.password = val

    @rx.event
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible

    @rx.event
    def set_signup_name(self, val: str):
        self.signup_name = val

    @rx.event
    def set_signup_email(self, val: str):
        self.signup_email = val

    @rx.event
    def set_signup_password(self, val: str):
        self.signup_password = val
        requirements = password_requirements(val)
        self.signup_password_min_length = requirements["minimum_length"]
        self.signup_password_uppercase = requirements["uppercase"]
        self.signup_password_lowercase = requirements["lowercase"]
        self.signup_password_number = requirements["number"]

    @rx.event
    def toggle_signup_password_visibility(self):
        self.signup_password_visible = not self.signup_password_visible

    @rx.event
    def open_signup_modal(self):
        self.is_signup_open = True
        self.signup_password_visible = False
        self.error_message = ""
        self.signup_error = ""
        self.signup_success = ""

    @rx.event
    def set_signup_open(self, is_open: bool):
        self.is_signup_open = is_open
        self.signup_password_visible = False
        self.error_message = ""
        self.signup_error = ""
        self.signup_success = ""

    @rx.event
    def close_signup_modal(self):
        self.is_signup_open = False
        self.signup_password_visible = False
        self.signup_error = ""
        self.signup_success = ""

    @rx.event
    def handle_login(self):
        """Valida as credenciais, abre uma sessão e encaminha para a aplicação."""
        self.error_message = ""
        validation_error = validate_login_fields(self.email, self.password)
        if validation_error:
            self.error_message = validation_error
            return

        normalized_email = self.email.strip().lower()
        self.is_loading = True
        yield

        try:
            token = AuthenticationClient.login(normalized_email, self.password)
        except AuthenticationAPIError as error:
            if error.status_code in (401, 403):
                self.error_message = "E-mail ou senha incorretos."
            else:
                self.error_message = str(error)
        else:
            self.auth_token = token
            self.email = normalized_email
            self.password = ""
            self.password_visible = False
            yield rx.redirect("/")
        finally:
            self.is_loading = False

    @rx.event
    async def logout(self):
        from academia.session_state import clear_app_session

        await clear_app_session(self)
        return rx.redirect("/login")

    @rx.event
    def handle_signup(self):
        """Valida e envia os dados públicos de cadastro para o Xano."""
        self.signup_error = ""
        self.signup_success = ""

        validation_error = validate_signup_fields(
            self.signup_name,
            self.signup_email,
            self.signup_password,
        )
        if validation_error:
            self.signup_error = validation_error
            return

        self.is_signup_loading = True
        yield

        try:
            AuthenticationClient.signup(
                self.signup_name,
                self.signup_email,
                self.signup_password,
            )
        except AuthenticationAPIError as error:
            if error.status_code in (400, 409):
                self.signup_error = (
                    "Não foi possível realizar o cadastro. "
                    "Verifique os dados ou se o e-mail já está cadastrado."
                )
            else:
                self.signup_error = str(error)
        else:
            self.signup_success = (
                "Conta criada com sucesso! Pode fechar e fazer login."
            )
            self.signup_name = ""
            self.signup_email = ""
            self.signup_password = ""
            self.signup_password_min_length = False
            self.signup_password_uppercase = False
            self.signup_password_lowercase = False
            self.signup_password_number = False
        finally:
            self.is_signup_loading = False


def password_requirement(label: str, is_met: rx.Var[bool]) -> rx.Component:
    return rx.hstack(
        rx.text(
            rx.cond(is_met, "✓", "○"),
            color=rx.cond(is_met, "var(--green-9)", "var(--gray-9)"),
            aria_hidden="true",
        ),
        rx.text(label, size="2", color="var(--gray-10)"),
        align="center",
        spacing="2",
        width="100%",
    )


def signup_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
            rx.vstack(
                rx.dialog.title("Criar sua conta", color="white", size="6"),
                rx.dialog.description(
                    "Preencha seus dados para começar.",
                    color="var(--gray-9)",
                    size="2",
                ),
                align="start",
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                rx.cond(
                    LoginState.signup_error != "",
                    rx.callout(
                        LoginState.signup_error,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.cond(
                    LoginState.signup_success != "",
                    rx.callout(LoginState.signup_success, icon="check_check", color_scheme="green", width="100%"),
                ),
                rx.vstack(
                    rx.text("Nome Completo", size="2", color="white"),
                    rx.input(
                        placeholder="Ex: João Silva",
                        size="3",
                        width="100%",
                        value=LoginState.signup_name,
                        on_change=LoginState.set_signup_name,
                        disabled=LoginState.is_signup_loading,
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("E-mail", size="2", color="white"),
                    rx.input(
                        placeholder="seuemail@academia.com",
                        type="email",
                        size="3",
                        width="100%",
                        value=LoginState.signup_email,
                        on_change=LoginState.set_signup_email,
                        disabled=LoginState.is_signup_loading,
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Senha", size="2", color="white"),
                    rx.hstack(
                        rx.input(
                            placeholder="Crie uma senha segura",
                            type=rx.cond(
                                LoginState.signup_password_visible,
                                "text",
                                "password",
                            ),
                            size="3",
                            flex="1",
                            min_width="0",
                            value=LoginState.signup_password,
                            on_change=LoginState.set_signup_password,
                            disabled=LoginState.is_signup_loading,
                        ),
                        rx.button(
                            rx.cond(
                                LoginState.signup_password_visible,
                                rx.icon("eye-off", size=18),
                                rx.icon("eye", size=18),
                            ),
                            type="button",
                            variant="soft",
                            color_scheme="gray",
                            size="3",
                            aria_label=rx.cond(
                                LoginState.signup_password_visible,
                                "Ocultar senha",
                                "Mostrar senha",
                            ),
                            title=rx.cond(
                                LoginState.signup_password_visible,
                                "Ocultar senha",
                                "Mostrar senha",
                            ),
                            on_click=LoginState.toggle_signup_password_visibility,
                            disabled=LoginState.is_signup_loading,
                        ),
                        align="center",
                        spacing="2",
                        width="100%",
                    ),
                    rx.text(
                        "A senha precisa conter:",
                        size="2",
                        weight="medium",
                        color="var(--gray-10)",
                        margin_top="1",
                    ),
                    rx.vstack(
                        password_requirement(
                            "Pelo menos 8 caracteres",
                            LoginState.signup_password_min_length,
                        ),
                        password_requirement(
                            "Uma letra maiúscula",
                            LoginState.signup_password_uppercase,
                        ),
                        password_requirement(
                            "Uma letra minúscula",
                            LoginState.signup_password_lowercase,
                        ),
                        password_requirement(
                            "Um número",
                            LoginState.signup_password_number,
                        ),
                        align="start",
                        spacing="1",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        cursor="pointer",
                        disabled=LoginState.is_signup_loading,
                        on_click=LoginState.close_signup_modal,
                    ),
                    rx.button(
                        "Cadastrar",
                        color_scheme="blue",
                        cursor="pointer",
                        loading=LoginState.is_signup_loading,
                        on_click=LoginState.handle_signup,
                    ),
                    justify="end",
                    spacing="4",
                    width="100%",
                    margin_top="2",
                ),
                align="stretch",
                spacing="5",
                width="100%",
                padding="clamp(1.25rem, 5vw, 2rem)",
            ),
            ),
            background="#121215",
            border="1px solid rgba(255, 255, 255, 0.15)",
            border_radius="16px",
            max_width="480px",
            width="calc(100vw - 2rem)",
            max_height="85vh",
            overflow_y="auto",
        ),
        open=LoginState.is_signup_open,
        on_open_change=LoginState.set_signup_open,
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
                        "Acesse sua conta para continuar",
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
                rx.vstack(
                    rx.vstack(
                        rx.text("E-mail", size="2", weight="medium", color="white"),
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
                        rx.text("Senha", size="2", weight="medium", color="white"),
                        rx.hstack(
                            rx.input(
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
                                value=LoginState.password,
                                on_change=LoginState.set_password_val,
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
                                on_click=LoginState.toggle_password_visibility,
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
                        loading=LoginState.is_loading,
                        on_click=LoginState.handle_login,
                    ),
                    rx.hstack(
                        rx.text("Ainda não tem conta?", size="2", color="var(--gray-9)"),
                        rx.text(
                            "Cadastre-se",
                            size="2",
                            color="var(--blue-9)",
                            weight="bold",
                            cursor="pointer",
                            on_click=LoginState.open_signup_modal,
                        ),
                        justify="center",
                        spacing="1",
                        width="100%",
                    ),
                    spacing="5",
                    width="100%",
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
        signup_dialog(),
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