import reflex as rx


async def clear_app_session(state: rx.State) -> None:
    from academia.academia import DashboardState
    from academia.alunos import AlunosState
    from academia.login import LoginState
    from academia.matriculas import MatriculasState
    from academia.planos import PlanosState

    dashboard_state = await state.get_state(DashboardState)
    dashboard_state.alunos = []
    dashboard_state.search_query = ""
    dashboard_state.error_message = ""
    dashboard_state.is_loading = False

    alunos_state = await state.get_state(AlunosState)
    alunos_state._clear_sensitive_data()
    alunos_state.is_loading = False
    alunos_state.is_loading_details = False
    alunos_state.is_saving = False
    alunos_state.is_deactivating = False

    planos_state = await state.get_state(PlanosState)
    planos_state._clear_sensitive_data()
    planos_state.is_loading = False
    planos_state.is_loading_details = False
    planos_state.is_saving = False
    planos_state.is_changing_status = False

    matriculas_state = await state.get_state(MatriculasState)
    matriculas_state._clear_sensitive_data()
    matriculas_state.is_loading = False
    matriculas_state.is_saving = False
    matriculas_state.is_loading_details = False

    login_state = await state.get_state(LoginState)
    login_state.auth_token = ""
    login_state.email = ""
    login_state.password = ""
    login_state.password_visible = False
    login_state.signup_password = ""
    login_state.signup_password_visible = False
