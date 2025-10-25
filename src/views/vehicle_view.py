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

    def save_event(label, expiration_date):
        saved_events = page.client_storage.get("events") or []
        saved_events.append({
            "vehicle": license_plate,
            "label": label,
            "expiration_date": expiration_date.isoformat(),
        })
        page.client_storage.set("events", saved_events)

    def load_events():
        saved_events = page.client_storage.get("events") or []
        for e in saved_events:
            if e["vehicle"] != license_plate:
                continue
            label = e["label"]
            expiration_date = datetime.fromisoformat(e["expiration_date"])
            events.controls.append(create_event(label, expiration_date))

    def update_empty_state():
        saved_events = [e for e in page.client_storage.get("events") or [] if e["vehicle"] == license_plate] or []
        no_events_text.visible = len(saved_events) == 0
        page.update()

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
        save_event(label, expiration_date)
        events.controls.append(create_event(label, expiration_date))
        update_empty_state()
        page.update()


    def update_event_dropdown(e):
        e.control.error_text = None
        page.update()
        
    event_dropdown = ft.Dropdown(
        label="Event Type",
        options=[
            ft.dropdown.Option("RCA"),
            ft.dropdown.Option("CASCO"),
            ft.dropdown.Option("ITP"),
            ft.dropdown.Option("ROVINIETA"),
        ],
        on_change=update_event_dropdown,
    )

    def update_date(e):
        nonlocal selected_date
        selected_date = e.control.value
        date_picker.bgcolor = None
        date_picker.style = None
        date_picker.text = f"{e.control.value.strftime('%d/%m/%Y')}"
        page.update()

    date_picker = ft.ElevatedButton(
            text="Select expiration date.",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.open(
                ft.DatePicker(
                    first_date=datetime.today(),
                    last_date=datetime(year=9999, month=12, day=31),
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
            ],
            tight=True,
        ),
    )

    def close_add_event_dialog(e=None):
        page.close(add_event_dialog)

    def confirm_add_event(e=None):
        if event_dropdown.value is None:
            event_dropdown.error_text = "Please select\nan event type."
            page.update()
            return
        label = event_dropdown.value.strip()

        for event in page.client_storage.get("events") or []:
            if event["label"] == label and event["vehicle"] == license_plate:
                event_dropdown.error_text = f"{label} already exists\nfor this vehicle."
                page.update()
                return

        if selected_date is None:
            date_picker.text = "Please select an expiration date."
            date_picker.bgcolor = page.theme.color_scheme.error
            date_picker.style = ft.ButtonStyle(
                color=page.theme.color_scheme.on_error,
                icon_color=page.theme.color_scheme.on_error
            )
            page.update()
            return
            
        add_event(label, selected_date)
        close_add_event_dialog()

    add_event_dialog.actions = [
        ft.TextButton("Cancel", on_click=close_add_event_dialog),
        ft.TextButton("Add", on_click=confirm_add_event),
    ]

    def open_add_event_dialog(e):
        event_dropdown.value = None
        event_dropdown.error_text = None
        nonlocal selected_date
        selected_date = None
        date_picker.text = "Select expiration date."
        date_picker.bgcolor = None
        date_picker.style = None
        page.open(add_event_dialog)

    def on_resize(e):
        for veh in events.controls:
            veh.width = page.width * 0.8
        page.update()
    page.on_resize = on_resize

    load_events()
    update_empty_state()

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
            ft.AppBar(
                title=ft.Text(license_plate),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
            ),
        ],
        floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=open_add_event_dialog,
        ),
    )