import reflex as rx

from academia.services.auth_client import (
    AuthenticationAPIError,
    AuthenticationClient,
    validate_login_fields,
)


class LoginState(rx.State):
    # Estado do Login
    email: str = ""
    password: str = ""
    password_visible: bool = False
    auth_token: str = ""
    error_message: str = ""
    is_loading: bool = False

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