import asyncio

import reflex as rx

from academia.login import LoginState
from academia.services.xano_client import XanoAPIError, XanoClient

ROLE_ROUTE_ACCESS = {
    "admin": frozenset(
        {
            "dashboard",
            "alunos",
            "planos",
            "matriculas",
            "financeiro",
            "checkins",
            "funcionarios",
            "modalidades",
            "sessoes",
            "relatorios",
        }
    ),
    "recepcionista": frozenset(
        {"alunos", "matriculas", "financeiro", "checkins"}
    ),
    "instrutor": frozenset({"alunos", "checkins"}),
}


class AdminAccessState(rx.State):
    is_admin: bool = False
    is_receptionist: bool = False
    is_instructor: bool = False
    user_role: str = ""
    is_verifying: bool = True
    error_message: str = ""
    authorized_route: str = ""

    def clear(self) -> None:
        self.is_admin = False
        self.is_receptionist = False
        self.is_instructor = False
        self.user_role = ""
        self.is_verifying = False
        self.error_message = ""
        self.authorized_route = ""


async def begin_admin_check(state: rx.State) -> None:
    if not hasattr(state, "get_state"):
        return
    access_state = await state.get_state(AdminAccessState)
    access_state.is_admin = False
    access_state.is_receptionist = False
    access_state.is_instructor = False
    access_state.user_role = ""
    access_state.is_verifying = True
    access_state.error_message = ""
    access_state.authorized_route = ""


async def require_roles(
    state: rx.State,
    allowed_roles: set[str],
    route: str = "",
    denial_message: str = "Você não tem permissão para acessar esta área.",
) -> tuple[str, bool]:
    access_state = await state.get_state(AdminAccessState)
    access_state.is_admin = False
    access_state.is_receptionist = False
    access_state.is_instructor = False
    access_state.user_role = ""
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

    role = login_state._get_verified_profile_role(token)
    if not role:
        try:
            identity = await asyncio.to_thread(
                XanoClient.get_current_user_with_retry,
                token,
            )
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
            elif error.status_code == 429:
                access_state.error_message = (
                    "A API está limitando solicitações. Aguarde um momento e "
                    "tente novamente."
                )
            else:
                access_state.error_message = (
                    "Não foi possível verificar seu perfil. Tente novamente."
                )
            return "", False

        identity_role = identity.get("role")
        role = (
            identity_role
            if isinstance(identity_role, str)
            and identity_role in ROLE_ROUTE_ACCESS
            else ""
        )
        if role:
            login_state._cache_verified_profile(token, role)

    access_state = await state.get_state(AdminAccessState)
    access_state.is_verifying = False
    if role not in allowed_roles:
        access_state.error_message = denial_message
        return "", False

    access_state.user_role = role
    access_state.is_admin = role == "admin"
    access_state.is_receptionist = role == "recepcionista"
    access_state.is_instructor = role == "instrutor"
    access_state.authorized_route = route
    return token, False


async def require_admin(
    state: rx.State,
    route: str = "",
) -> tuple[str, bool]:
    return await require_roles(state, {"admin"}, route)


async def require_route_access(
    state: rx.State,
    route: str,
) -> tuple[str, bool]:
    allowed_roles = {
        role for role, routes in ROLE_ROUTE_ACCESS.items() if route in routes
    }
    return await require_roles(state, allowed_roles, route)
