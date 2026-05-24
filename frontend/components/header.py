from nicegui import ui, app
from frontend import state
from frontend.state import clear_auth


def create_header(left_drawer: ui.left_drawer, title: str) -> None:
    """Creates the application header."""

    if not state.get_auth():
        ui.navigate.to("/login")
        return

    async def handle_logout():
        clear_auth()
        app.storage.user.clear()
        ui.navigate.to("/login")
   
    with ui.header(elevated=True).classes("items-center justify-between bg-slate-700"):
       path = ui.context.client.sub_pages_router.current_path

       match path:
           case '/landing':
               if not app.storage.user.get("is_superuser"):
                   ui.button('1/Notes', on_click=lambda: ui.navigate.to("/items")).classes('p-4').props('flat')
                   ui.button('2/Links', on_click=lambda: ui.navigate.to("/items2")).classes('p-4').props('flat')
                   ui.button('3/Files', on_click=lambda: ui.navigate.to("/items3")).classes('p-4').props('flat')
       
           case '/items':
               ui.button('1/Notes', on_click=lambda: ui.navigate.to("/items")).classes('p-4').props('outline')
               ui.button('2/Links', on_click=lambda: ui.navigate.to("/items2")).classes('p-4').props('flat')
               ui.button('3/Files', on_click=lambda: ui.navigate.to("/items3")).classes('p-4').props('flat')

           case '/items2':
               ui.button('1/Notes', on_click=lambda: ui.navigate.to("/items")).classes('p-4').props('flat')
               ui.button('2/Links', on_click=lambda: ui.navigate.to("/items2")).classes('p-4').props('outline')
               ui.button('3/Files', on_click=lambda: ui.navigate.to("/items3")).classes('p-4').props('flat')
           
           case '/items3':
               ui.button('1/Notes', on_click=lambda: ui.navigate.to("/items")).classes('p-4').props('flat')
               ui.button('2/Links', on_click=lambda: ui.navigate.to("/items2")).classes('p-4').props('flat')
               ui.button('3/Files', on_click=lambda: ui.navigate.to("/items3")).classes('p-4').props('outline')

       ui.button(on_click=handle_logout, icon='logout').classes('p-4').props('flat')

