from nicegui import ui


def create_footer() -> None:
    """Creates the application footer."""
    with ui.footer(elevated=True).classes(
        "bg-slate-700 text-white items-center justify-center p-1"
    ):
         ui.link('HOME', target='/landing').classes('text-white')
         ui.label("    © 2026 All rights reserved.")
