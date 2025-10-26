import flet as ft
from typing import List, Dict, Optional


def home_view(page: ft.Page) -> ft.View:
    page.title = "Mașinică - Vehicles"

    vehicles = ft.Column(spacing=20)

    no_vehicles_text = ft.Text(
        'No vehicles added yet.\nClick the "+" button to add a new vehicle.',
        size=20,
        italic=True,
        text_align=ft.TextAlign.CENTER,
    )
    helper_text = ft.Text(
        "Press and hold a vehicle to edit or delete it.",
        style=ft.TextStyle(color=page.theme.color_scheme.on_background),
        text_align=ft.TextAlign.CENTER,
        italic=True,
    )

    # --- storage helpers ---
    def _get_saved_vehicles() -> List[str]:
        return page.client_storage.get("vehicles") or []

    def _set_saved_vehicles(plates: List[str]) -> None:
        page.client_storage.set("vehicles", plates)

    def _get_saved_events() -> List[Dict]:
        return page.client_storage.get("events") or []

    def _set_saved_events(evts: List[Dict]) -> None:
        page.client_storage.set("events", evts)

    def delete_events(license_plate: str) -> None:
        new_events = [e for e in _get_saved_events() if e.get("vehicle") != license_plate]
        _set_saved_events(new_events)

    def save_vehicles() -> None:
        license_plates = [getattr(veh, "text", None) for veh in vehicles.controls]
        license_plates = [p for p in license_plates if p]
        _set_saved_vehicles(license_plates)

    def load_vehicles() -> None:
        vehicles.controls.clear()
        saved_vehicles = _get_saved_vehicles()
        for license_plate in saved_vehicles:
            vehicles.controls.append(create_vehicle(license_plate))

    def update_empty_state() -> None:
        saved_vehicles = _get_saved_vehicles()
        no_vehicles_text.visible = len(saved_vehicles) == 0
        helper_text.visible = len(saved_vehicles) > 0
        page.update()

    def open_vehicle(e: ft.ControlEvent) -> None:
        page.go(f"/vehicle/{e.control.text}")

    def create_vehicle(label: str) -> ft.Control:
        return ft.ElevatedButton(
            icon=ft.Icons.DIRECTIONS_CAR,
            text=label,
            width=page.width * 0.8,
            height=50,
            on_click=open_vehicle,
            on_long_press=open_edit_vehicle_dialog,
        )

    def add_vehicle(label: str) -> None:
        vehicles.controls.append(create_vehicle(label))
        save_vehicles()
        update_empty_state()
        page.update()

    # New vehicle dialog
    license_plate_input = ft.TextField(
        label="Enter license plate number",
        autofocus=True,
        capitalization=ft.TextCapitalization.CHARACTERS,
    )

    new_vehicle_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Vehicle"),
        content=license_plate_input,
    )

    def close_new_vehicle_dialog(e: Optional[ft.ControlEvent] = None) -> None:
        page.close(new_vehicle_dialog)

    def confirm_add_vehicle(e: Optional[ft.ControlEvent] = None) -> None:
        value = (license_plate_input.value or "").strip()
        if not value:
            license_plate_input.error_text = "License plate\ncannot be empty."
            page.update()
            return

        saved_vehicles = _get_saved_vehicles()
        if value in saved_vehicles:
            license_plate_input.error_text = "Vehicle already exists."
            page.update()
            return

        license_plate_input.error_text = None
        add_vehicle(value)
        close_new_vehicle_dialog()

    new_vehicle_dialog.actions = [
        ft.TextButton("Cancel", on_click=close_new_vehicle_dialog),
        ft.TextButton("Add", on_click=confirm_add_vehicle),
    ]

    def open_new_vehicle_dialog(e: ft.ControlEvent) -> None:
        license_plate_input.value = ""
        license_plate_input.error_text = None
        page.open(new_vehicle_dialog)

    # Edit vehicle dialog
    def open_edit_vehicle_dialog(e: ft.ControlEvent) -> None:
        vehicle_button = e.control
        old_label = vehicle_button.text

        edit_license_plate_input = ft.TextField(
            label="Edit license plate number",
            value=old_label,
            autofocus=True,
            capitalization=ft.TextCapitalization.CHARACTERS,
        )

        edit_vehicle_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Vehicle"),
            content=edit_license_plate_input,
        )

        def close_edit_vehicle_dialog(ev: Optional[ft.ControlEvent] = None) -> None:
            page.close(edit_vehicle_dialog)

        def confirm_edit_vehicle(ev: Optional[ft.ControlEvent] = None) -> None:
            new_label = (edit_license_plate_input.value or "").strip()
            if not new_label:
                edit_license_plate_input.error_text = "License plate cannot be empty."
                page.update()
                return

            saved_vehicles = _get_saved_vehicles()
            # If new_label already exists (and isn't the same as old), show error
            if new_label in saved_vehicles and new_label != old_label:
                edit_license_plate_input.error_text = "Another vehicle with this plate\nalready exists."
                page.update()
                return

            # Update the button text
            vehicle_button.text = new_label

            # Update saved vehicles list order and persist
            plates = [getattr(veh, "text", None) for veh in vehicles.controls]
            plates = [p for p in plates if p]
            _set_saved_vehicles(plates)

            # Update events related to this vehicle (rename vehicle tag)
            evts = _get_saved_events()
            changed = False
            for item in evts:
                if item.get("vehicle") == old_label:
                    item["vehicle"] = new_label
                    changed = True
            if changed:
                _set_saved_events(evts)

            page.update()
            close_edit_vehicle_dialog()

        def delete_vehicle(ev: Optional[ft.ControlEvent] = None) -> None:
            # Capture label before mutating controls
            label_to_remove = old_label
            vehicles.controls[:] = [veh for veh in vehicles.controls if getattr(veh, "text", None) != label_to_remove]
            delete_events(label_to_remove)
            save_vehicles()
            update_empty_state()
            page.update()
            close_edit_vehicle_dialog()
            page.close(confirm_delete_vehicle_dialog)

        confirm_delete_vehicle_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Vehicle"),
            content=ft.Text(f'Are you sure you want to delete vehicle "{old_label}" and all its events?'),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: page.close(confirm_delete_vehicle_dialog)),
                ft.TextButton(
                    "Delete",
                    on_click=delete_vehicle,
                    style=ft.ButtonStyle(color=page.theme.color_scheme.error),
                ),
            ],
        )

        edit_vehicle_dialog.actions = [
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=page.theme.color_scheme.error,
                        on_click=lambda _: page.open(confirm_delete_vehicle_dialog),
                    ),
                    ft.Container(expand=True),
                    ft.TextButton("Cancel", on_click=close_edit_vehicle_dialog),
                    ft.TextButton("Save", on_click=confirm_edit_vehicle),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]

        page.open(edit_vehicle_dialog)

    def on_resize(e: ft.ControlEvent) -> None:
        for veh in vehicles.controls:
            try:
                veh.width = page.width * 0.8
            except Exception:
                pass
        page.update()

    page.on_resize = on_resize

    load_vehicles()
    update_empty_state()

    return ft.View(
        "/",
        controls=[
            ft.SafeArea(
                ft.Stack(
                    [
                        ft.Container(
                            content=no_vehicles_text,
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                        ft.Container(
                            content=vehicles,
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
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
                leading=ft.Icon(ft.Icons.HOME),
            ),
        ],
        floating_action_button=ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=open_new_vehicle_dialog,
        ),
    )