from datetime import datetime
import flet as ft

def vehicle_view(page: ft.Page, license_plate: str):
    page.title = f"Mașinică - {license_plate}"

    events = ft.Column(spacing=20)
    event_count = 0

    selected_date = None

    no_events_text = ft.Text(
        'No events added yet.\nClick the "+" button to add a new event.',
        size=20,
        italic=True,
        text_align=ft.TextAlign.CENTER,
    )

    def create_event(label, expiration_date):
        remaining_days = (expiration_date - datetime.now()).days + 1
        badge_color = None
        if remaining_days <= 3:
            badge_color = page.theme.color_scheme.error
        elif remaining_days <= 15:
            badge_color = page.theme.color_scheme.tertiary
        return ft.ElevatedButton(
            text=label,
            badge=ft.Badge(
                f"{remaining_days}" + (" day" if remaining_days == 1 or remaining_days == -1 else " days"),
                bgcolor=badge_color,
                alignment=ft.alignment.center_right,
                offset=(-60,-8),
            ),
            width=page.width * 0.8,
            height=50,
        )
    
    def add_event(label, expiration_date):
        nonlocal event_count
        event_count += 1
        events.controls.append(create_event(label, expiration_date))
        no_events_text.visible = event_count == 0
        page.update()

    event_dropdown = ft.Dropdown(
        label="Event Type",
        options=[
            ft.dropdown.Option("RCA"),
            ft.dropdown.Option("CASCO"),
            ft.dropdown.Option("ITP"),
            ft.dropdown.Option("ROVINIETA"),
        ]
    )

    selected_date_label = ft.Text("Selected date: Please select.")
    def update_date(e):
        nonlocal selected_date, selected_date_label
        selected_date = e.control.value
        selected_date_label.value = f"Selected date: {e.control.value.strftime('%d/%m/%Y')}"
        page.update()

    date_picker = ft.ElevatedButton(
            "Pick expiration date",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.open(
                ft.DatePicker(
                    first_date=datetime(year=2000, month=1, day=1),
                    last_date=datetime(year=3000, month=12, day=31),
                    on_change=update_date,
                )
            ),
        )
    
    add_event_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Event"),
        content=ft.Column(
            [
                event_dropdown,
                date_picker,
                selected_date_label,
            ],
            tight=True,
        ),
    )

    def close_add_event_dialog(e=None):
        page.close(add_event_dialog)

    def confirm_add_event(e=None):
        label = event_dropdown.value.strip()
        if label:
            add_event(label, selected_date)
        close_add_event_dialog()

    add_event_dialog.actions = [
        ft.TextButton("Cancel", on_click=close_add_event_dialog),
        ft.TextButton("Add", on_click=confirm_add_event),
    ]

    def open_add_event_dialog(e):
        page.open(add_event_dialog)

    def on_resize(e):
        for veh in events.controls:
            veh.width = page.width * 0.8
        page.update()
    page.on_resize = on_resize

    return ft.View(
        f"/vehicle/{license_plate}",
        controls=[
            ft.SafeArea(
                ft.Stack(
                    [
                        ft.Container(
                            content=no_events_text,
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                        ft.Container(
                            content=events,
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                    ],
                ),
                expand=True,
            ),
        ],
        floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=open_add_event_dialog,
        ),
    )