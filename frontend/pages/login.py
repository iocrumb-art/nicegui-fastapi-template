import httpx
from nicegui import app, ui
from frontend import state
from frontend.components.form_helpers import enable_button_on_user_inputs
from frontend.components import notifications
from pathlib import Path

@ui.page("/login", dark=True)
def login_page():
    """Defines the page for login."""
    static_files_dir = Path(__file__).parent / 'static'
    static_files_dir.mkdir(exist_ok=True) 
    app.add_static_files('/static', static_files_dir.as_posix())

    #ui.image('/static/id662.png').classes('size-32')
    ui.query('.nicegui-content').classes('p-0')

    if state.get_auth():
        ui.navigate.to("/landing")
        return
    
    with ui.card().classes("absolute-center w-full max-w-md p-2"):
    #with ui.card().classes("absolute-center right-2 w-full max-w-md p-2 bg-transparent no-shadow border border-gray-200"):
      with ui.row().classes('w-full justify-center'):
        #ui.label("").classes("text-h6 text-gray")

        email = (
            ui.input("Username").props("autocomplete=username outlined").classes("w-full text-white border border-gray-200")
        )
        password = (
            ui.input("Password")
            .props("type=password autocomplete=current-password outlined")
            .classes("w-full text-white border border-gray-200")
        )
        login_button = ui.button("Log in").props("color=slate-700").classes("w-full")

        login_button.on("click", lambda: perform_login(email, password))
        email.on("keydown.enter", lambda: perform_login(email, password))
        password.on("keydown.enter", lambda: perform_login(email, password))

        email.on(
            "update:model-value",
            lambda: enable_button_on_user_inputs([email, password], login_button),
        )
        password.on(
            "update:model-value",
            lambda: enable_button_on_user_inputs([email, password], login_button),
        )

        # Set the initial disabled state of the button
        enable_button_on_user_inputs([email, password], login_button)


async def perform_login(email_input: ui.input, password_input: ui.input):
    """Sends user credentials to the backend."""
    if not email_input.validate() or not password_input.validate():
        return
    data = {"username": email_input.value, "password": password_input.value}
    try:
        url = "http://127.0.0.1:8000/login/access-token"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
        if response.status_code == 200:
            state.set_auth(response.json())
            app.storage.user["is_superuser"] = email_input.value == "u016645151@example.com"
            app.storage.user['username'] = email_input.value
            ui.navigate.to("/landing")
        else:
            notifications.show_error(response.json().get("detail", "Login failed."))
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")
