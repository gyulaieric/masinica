import flet as ft
from themes.catppuccin_theme import catppuccin_theme
from views.home_view import home_view
from views.vehicle_view import vehicle_view

def main(page: ft.Page):
    page.theme = catppuccin_theme("light")
    page.dark_theme = catppuccin_theme("dark")
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page))
        elif page.route.startswith("/vehicle/"):
            license_plate = page.route.split("/vehicle/")[-1]
            page.views.append(vehicle_view(page, license_plate))
        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

ft.app(main)
