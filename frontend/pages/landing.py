import httpx
from nicegui import ui, app
from frontend import state
from frontend.components import notifications
from frontend.layouts.default import dashboard_frame
from nicegui import ui
from pathlib import Path

@ui.page("/landing", dark=True)
def landing_page():
    """Defines the page for displaying and creating user items."""
    static_files_dir = Path(__file__).parent / 'static'
    static_files_dir.mkdir(exist_ok=True) 
    app.add_static_files('/static', static_files_dir.as_posix())

    with dashboard_frame(title="Welcome"):
        ui.query('.nicegui-content').classes('p-0')

        with ui.row().classes('h-screen w-screen bg-gray-900 bg-cover bg-center bg-no-repeat').style('background-image: url("/static/id660.jpg")'):
            ui.label('').classes('text-white text-xl mx-auto my-auto')

