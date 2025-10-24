import flet as ft

from views.home_view import home_view

def main(page: ft.Page):
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page))
        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

ft.app(main)
