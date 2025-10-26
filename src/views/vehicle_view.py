from datetime import datetime, date
from typing import Optional, List, Dict
import flet as ft


def vehicle_view(page: ft.Page, license_plate: str) -> ft.View:
    page.title = f"Mașinică - {license_plate}"

    events = ft.Column(spacing=20)
    selected_date: Optional[date] = None

    no_events_text = ft.Text(
        'No events added yet.\nClick the "+" button to add a new event.',
        size=20,
        italic=True,
        text_align=ft.TextAlign.CENTER,
    )
    helper_text = ft.Text(
        "Tap an event to view or edit it.",
        style=ft.TextStyle(color=page.theme.color_scheme.on_background),
        text_align=ft.TextAlign.CENTER,
        italic=True,
    )

    # --- storage helpers ---
    def _get_saved_events() -> List[Dict]:
        return page.client_storage.get("events") or []

    def _set_saved_events(evts: List[Dict]) -> None:
        page.client_storage.set("events", evts)

    def save_event(label: str, expiration_date: date) -> None:
        evts = _get_saved_events()
        evts.append({
            "vehicle": license_plate,
            "label": label,
            "expiration_date": expiration_date.isoformat(),
        })
        _set_saved_events(evts)

    # --- UI helpers ---
    def _badge_text(days: int) -> str:
        return f"{days} day" + ('' if abs(days) == 1 else 's')

    def create_event(label: str, expiration_dt: datetime) -> ft.Control:
        remaining_days = (expiration_dt.date() - datetime.now().date()).days
        badge_color = None
        if remaining_days <= 3:
            badge_color = page.theme.color_scheme.error
        elif remaining_days <= 15:
            badge_color = page.theme.color_scheme.tertiary

        return ft.ElevatedButton(
            text=label,
            badge=ft.Badge(
                _badge_text(remaining_days),
                bgcolor=badge_color,
                alignment=ft.alignment.center_right,
                offset=(-60, -8),
            ),
            width=page.width * 0.8,
            height=50,
            on_click=lambda e: page.go(f"/vehicle/{license_plate}/{label}"),
        )

    def load_events() -> None:
        events.controls.clear()
        for e in _get_saved_events():
            if e.get("vehicle") != license_plate:
                continue
            label = e.get("label")
            expiration_date = datetime.fromisoformat(e.get("expiration_date"))
            events.controls.append(create_event(label, expiration_date))

    def update_empty_state() -> None:
        has = any(e.get("vehicle") == license_plate for e in _get_saved_events())
        no_events_text.visible = not has
        helper_text.visible = has
        page.update()

    # --- event dialog controls ---
    def on_event_dropdown_change(e: ft.ControlEvent) -> None:
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
        on_change=on_event_dropdown_change,
    )

    def update_date(e: ft.ControlEvent) -> None:
        nonlocal selected_date
        selected_date = e.control.value
        date_picker.bgcolor = None
        date_picker.style = None
        date_picker.text = f"{selected_date.strftime('%d/%m/%Y')}"
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
        content=ft.Column([event_dropdown, date_picker], tight=True),
    )

    def close_add_event_dialog(e: ft.ControlEvent | None = None) -> None:
        page.close(add_event_dialog)

    def confirm_add_event(e: ft.ControlEvent | None = None) -> None:
        nonlocal selected_date
        if event_dropdown.value is None:
            event_dropdown.error_text = "Please select\nan event type."
            page.update()
            return

        label = event_dropdown.value.strip()

        for ev in _get_saved_events():
            if ev.get("label") == label and ev.get("vehicle") == license_plate:
                event_dropdown.error_text = f"{label} already exists\nfor this vehicle."
                page.update()
                return

        if selected_date is None:
            date_picker.text = "Please select an expiration date."
            date_picker.bgcolor = page.theme.color_scheme.error
            date_picker.style = ft.ButtonStyle(
                color=page.theme.color_scheme.on_error,
                icon_color=page.theme.color_scheme.on_error,
            )
            page.update()
            return

        save_event(label, selected_date)
        events.controls.append(create_event(label, datetime.fromisoformat(selected_date.isoformat())))
        update_empty_state()
        page.update()
        close_add_event_dialog()

    add_event_dialog.actions = [
        ft.TextButton("Cancel", on_click=close_add_event_dialog),
        ft.TextButton("Add", on_click=confirm_add_event),
    ]

    def open_add_event_dialog(e: ft.ControlEvent) -> None:
        nonlocal selected_date
        event_dropdown.value = None
        event_dropdown.error_text = None
        selected_date = None
        date_picker.text = "Select expiration date."
        date_picker.bgcolor = None
        date_picker.style = None
        page.open(add_event_dialog)

    def on_resize(e: ft.ControlEvent) -> None:
        for veh in events.controls:
            try:
                veh.width = page.width * 0.8
            except Exception:
                pass
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
                        ft.Container(content=no_events_text, alignment=ft.alignment.center, expand=True),
                        ft.Container(content=events, alignment=ft.alignment.center, expand=True),
                    ],
                ),
                expand=True,
            ),
            ft.Container(
                content=(helper_text),
                alignment=ft.alignment.bottom_center,
                padding=ft.padding.only(bottom=60),
            ),
            ft.AppBar(
                title=ft.Text(license_plate),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
            ),
        ],
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=open_add_event_dialog,
        ),
    )