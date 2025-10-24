import flet as ft


def main(page: ft.Page):
    page.add(
        ft.SafeArea(
            ft.Container(
                ft.Text("Hello, Mașinică!"),
                alignment=ft.alignment.center,
            ),
            expand=True,
        )
    )

ft.app(main)
