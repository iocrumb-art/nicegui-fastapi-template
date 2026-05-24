import httpx
from nicegui import ui, app
from frontend import state
from frontend.components import notifications
from frontend.layouts.default import dashboard_frame
from nicegui import ui
from pathlib import Path

@ui.page("/items2", dark=True)
def items_page():
    """Defines the page for displaying and creating user items."""

    with dashboard_frame(title="My Crumbs"):
        items_grid = ui.grid(columns=1).classes(
            "w-full gap-0 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
        )

        static_files_dir = Path(__file__).parent / 'static'
        static_files_dir.mkdir(exist_ok=True) 
        app.add_static_files('/static', static_files_dir.as_posix())

        async def get_size():
            width = await ui.run_javascript('window.innerWidth')
            height = await ui.run_javascript('window.innerHeight')

            if int(width) < 550:
                ui.add_css('''
                     body {
                             background-image: url('/static/id663.jpg');
                             background-size: cover; /* This makes the image cover the entire viewport */
                             background-repeat: no-repeat;
                             background-attachment: fixed; /* Keeps the image fixed while scrolling */
                          }
                     ''')

            else:

                ui.add_css('''
                     body {
                             background-image: url('/static/id660.jpg');
                             background-size: cover; /* This makes the image cover the entire viewport */
                             background-repeat: no-repeat;
                             background-attachment: fixed; /* Keeps the image fixed while scrolling */
                          }
                     ''')

        ui.timer(0.01, lambda: get_size(), once=True)

        with ui.dialog() as dialog, ui.card().classes("min-w-[300px]"): 
            ui.label("Create New Link").classes("text-h6")
            title_input = ui.input("Title").classes("w-full").props('clearable')
            desc_input = ui.textarea("URL").classes("w-full")
            ui.button(
                "Create",
                on_click=lambda: create_item(
                    title_input, desc_input, dialog, items_grid
                ),
            ).classes("w-full text-white")

        ui.button("Add Link", on_click=dialog.open, icon="add").props(
            "color=primary" 
        ).classes('text-bold p-5 mt-10 gap-2')
        ui.timer(0.1, lambda: load_items(items_grid), once=True)


async def load_items(grid: ui.grid):
    """Fetches items from the API and populates the grid with cards, including action buttons."""
    token = state.get_token()
    if not token:
        return
    try:
        headers = {"Authorization": token}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://127.0.0.1:8000/api/v1/items/", headers=headers
            )

        if response.status_code == 200:


            grid.clear()
            with grid:
  
                raw_data = response.json() 
                filtered = [item for item in raw_data if item.get('title').startswith('2/')]
                for item in filtered:
                #for item in response.json():
                    with ui.card().classes("p-0 bg-transparent"):
                            with ui.grid(columns='auto 20px 30px').classes('w-full gap-0'):
                                # Modify Button - opens its own dialog
                                with (
                                    ui.dialog() as modify_dialog,
                                    ui.card().classes("min-w-[300px]"),
                                ):
                                    ui.label("Modify Link").classes("text-h6")
                                    modify_title = ui.input(
                                        "Title", value=item["title"]
                                    ).classes("w-full")
                                    modify_desc = ui.textarea(
                                        "Url", value=item["description"]
                                    ).classes("w-full")
                                    # The lambda captures the item's specific data for the handler
                                    ui.button(
                                        "Save",
                                        on_click=lambda i=item,
                                        t=modify_title,
                                        d=modify_desc: update_item(
                                            i["id"], t, d, modify_dialog, grid
                                        ),
                                    ).classes("w-full text-white")
				#########################
                                with ui.link('', item["description"], new_tab=True):
                                  ui.label(item["title"]).classes("text-lg font-semibold text-white")
                                ui.button(
                                    icon="edit", on_click=modify_dialog.open
                                ).props("flat dense size=sm color=white")

                                # Delete Button - opens a confirmation dialog
                                with ui.dialog() as confirm_dialog, ui.card():
                                    ui.label(
                                        f"Are you sure you want to delete '{item['title']}'?"
                                    )
                                    with ui.row().classes("w-full justify-end"):
                                        ui.button(
                                            "Cancel",
                                            on_click=confirm_dialog.close,
                                            color="black",
                                        )
                                        # The lambda captures the specific item_id for the handler
                                        ui.button(
                                            "Yes",
                                            on_click=lambda item_id=item[
                                                "id"
                                            ]: delete_item(item_id, grid),
                                            color="red",
                                        )

                                ui.button(
                                    icon="delete", on_click=confirm_dialog.open
                                ).props("flat dense size=sm color=white")
        else:
            notifications.show_error("Failed to load items.")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")


async def create_item(
    title_input: ui.input,
    desc_input: ui.textarea,
    dialog_to_close: ui.dialog,
    items_grid: ui.grid,
):
    """Sends the new item data from the inputs to the API."""
    title_input.value = f'2/{title_input.value}'
    token = state.get_token()
    if not token:
        return
    data = {"title": title_input.value, "description": desc_input.value}
    title_input.value = ''
    headers = {"Authorization": token}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8000/api/v1/item/",
                json=data,
                headers=headers,
            )

        if response.status_code == 200:
            notifications.show_success("Link created successfully!")
            await load_items(items_grid)  # Pass the grid to the load function
            dialog_to_close.close()
        elif response.status_code == 409:
            notifications.show_error(f"Conflict: {response.json().get('detail')}")
        else:
            notifications.show_error(f"Error: {response.json().get('detail')}")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")


async def update_item(
    item_id: int,
    title_input: ui.input,
    desc_input: ui.textarea,
    dialog: ui.dialog,
    grid: ui.grid,
):
    """Makes an API call to update an item and reloads the grid on success."""
    token = state.get_token()
    if not token:
        return
    data = {"title": title_input.value, "description": desc_input.value}
    try:
        headers = {"Authorization": token}
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://127.0.0.1:8000/api/v1/item/{item_id}",
                json=data,
                headers=headers,
            )
        if response.status_code == 200:
            notifications.show_success("Link updated successfully.")
            dialog.close()
            await load_items(grid)
        else:
            notifications.show_error(f"Error: {response.json().get('detail')}")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")


async def delete_item(item_id: int, grid: ui.grid):
    """Makes an API call to delete an item and reloads the grid on success."""
    token = state.get_token()
    if not token:
        return
    try:
        headers = {"Authorization": token}
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://127.0.0.1:8000/api/v1/item/{item_id}", headers=headers
            )
        if response.status_code == 200:
            notifications.show_success("Link deleted successfully.")
            await load_items(grid)  # Refresh the items grid
        else:
            notifications.show_error(f"Error: {response.json().get('detail')}")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")


