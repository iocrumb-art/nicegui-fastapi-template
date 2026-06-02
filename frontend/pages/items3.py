import os
from nicegui import ui, app
from frontend import state
from frontend.components import notifications
from frontend.layouts.default import dashboard_frame
from nicegui import ui
from pathlib import Path
from nicegui import events

@ui.page("/items3", dark=True, reconnect_timeout=60)
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
        ui.timer(0.1, lambda: load_items(items_grid), once=True)

        async def handle_upload(e):
             await e.file.save(UPLOAD_DIR / e.file.name)
             ui.notify(f'Uploaded {e.file.name}')
             await load_items(items_grid)

        username = app.storage.user.get('username', 'Guest')
        UPLOAD_DIR = Path(__file__).parent / 'uploads' / f'{username}'
        #ui.label(f'saving files to: {UPLOAD_DIR}')
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        with ui.dialog() as dialog, ui.card().classes("min-w-[300px]"):
            ui.upload(on_upload=handle_upload, multiple=True)

        ui.button("Add File", on_click=dialog.open, icon="add").props(
            "color=primary"
        ).classes('text-bold p-5 mt-10 gap-2')



async def load_items(grid: ui.grid):
    """Fetches items from the API and populates the grid with cards, including action buttons."""
    token = state.get_token()
    if not token:
        return

    grid.clear()
    with grid:

        username = app.storage.user.get('username', 'Guest')
        UPLOAD_DIR = Path(__file__).parent / 'uploads' / f'{username}'

        directory = UPLOAD_DIR
        for file in directory.iterdir():
              with ui.card().classes("p-0 bg-transparent"):
                            with ui.grid(columns='auto 20px 30px').classes('w-full gap-0'):
                                # print filename
                                ui.label(file.name).classes("text-sm font-semibold text-white")

                                # download button
                                filelist=f'{UPLOAD_DIR / file.name}'
                                ui.button(
                                    icon="file_download", on_click=lambda filelist=filelist: ui.download(filelist)
                                ).props("flat dense size=sm color=white")

                                # delete button
                                ui.button(
                                    icon="delete", on_click=lambda filelist=filelist: (
                                       deldialog(filelist, grid)
                                )).props("flat dense size=sm color=white")



async def deldialog(item_id: int, grid: ui.grid):
    token = state.get_token()
    if not token:
        return
    with ui.dialog() as confirm_dialog, ui.card():
        ui.label(
           f"Are you sure you want to delete '{item_id}'?"
        )
        with ui.row().classes("w-full justify-end"):
            ui.button(
                "Cancel",
                on_click=confirm_dialog.close,
                color="black",
            )
            ui.button(
                "Yes",
                on_click=lambda:
                    del_item(item_id, grid),
                color="red",
            )
    confirm_dialog.open() 



async def del_item(item_id: int, grid: ui.grid):
    token = state.get_token()
    if not token:
        return
                               
    os.remove(item_id),
    ui.notify('File Deleted Successfully')
    await load_items(grid)



