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

    def create_vehicle(label):
        return ft.ElevatedButton(
            icon=ft.Icons.DIRECTIONS_CAR,
            text=label,
            width=page.width * 0.8,
            height=50,
        )
    
    def add_vehicle(label):
        nonlocal vehicle_count
        vehicle_count += 1
        vehicles.controls.append(create_vehicle(label))
        no_vehicles_text.visible = vehicle_count == 0
        page.update()

    label_input = ft.TextField(
        label="Enter license plate number",
        autofocus=True,
        capitalization=ft.TextCapitalization.CHARACTERS,
    )
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Vehicle"),
        content=label_input,
    )

    def close_dialog(e=None):
        page.close(dialog)

    def confirm_add_vehicle(e=None):
        label = label_input.value.strip()
        if label:
            add_vehicle(label)
        close_dialog()

    dialog.actions = [
        ft.TextButton("Cancel", on_click=close_dialog),
        ft.TextButton("Add", on_click=confirm_add_vehicle),
    ]

    def open_dialog(e):
        label_input.value = ""
        page.open(dialog)

    def on_resize(e):
        for veh in vehicles.controls:
            veh.width = page.width * 0.8
        page.update()
    page.on_resize = on_resize

    return ft.View(
        "/",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=no_vehicles_text,
                    alignment=ft.alignment.center,
                ),
            ),
            ft.SafeArea(
                ft.Container(
                    content=vehicles,
                    alignment=ft.alignment.center,
                ),
                expand=True,
            ),
        ],
        floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=open_dialog,
        ),
    )