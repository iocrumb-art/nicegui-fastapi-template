from contextlib import contextmanager
from nicegui import app, ui
from frontend import state
from frontend.state import clear_auth
from frontend.components.header import create_header
from frontend.components.footer import create_footer

@contextmanager
def dashboard_frame(title: str):
    ui.colors(primary='slate-700')

    """
    A layout for all protected dashboard pages.
    - It checks for authentication and redirects to /login if the user is not logged in.
    - It provides a consistent header/footer and a full-height drawer.
    """
    if not state.get_auth():
        ui.navigate.to("/login")
        return

    async def handle_logout():
        clear_auth()
        app.storage.user.clear()
        ui.navigate.to("/login")

    #left_drawer = ui.left_drawer(value=True, elevated=True).classes("bg-white")
    left_drawer = ui.header(value=True, elevated=False)

    # Render header from shared components
    create_header(left_drawer, title)

    # TODO: Extract into a reusable component
    #with ui.left_drawer(value=True, elevated=False).classes("bg-white") as left_drawer:


    if app.storage.user.get("is_superuser"):
        with ui.page_sticky(position='bottom-left', x_offset=312, y_offset=20):
          ui.button('Create User', on_click=lambda: ui.navigate.to("/users/create"))

    if app.storage.user.get("is_superuser"):
        with ui.page_sticky(position='bottom-left', x_offset=195, y_offset=20):
          ui.button('List Users', on_click=lambda: ui.navigate.to("/users/list"))

    with ui.column().classes("w-full p-4 md:p-8 items-center"):
        yield

    # Render footer from shared components
    create_footer()
