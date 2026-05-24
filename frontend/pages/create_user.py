import httpx
from nicegui import app, ui
from frontend import state
from frontend.layouts.default import dashboard_frame
from frontend.components.form_helpers import enable_button_on_user_inputs
from frontend.components import notifications
from backend.core.security import get_password_hash
from pathlib import Path


#########################################################################################3
## CREATE USER 

@ui.page("/users/create", dark=True)
def create_user_page():
    """Defines the page for creating a new user."""
    with dashboard_frame(title="Create a User"):

        static_files_dir = Path(__file__).parent / 'static'
        static_files_dir.mkdir(exist_ok=True)
        app.add_static_files('/static', static_files_dir.as_posix())
        ui.add_css('''
                body {
                        background-image: url('/static/id660.jpg');
                        background-size: cover; /* This makes the image cover the entire viewport */
                        background-repeat: no-repeat;
                        background-attachment: fixed; /* Keeps the image fixed while scrolling */
                }
            ''')

        if not app.storage.user.get("is_superuser"):
            ui.label("You don't have permission to access this page.").classes(
                "text-red-500"
            )
            return

        with ui.card().tight().classes("w-full p-10 justify-center text-white"):
            ui.label("Create a New User")

            email = (
                ui.input("Email")
                .props("autocomplete=username outlined")
                .classes("w-full")
            )
            password = (
                ui.input("Password")
                .props("type=password autocomplete=current-password outlined")
                .classes("w-full")
            )
            #is_superuser = ui.checkbox("Is Superuser?").classes("w-full")
            is_superuser = ui.input()
            is_superuser.visible = False
            is_superuser.value = 'f'

            user_button = (
                ui.button("Create User").props("color=black").classes("w-full")
            )

            user_button.on("click", lambda: create_user(email, password, is_superuser))
            email.on(
                "keydown.enter", lambda: create_user(email, password, is_superuser)
            )
            password.on(
                "keydown.enter", lambda: create_user(email, password, is_superuser)
            )

            email.on(
                "update:model-value",
                lambda: enable_button_on_user_inputs([email, password], user_button),
            )
            password.on(
                "update:model-value",
                lambda: enable_button_on_user_inputs([email, password], user_button),
            )

            # Set initial button state
            enable_button_on_user_inputs([email, password], user_button)


async def create_user(
    email_input: ui.input, password_input: ui.input, is_superuser_checkbox: ui.checkbox
):
    """Creates a new user using data from the input elements."""
    token = state.get_token()
    if not token:
        return
    data = {
        "email": email_input.value,
        "password": password_input.value,
        "is_superuser": is_superuser_checkbox.value,
    }
    headers = {"Authorization": token}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8000/api/v1/user/", json=data, headers=headers
            )
        if response.status_code == 200:
            notifications.show_success(f"User {email_input.value} created!")
            email_input.value = ""
            password_input.value = ""
            is_superuser_checkbox.value = False
        else:
            notifications.show_error(response.json().get("detail"))
    except httpx.RequestError:
        notifications.show_error("Could not connect to backend.")


#########################################################################################3
## LIST USERS 


@ui.page("/users/list", dark=True)
def list_user_page():
    with dashboard_frame(title="List Users"):

        static_files_dir = Path(__file__).parent / 'static'
        static_files_dir.mkdir(exist_ok=True)
        app.add_static_files('/static', static_files_dir.as_posix())
        ui.add_css('''
                body {
                        background-image: url('/static/id660.jpg');
                        background-size: cover; /* This makes the image cover the entire viewport */
                        background-repeat: no-repeat;
                        background-attachment: fixed; /* Keeps the image fixed while scrolling */
                }
            ''')

        items_grid = ui.grid(columns=1).classes(
            "w-full gap-3 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
        )
        if not app.storage.user.get("is_superuser"):
            ui.label("You don't have permission to access this page.").classes(
                "text-red-500"
            )
            return

        ui.timer(0.1, lambda: list_user(items_grid), once=True)
        """
        with ui.card().classes("w-full max-w-md p-8"):
            user_button = (
                ui.button("List Users").props("color=black").classes("w-full")
            )
            
            user_button.on("click", lambda: list_user(items_grid))
        """


