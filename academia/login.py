import reflex as rx
import httpx
import os

class LoginState(rx.State):
    # Estado do Login
    email: str = ""
    password: str = ""
    error_message: str = ""
    is_loading: bool = False

    # Estado do Modal de Cadastro
    is_signup_open: bool = False
    signup_name: str = ""
    signup_email: str = ""
    signup_password: str = ""
    signup_error: str = ""
    signup_success: str = ""
    is_signup_loading: bool = False

    def set_email_val(self, val: str):
        self.email = val

    def set_password_val(self, val: str):
        self.password = val

    def set_signup_name(self, val: str):
        self.signup_name = val

    def set_signup_email(self, val: str):
        self.signup_email = val

    def set_signup_password(self, val: str):
        self.signup_password = val

    def toggle_signup_modal(self):
        """Abre/Fecha o modal de cadastro e limpa mensagens."""
        self.is_signup_open = not self.is_signup_open
        self.signup_error = ""
        self.signup_success = ""

    def handle_login(self):
        """Valida os campos e envia a requisição de login para o Xano."""
        self.error_message = ""

        if not self.email or not self.password:
            self.error_message = "Por favor, preencha o e-mail e a senha."
            return

        self.is_loading = True
        yield

        api_url = os.getenv("API_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:sGd5fzIy")
        endpoint = f"{api_url}/auth/login"

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    endpoint,
                    json={"email": self.email, "password": self.password}
                )

                if response.status_code == 200:
                    data = response.json()
                    token = data.get("authToken") or data.get("token")
                    
                    yield rx.set_value("auth_token", token)
                    yield rx.redirect("/")
                else:
                    self.error_message = "E-mail ou senha incorretos."
        except Exception as e:
            self.error_message = f"Erro ao conectar com o servidor: {str(e)}"
        finally:
            self.is_loading = False

    def handle_signup(self):
        """Envia os dados de novo utilizador para o Xano."""
        self.signup_error = ""
        self.signup_success = ""

        if not self.signup_name or not self.signup_email or not self.signup_password:
            self.signup_error = "Preencha todos os campos do formulário."
            return

        self.is_signup_loading = True
        yield

        api_url = os.getenv("API_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:sGd5fzIy")
        endpoint = f"{api_url}/auth/signup"

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    endpoint,
                    json={
                        "name": self.signup_name,
                        "email": self.signup_email,
                        "password": self.signup_password
                    }
                )

                if response.status_code in (200, 201):
                    self.signup_success = "Conta criada com sucesso! Pode fechar e fazer login."
                    self.signup_name = ""
                    self.signup_email = ""
                    self.signup_password = ""
                else:
                    self.signup_error = "Não foi possível realizar o cadastro. Verifique os dados."
        except Exception as e:
            self.signup_error = f"Erro ao conectar: {str(e)}"
        finally:
            self.is_signup_loading = False


def signup_dialog() -> rx.Component:
    """Modal/Pop-up para cadastro de novos utilizadores."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Criar Nova Conta", color="white", size="5"),
            rx.dialog.description("Preencha as informações para registar um novo utilizador no sistema.", color="var(--gray-9)", size="2"),
            
            rx.vstack(
                rx.cond(
                    LoginState.signup_error != "",
                    rx.callout(LoginState.signup_error, icon="triangle_alert", color_scheme="red", width="100%"),
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
                    ),
                    spacing="1",
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
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Senha", size="2", color="white"),
                    rx.input(
                        placeholder="••••••••",
                        type="password",
                        size="3",
                        width="100%",
                        value=LoginState.signup_password,
                        on_change=LoginState.set_signup_password,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray", cursor="pointer"),
                    ),
                    rx.button(
                        "Cadastrar",
                        color_scheme="blue",
                        cursor="pointer",
                        loading=LoginState.is_signup_loading,
                        on_click=LoginState.handle_signup,
                    ),
                    justify="end",
                    spacing="3",
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
            max_width="480px",
            padding="6",
        ),
        open=LoginState.is_signup_open,
        on_open_change=LoginState.toggle_signup_modal,
    )


def login_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                # Cabeçalho
                rx.vstack(
                    rx.heading("SISTEMA ACADEMIA", size="8", weight="bold", color="white"),
                    rx.text("Acesse sua conta para continuar", color="var(--gray-9)", size="3"),
                    align="center",
                    spacing="2",
                ),
                
                # Mensagem de Erro
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

                # Formulário
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
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Senha", size="2", weight="medium", color="white"),
                        rx.input(
                            placeholder="••••••••",
                            type="password",
                            size="3",
                            width="100%",
                            variant="surface",
                            value=LoginState.password,
                            on_change=LoginState.set_password_val,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.button(
                        "Entrar no Sistema",
                        size="3",
                        width="100%",
                        color_scheme="blue",
                        cursor="pointer",
                        margin_top="2",
                        loading=LoginState.is_loading,
                        on_click=LoginState.handle_login,
                    ),
                    # Link para abrir o Modal de Cadastro
                    rx.hstack(
                        rx.text("Ainda não tem conta?", size="2", color="var(--gray-9)"),
                        rx.text(
                            "Cadastre-se",
                            size="2",
                            color="var(--blue-9)",
                            weight="bold",
                            cursor="pointer",
                            on_click=LoginState.toggle_signup_modal,
                        ),
                        justify="center",
                        spacing="2",
                        width="100%",
                        margin_top="2",
                    ),
                    spacing="4",
                    width="100%",
                    padding_x="8",
                ),
                spacing="8",
                align="center",
                padding_x="12",
                padding_y="16",
                border_radius="16px",
                background="rgba(20, 20, 23, 0.88)",
                backdrop_filter="blur(16px)",
                box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.8)",
                max_width="680px",
                width="92%",
                border="1px solid rgba(255, 255, 255, 0.15)",
            ),
            min_height="100vh",
        ),
        signup_dialog(),  # Modal inserido na página
        background_image="url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1920&auto=format&fit=crop')",
        background_size="cover",
        background_position="center",
        min_height="100vh",
        width="100%",
    )