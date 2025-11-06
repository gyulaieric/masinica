import flet as ft
import flet_permission_handler as fph
from themes.catppuccin_theme import catppuccin_theme
from views.home_view import home_view
from views.vehicle_view import vehicle_view
from views.event_view import event_view

def main(page: ft.Page):
    page.theme = catppuccin_theme("light")
    page.dark_theme = catppuccin_theme("dark")

    ph = fph.PermissionHandler()
    page.overlay.append(ph)
    page.update()

    async def open_app_settings(e):
        await ph.open_app_settings_async()
        page.go("/")

    permission_dialog = ft.AlertDialog(
        modal=True,
        title= ft.Row(
            [
                ft.Icon(name=ft.Icons.NOTIFICATIONS),
                ft.Text("Notifications"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        content=ft.Text(
            "Mașinică requires notification access to give you reminders when your vehicle's documents expire.\n\nPlease make sure notifications are enabled.",
            text_align=ft.TextAlign.JUSTIFY,
        ),
        actions=[
            ft.TextButton(
                "Open settings",
                on_click=open_app_settings,
            ),
        ],
    )

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page))
        elif page.route.startswith("/vehicle/"):
            parts = page.route.split("/vehicle/")[1].split("/")
            license_plate = parts[0]
            if len(parts) == 1:
                page.views.append(vehicle_view(page, license_plate))
            else:
                event_type = parts[1]
                page.views.append(event_view(page, license_plate, event_type))
        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if page.client_storage.get("first_launch") is None:
        page.open(permission_dialog)
        page.client_storage.set("first_launch", False)
    else:
        page.go("/")

ft.app(main)