async def list_user(grid: ui.grid):
    """Lists Users"""
    token = state.get_token()
    if not token:
        return
    headers = {"Authorization": token}
    try:
        headers = {"Authorization": token}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://127.0.0.1:8000/api/v1/userlist/", headers=headers
            )
        if response.status_code == 200:
          grid.clear()
          with grid:
            for user in response.json():
              with ui.card().classes("p-0 w-full gap-0 bg-transparent"):  
                with ui.grid(columns='auto 20px 30px').classes('w-full p-0 gap-0'):
                   ui.label(user["email"]).classes("text-sm p-0 gap-0 text-white")

                    # Modify Button - opens its own dialog
                   with (
                          ui.dialog() as modify_dialog,
                          ui.card().classes("min-w-[300px]"),
                    ):
                          ui.label("Change User Password").classes("text-h6")
                          modify_title = ui.label(
                               user["email"]
                          ).classes("w-full")
                          modify_desc = ui.textarea(
                               "Set New Password", placeholder='start typing'
                          ).classes("w-full")
                          # The lambda captures the item's specific data for the handler
                          ui.button(
                               "Save",
                               on_click=lambda i=user,
                               t=modify_title,
                               d=modify_desc: update_user(i["id"], t, d, modify_dialog, grid),
                          ).classes("w-full text-white")

                   # Delete Button - opens a confirmation dialog
                   with ui.dialog() as confirm_dialog, ui.card():
                      ui.label(f"Are you sure you want to delete '{user['email']}'?")
                      with ui.row().classes("w-full justify-end"):
                         ui.button(
                         "Cancel",
                         on_click=confirm_dialog.close,
                         color="black",
                         )
                         # The lambda captures the specific item_id for the handler
                         ui.button(
                         "Yes",
                         on_click=lambda user_id=user[
                         "id"
                         ]: delete_user(user_id, grid),
                         color="red",
                         )

                   ui.button(
                     icon="edit", on_click=modify_dialog.open
                   ).props("flat dense")

                   ui.button(
                     icon="delete", on_click=confirm_dialog.open
                     ).props("flat dense color=red")


        else:
            notifications.show_error(response.json().get("detail"))
    except httpx.RequestError:
        notifications.show_error("Could not connect to backend.")


async def delete_user(user_id: int, grid: ui.grid):
    """Makes an API call to delete users data and account and reloads the grid on success."""
    token = state.get_token()
    if not token:
        return

    try:
        headers = {"Authorization": token}
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://127.0.0.1:8000/api/v1/user/{user_id}", headers=headers
            )
        if response.status_code == 200:
            notifications.show_success("User Account Deleted Successfully.")
            await list_user(grid)  # Refresh the items grid
        else:
            notifications.show_error(f"Error: {response.json().get('detail')}")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")



async def update_user(
    user_id: int,
    title_input: ui.input,
    desc_input: ui.textarea,
    dialog: ui.dialog,
    grid: ui.grid,
):
    """Makes an API call to update an item and reloads the grid on success."""
    token = state.get_token()
    if not token:
        return
    #data = {"email": title_input.value, "id": desc_input.value, "hashed_password": "$2b$12$He0FZHMPZQb7sjaCEFt/BO2P2Tlk0BPuXwNolq8im9o9Ry6ToKKM."}
    data = {"hashed_password": get_password_hash(desc_input.value)}

    try:
        headers = {"Authorization": token}
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://127.0.0.1:8000/api/v1/user/{user_id}",
                json=data,
                headers=headers,
            )
        if response.status_code == 200:
            notifications.show_success("Password Updated Successfully.")
            dialog.close()
            await list_user(grid)
        else:
            notifications.show_error(f"Error: {response.json().get('detail')}")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")



