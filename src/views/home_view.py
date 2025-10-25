import flet as ft
def home_view(page: ft.Page):
    page.title = "Mașinică - Vehicles"

    vehicles = ft.Column(spacing=20)
    vehicle_count = 0

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

    def delete_events(license_plate):
        new_events = [e for e in page.client_storage.get("events") or [] if e["vehicle"] != license_plate]
        page.client_storage.set("events", new_events)

    def save_vehicles():
        license_plates = [veh.text for veh in vehicles.controls]
        page.client_storage.set("vehicles", license_plates)

    def load_vehicles():
        saved_vehicles = page.client_storage.get("vehicles") or []
        for license_plate in saved_vehicles:
            vehicles.controls.append(create_vehicle(license_plate))

    def update_empty_state():
        saved_vehicles = page.client_storage.get("vehicles") or []
        no_vehicles_text.visible = len(saved_vehicles) == 0
        helper_text.visible = len(saved_vehicles) > 0
        page.update()

    def open_vehicle(e):
        page.go(f"/vehicle/{e.control.text}")

    def create_vehicle(label):
        return ft.ElevatedButton(
            icon=ft.Icons.DIRECTIONS_CAR,
            text=label,
            width=page.width * 0.8,
            height=50,
            on_click=open_vehicle,
            on_long_press=open_edit_vehicle_dialog,
        )
    
    def add_vehicle(label):
        nonlocal vehicle_count
        vehicle_count += 1
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

    def close_new_vehicle_dialog(e=None):
        page.close(new_vehicle_dialog)

    def confirm_add_vehicle(e=None):
        label = license_plate_input.value.strip()
        if label:
            if label in page.client_storage.get("vehicles"):
                license_plate_input.error_text = "Vehicle already exists."
                page.update()
                return
            license_plate_input.error_text = None
            add_vehicle(label)
        close_new_vehicle_dialog()

    new_vehicle_dialog.actions = [
        ft.TextButton("Cancel", on_click=close_new_vehicle_dialog),
        ft.TextButton("Add", on_click=confirm_add_vehicle),
    ]

    def open_new_vehicle_dialog(e):
        license_plate_input.value = ""
        page.open(new_vehicle_dialog)
    
    # Edit vehicle dialog
    def open_edit_vehicle_dialog(e):
        vehicle_button = e.control

        edit_license_plate_input = ft.TextField(
            label="Edit license plate number",
            value=vehicle_button.text,
            autofocus=True,
            capitalization=ft.TextCapitalization.CHARACTERS,
        )

        edit_vehicle_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Vehicle"),
            content=edit_license_plate_input,
        )

        def close_edit_vehicle_dialog(e=None):
            page.close(edit_vehicle_dialog)

        def confirm_edit_vehicle(e=None):
            new_label = edit_license_plate_input.value.strip()
            if new_label:
                vehicle_button.text = new_label
                page.update()
            close_edit_vehicle_dialog()
        
        def delete_vehicle(e=None):
            vehicles.controls.remove(vehicle_button)
            nonlocal vehicle_count
            vehicle_count -= 1
            vehicles.controls = [veh for veh in vehicles.controls if veh.text != vehicle_button.text]
            delete_events(vehicle_button.text)
            save_vehicles()
            update_empty_state()
            page.update()
            close_edit_vehicle_dialog() 

        edit_vehicle_dialog.actions = [
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=page.theme.color_scheme.error,
                        on_click=delete_vehicle
                        ),
                    ft.Container(expand=True),
                    ft.TextButton("Cancel", on_click=close_edit_vehicle_dialog),
                    ft.TextButton("Save", on_click=confirm_edit_vehicle),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]

        page.open(edit_vehicle_dialog)

    def on_resize(e):
        for veh in vehicles.controls:
            veh.width = page.width * 0.8
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
        floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=open_new_vehicle_dialog,
        ),
    )