import reflex as rx

from academia.login import LoginState
from academia.services.xano_client import XanoAPIError, XanoClient


class AdminAccessState(rx.State):
    is_admin: bool = False
    is_verifying: bool = True
    error_message: str = ""
    authorized_route: str = ""

    def clear(self) -> None:
        self.is_admin = False
        self.is_verifying = False
        self.error_message = ""
        self.authorized_route = ""


async def begin_admin_check(state: rx.State) -> None:
    if not hasattr(state, "get_state"):
        return
    access_state = await state.get_state(AdminAccessState)
    access_state.is_admin = False
    access_state.is_verifying = True
    access_state.error_message = ""
    access_state.authorized_route = ""


async def require_admin(
    state: rx.State,
    route: str = "",
) -> tuple[str, bool]:
    access_state = await state.get_state(AdminAccessState)
    access_state.is_admin = False
    access_state.is_verifying = True
    access_state.error_message = ""
    access_state.authorized_route = ""

    login_state = await state.get_state(LoginState)
    token = login_state.auth_token
    if not token:
        from academia.session_state import clear_app_session

        await clear_app_session(state)
        access_state = await state.get_state(AdminAccessState)
        access_state.error_message = ""
        return "", True

    try:
        identity = XanoClient.get_current_user(token)
    except XanoAPIError as error:
        access_state = await state.get_state(AdminAccessState)
        access_state.is_verifying = False
        if error.status_code == 401:
            from academia.session_state import clear_app_session

            await clear_app_session(state)
            return "", True
        if error.status_code == 403:
            access_state.error_message = (
                "Você não tem permissão para acessar esta área."
            )
        else:
            access_state.error_message = (
                "Não foi possível verificar seu perfil. Tente novamente."
            )
        return "", False

    access_state = await state.get_state(AdminAccessState)
    access_state.is_verifying = False
    if identity.get("role") != "admin":
        access_state.error_message = (
            "Você não tem permissão para acessar esta área."
        )
        return "", False

    access_state.is_admin = True
    access_state.authorized_route = route
    return token, False
