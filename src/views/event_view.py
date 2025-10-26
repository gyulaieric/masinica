from datetime import datetime, date
from typing import Optional, List, Dict
import flet as ft


def event_view(page: ft.Page, license_plate: str, event_type: str) -> ft.View:
    page.title = f"Mașinică - {license_plate} - {event_type}"

    # --- storage helpers ---
    def _get_saved_events() -> List[Dict]:
        return page.client_storage.get("events") or []
    
    def _get_saved_event() -> Optional[Dict]:
        evts = _get_saved_events()
        for evt in evts:
            if evt.get("vehicle") == license_plate and evt.get("label") == event_type:
                return evt
        return None

    def _set_saved_events(evts: List[Dict]) -> None:
        page.client_storage.set("events", evts)

    event = _get_saved_event()
    if event is None:
        page.go(f"/vehicle/{license_plate}")
        return
    
    def save_event(label: str, expiration_date: date) -> None:
        evts = _get_saved_events()
        for evt in evts:
            if evt.get("vehicle") == license_plate and evt.get("label") == label:
                evt["expiration_date"] = expiration_date.isoformat()
                break
        _set_saved_events(evts)
        page.go(f"/vehicle/{license_plate}")

    def delete_event(label: str) -> None:
        evts = _get_saved_events()
        evts = [evt for evt in evts if not (evt.get("vehicle") == license_plate and evt.get("label") == label)]
        _set_saved_events(evts)
        page.go(f"/vehicle/{license_plate}")
    
    selected_date: Optional[date] = None

    def update_date(e: ft.ControlEvent) -> None:
        nonlocal selected_date
        selected_date = e.control.value
        date_picker.bgcolor = None
        date_picker.style = None
        date_picker.text = f"{selected_date.strftime('%d/%m/%Y')}"
        page.update()

    date_picker = ft.ElevatedButton(
        text=f"{selected_date or datetime.fromisoformat(event.get('expiration_date')).strftime('%d/%m/%Y')}",
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: page.open(
            ft.DatePicker(
                value=selected_date or datetime.fromisoformat(event.get('expiration_date')),
                first_date=datetime(year=2000, month=1, day=1),
                last_date=datetime(year=9999, month=12, day=31),
                on_change=update_date,
            )
        ),
    )

    delete_event_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete Event"),
        content=ft.Text(f'Are you sure you want to delete "{event_type}" for "{license_plate}"?'),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close(delete_event_dialog)),
            ft.TextButton(
                "Delete",
                on_click=lambda e: delete_event(event_type),
                style=ft.ButtonStyle(color=page.theme.color_scheme.error),
            ),
        ],
    )

    def open_delete_event_dialog(e: ft.ControlEvent) -> None:
        page.open(delete_event_dialog)
    
    # --- UI helpers ---
    def _remaining_days_text(days: int) -> str:
        text = Optional[str]
        color = Optional[ft.ColorValue]

        if days <= 3:
            color = page.theme.color_scheme.error
        elif days <= 15:
            color = page.theme.color_scheme.tertiary
        else:
            color = page.theme.color_scheme.secondary

        if days < 0:
            text = f"Expired {-days} day{'' if days == -1 else 's'} ago."
        else:
            text = f"{days} day{'' if days == 1 else 's'} left."

        return ft.Text(
            text,
            size=20,
            color=color,
        )

    return ft.View(
        f"/vehicle/{license_plate}/{event_type}",
        [
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                f"{event.get('label')}:",
                                size=20,
                            ),
                            _remaining_days_text((datetime.fromisoformat(event.get('expiration_date')).date() - datetime.now().date()).days),
                        ],  
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                "Expiration Date:",
                            ),
                            date_picker,
                        ],
                    ),
                    ft.Text(
                        "(Tap the calendar to change the date)",
                        italic=True,
                        size=14,
                        color=page.theme.color_scheme.on_background,
                    ),
                ],
                alignment=ft.alignment.center,
                expand=True,
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Delete",
                            icon=ft.Icons.DELETE,
                            color=page.theme.color_scheme.error,
                            icon_color=page.theme.color_scheme.error,
                            on_click=open_delete_event_dialog,
                        ),
                        ft.ElevatedButton(
                            text="Save",
                            icon=ft.Icons.SAVE,
                            on_click=lambda e: save_event(event.get("label"), selected_date or datetime.fromisoformat(event.get('expiration_date'))),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.only(bottom=20),
            ),
            ft.AppBar(
                title=ft.Text(f"{license_plate} - {event_type}"),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: page.go(f"/vehicle/{license_plate}"),
                ),
            ),
        ],
    )
