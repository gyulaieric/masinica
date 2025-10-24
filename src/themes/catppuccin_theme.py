import flet as ft
from themes.palettes.catppuccin import latte, mocha

def catppuccin_theme(theme_mode: str) -> ft.Theme:
    flavor = mocha if theme_mode == "dark" else latte
    primary_color = flavor["mauve"]
    secondary_color = flavor["pink"]
    text_color = flavor["text"]

    return ft.Theme(
        appbar_theme=ft.AppBarTheme(
            elevation=0,
            title_text_style=ft.TextStyle(
                color=text_color,
                size=20,
                weight=ft.FontWeight.BOLD,
            ),
            bgcolor=flavor["crust"],
            foreground_color=text_color,
        ),
        color_scheme=ft.ColorScheme(
            primary=primary_color,
            on_primary=flavor["base"],
            secondary=secondary_color,
            on_secondary=flavor["base"],
            tertiary=flavor["green"],
            on_tertiary=flavor["base"],
            surface=flavor["mantle"],
            on_surface=text_color,
            surface_variant=flavor["surface0"],
            on_surface_variant=flavor["subtext0"],
            background=flavor["base"],
            on_background=text_color,
            error=flavor["red"],
            on_error=flavor["base"],
            outline=flavor["overlay0"],
            shadow=flavor["crust"],
            inverse_surface=flavor["crust"],
            on_inverse_surface=flavor["subtext1"],
            surface_tint=primary_color,
        ),
        text_theme=ft.TextTheme(
            body_small=ft.TextStyle(color=text_color),
            body_medium=ft.TextStyle(color=text_color),
            body_large=ft.TextStyle(color=text_color),
            display_small=ft.TextStyle(color=primary_color),
            display_medium=ft.TextStyle(color=primary_color),
            display_large=ft.TextStyle(color=primary_color),
        ),
        floating_action_button_theme=ft.FloatingActionButtonTheme(
            bgcolor=flavor["base"],
            foreground_color=primary_color,
        ),
    )
