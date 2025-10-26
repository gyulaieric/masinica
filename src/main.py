import flet as ft
from themes.catppuccin_theme import catppuccin_theme
from views.home_view import home_view
from views.vehicle_view import vehicle_view
from views.event_view import event_view

def main(page: ft.Page):
    page.theme = catppuccin_theme("light")
    page.dark_theme = catppuccin_theme("dark")

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
    page.go("/")

ft.app(main)
