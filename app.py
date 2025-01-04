import flet as ft
import flet.map as map
from flet.auth.providers import GoogleOAuthProvider
import geocoder
from dotenv import load_dotenv
import os
import json

load_dotenv()
clientID = os.getenv('clientID')
clientSecret = os.getenv('clientSecret')

def main(page: ft.Page):
    dlg = None
    selected_marker = None

    try:
        g = geocoder.ip("me")
        current_lat = g.latlng[0]
        current_lon = g.latlng[1]
    except:
        current_lat = 36.188110
        current_lon = -115.176468


    marker_layer_ref = ft.Ref[map.MarkerLayer]()
    map_ref = ft.Ref[map.Map]()

    with open("marker_info.json", "r") as f:
        marker_info = json.load(f)

    page.bgcolor = ft.Colors.WHITE
    page.theme_mode = "light"

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    provider = GoogleOAuthProvider(
        client_id = clientID,
        client_secret = clientSecret,
        redirect_url = "https://stuntguru.me/oauth_callback"
    )

    def logingoogle(e):
        page.login(provider)

    def on_login(e):
        global credentials
        credentials = {"Name": page.auth.user['given_name'], "Family_Name": page.auth.user['family_name'], "Picture": page.auth.user['picture'], "Email": page.auth.user['email']}
        toggle_login_buttons()
        if page.auth.user['email'] == os.getenv('admin_email'):
            edit_markers_button.visible = True
        else:
            edit_markers_button.visible = False
        page.update()


    def logoutgoogle(e):
        page.logout()

    def on_logout(e):
        toggle_login_buttons()

    def toggle_login_buttons():
        login_button.visible = page.auth is None
        logout_button.visible = page.auth is not None
        page.update()

    def submit_change(e, values, dest):
        global dlg
        for _, marker in marker_info.items():
            if marker["name"] == dest:
                marker["name"] = values[0]
                marker["contact"] = values[1]
                marker["image"] = values[2]
                marker["rating"] = values[3]
                marker["coordinates"] = values[4]
                break

        with open("marker_info.json", "w") as f:
            json.dump(marker_info, f, indent=4)

        page.close(dlg)
        marker_layer_ref.current.markers = [map.Marker(
                            content=ft.IconButton(ft.Icons.LOCATION_ON, icon_color = ft.Colors.RED, icon_size = 45, on_click=lambda e, values=[marker["coordinates"][0], marker["coordinates"][1], marker["name"], marker["image"], marker["contact"], marker["coordinates"], marker["rating"]]: handle_marker_tap(e, values)),
                            coordinates=map.MapLatitudeLongitude(marker["coordinates"][0], marker["coordinates"][1])
                        ) for marker in marker_info.values()]
        page.update()

        anchor_searchbar.controls.clear()
        anchor_searchbar.controls = [ft.ListTile(title = ft.Text(list(marker_info.values())[i]['name']), on_click = close_anchor, data = i) for i in range(len(marker_info))]
        anchor_searchbar.update()

    def change_coordinates(e, dest):
        global selected_marker
        close_dialog(None)

        selected_marker = dest
        page.update()

    def return_value(e):
        global dropdown
        global dlg
        dest = e.control.value

        for marker in marker_info.values():
            if marker["name"] == dest:
                values = [marker["name"], marker["contact"], marker["image"], marker["rating"], marker["coordinates"]]
                break

        field1 = ft.TextField(
            label="Location",
            value = values[0]
        )
        field2 = ft.TextField(
            label="Contact",
            value = values[1]
        )
        field3 = ft.TextField(
            label = "Image URL",
            value = values[2],
        )
        field4 = ft.TextField(
            label="Rating",
            value = values[3],
        )
        field5 = ft.TextField(
            label="X coordinate",
            value = values[4][0]
        )
        field6 = ft.TextField(
            label="Y coordinate",
            value = values[4][1]
        )

        def submit_handler(e):
            global dlg
            updated_values = [field1.value, field2.value, field3.value, field4.value, tuple((float(field5.value), float(field6.value)))]
            submit_change(e, updated_values, dest)
            close_dialog(None)

        action = [dropdown, ft.Container(height=10), field1, ft.Container(height=10), field2, ft.Container(), ft.Container(height=10), field3, ft.Container(height=10), field4, ft.Container(height=10),
                   field5, ft.Container(height=10), field6, ft.Container(height=10),
                   ft.ElevatedButton("Submit", bgcolor = ft.Colors.BLUE_50, on_click = submit_handler)]
        
        dlg = ft.AlertDialog(
            title=ft.Text(dest),
            content = ft.Column([ft.ElevatedButton("Change Coordinates on Map", on_click = lambda e: change_coordinates(e, dest))], tight = True, alignment = ft.alignment.bottom_left),
            actions = action,
        )

        page.open(dlg)

    def handle_edit(e):
        global dlg
        global dropdown

        dropdown = ft.Dropdown(
            label="Destination",
            hint_text="Select a Destination..",
            options=[ft.dropdown.Option(item['name']) for item in marker_info.values()],
            autofocus=True,
            bgcolor=ft.Colors.WHITE,
            on_change=return_value
        )

        field1 = ft.TextField(label="Location")
        field2 = ft.TextField(label="Contact")
        field3 = ft.TextField(label="Image URL")
        field4 = ft.TextField(label="Rating")
        field5 = ft.TextField(label="X Coordinate")
        field6 = ft.TextField(label="Y Coordinate")

        action = [dropdown, ft.Container(height=10), field1, ft.Container(height=10), field2, ft.Container(), ft.Container(height=10), field3, ft.Container(height=10), field4, ft.Container(height=10),
                   field5, ft.Container(height=10), field6, ft.Container(height=10)]

        dlg = ft.AlertDialog(
            title=ft.Text("Select a Destination"),
            actions = action,
        )
        page.open(dlg)
    
    login_button = ft.GestureDetector(content=ft.Image(src="google_login_light.png", width=160, height=40, fit = ft.ImageFit.CONTAIN), on_tap=logingoogle, mouse_cursor=ft.MouseCursor.CLICK)
    logout_button = ft.ElevatedButton("Logout", bgcolor = ft.Colors.BLUE_50, color = ft.Colors.PURPLE_300, on_click = logoutgoogle)
    edit_markers_button = ft.ElevatedButton("Edit Markers", bgcolor = ft.Colors.BLUE_50, color = ft.Colors.PURPLE_300, on_click = handle_edit)
    edit_markers_button.visible = False

    toggle_login_buttons()

    page.on_login = on_login
    page.on_logout = on_logout

    nav_icon = ft.Container(content = ft.IconButton(ft.Icons.MENU, on_click=lambda e: page.open(drawer), icon_size = 40, icon_color = ft.Colors.BLUE_200), alignment = ft.alignment.top_left)

    def change_mode(e):
        if e.control.value == 'Dark Mode':
            page.bgcolor = ft.Colors.BLACK
            page.theme_mode = "dark"

            anchor_searchbar.view_bgcolor = ft.Colors.BLACK
            anchor_searchbar.bar_overlay_color = ft.Colors.BLACK
            anchor_searchbar.bar_bgcolor = ft.Colors.BLACK
            anchor_searchbar.update()

            nav_icon.content.icon_color = ft.Colors.WHITE
            drawer.indicator_color = ft.Colors.WHITE,
            drawer.bgcolor = ft.Colors.BLACK

            login_button.content = ft.Image(src="google_login_dark.png", width=160, height=40, fit = ft.ImageFit.CONTAIN)
            login_button.update()

            page.update()

        elif e.control.value == "Light Mode":
            page.bgcolor = ft.Colors.WHITE
            page.theme_mode = "light"

            anchor_searchbar.view_bgcolor = ft.Colors.WHITE
            anchor_searchbar.bar_overlay_color = ft.Colors.BLUE_100
            anchor_searchbar.bar_bgcolor = ft.Colors.BLUE_50
            anchor_searchbar.update()

            nav_icon.content.icon_color = ft.Colors.BLUE_200
            drawer.indicator_color = ft.Colors.BLUE_50,
            drawer.bgcolor = ft.Colors.WHITE

            login_button.content = ft.Image(src="google_login_light.png", width=160, height=40, fit = ft.ImageFit.CONTAIN)
            login_button.update()

            page.update()

    def return_main(e):
        drawer.selected_index = 0
        drawer.update()

    def handle_navigation_change(e):
        if int(e.data) == 0:
            page.close(drawer)

        elif int(e.data) == 1:
            content = ft.Column(
                [
                    ft.Text("SETTINGS"),
                    ft.RadioGroup(content=ft.Column([
                        ft.Radio(value="Light Mode", label="Light Mode"),
                        ft.Radio(value="Dark Mode", label="Dark Mode")
                    ], tight = True
                ), on_change = change_mode
            )], tight = True)

            dlg = ft.AlertDialog(content=content, adaptive = True, shape = ft.RoundedRectangleBorder(radius = 2))

            page.open(dlg)
            page.update()

        elif int(e.data) == 2:
            if page.auth is None:
                dlg = ft.AlertDialog(content=ft.Container(ft.Text("Please Login First!")), adaptive = True, shape = ft.RoundedRectangleBorder(radius = 2))
                page.open(dlg)
                page.update()
            
            else:
                content = ft.Column([ft.Image(src = credentials['Picture'], height = 200, width = 200),
                                    ft.Text("Name: " + credentials["Name"], size = 15),
                                    ft.Text("Surname: " + credentials['Family_Name'], size = 15),
                                    ft.Text("Email: " + credentials['Email'], size = 15)], tight = True)
                dlg = ft.AlertDialog(title = ft.Text("Profile"), content = content)
                page.open(dlg)
                page.update()

    drawer = ft.NavigationDrawer(
        on_change = handle_navigation_change,
        on_dismiss = return_main,
        controls=[
            ft.Container(height=25),
            ft.NavigationDrawerDestination(
                label= "Home",
                icon=ft.Icons.HOME,
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Settings",
                icon=ft.Icon(ft.Icons.SETTINGS),
            ),
            ft.NavigationDrawerDestination(
                label="Profile",
                icon=ft.Icon(ft.Icons.PERSON),
            ),
        ],
        indicator_color = ft.Colors.BLUE_200,
        bgcolor = ft.Colors.WHITE,
    )

    def close_dialog(e):
        global dlg
        page.close(dlg)
        print("Dialog Closed")
        page.update()

    def generate_dialog(latitude, longitude, title, image, contact, coordinates, rating):
        global dlg
        content = ft.Column([   
            ft.Image(src=image, width=800, height=450),
            ft.Text(f"Contact: {contact}"),
            ft.Text(f"Rating: {rating}"),
            ft.Text(f"Coordinates: {coordinates}")
        ], spacing = 10, tight = True)

        dlg = ft.AlertDialog(
            title=ft.Text(f"Details for {title}"),
            content=content,
            actions = [ft.TextButton("Close", on_click = close_dialog)]
        )

        page.open(dlg)
        page.update()

    def handle_marker_tap(e, values):
        generate_dialog(*values)

    def handle_map_tap(e: map.MapTapEvent):
        global selected_marker, dlg

        try:
            if selected_marker:
                latitude = e.coordinates.latitude
                longitude = e.coordinates.longitude

                for _, marker in marker_info.items():
                    if marker["name"] == selected_marker:
                        marker["coordinates"] = (latitude, longitude)
                        break

            with open("marker_info.json", "w") as f:
                json.dump(marker_info, f, indent=4)


            dlg = ft.AlertDialog(
                content = ft.Column([ft.Text(f"Coordinates for {selected_marker} updated to: ({latitude}, {longitude})")], tight = True),
                actions=[ft.TextButton("OK", on_click = close_dialog)])

            page.open(dlg)
            page.update()

            selected_marker = None

            marker_layer_ref.current.markers = [map.Marker(
                            content=ft.IconButton(ft.Icons.LOCATION_ON, icon_color = ft.Colors.RED, icon_size = 45, on_click=lambda e, values=[marker["coordinates"][0], marker["coordinates"][1], marker["name"], marker["image"], marker["contact"], marker["coordinates"], marker["rating"]]: handle_marker_tap(e, values)),
                            coordinates=map.MapLatitudeLongitude(marker["coordinates"][0], marker["coordinates"][1])) for marker in marker_info.values()]

            page.update()

        except:
            pass

    def handle_search_submit(e):

        for dct in list(marker_info.values()):
            if dct['name'] == e.data:
                image = dct['image']
                contact = dct['contact']
                coordinates = dct['coordinates']
                rating = dct['rating']
                break

            try:
                if dct['name'] == e.control.title.value:
                    image = dct['image']
                    contact = dct['contact']
                    coordinates = dct['coordinates']
                    rating = dct['rating']
                    break
            
            except:
                pass

        if coordinates:
            generate_dialog(coordinates[0], coordinates[1], e.data, image, contact, coordinates, rating)

    def handle_search_tap(e):
        anchor_searchbar.open_view()

    def close_anchor(e):
        text = e.control.title.value
        anchor_searchbar.close_view(text)
        handle_search_submit(e)

    anchor_searchbar = ft.SearchBar(
            view_elevation = 4,
            divider_color = ft.Colors.BLUE,
            bar_hint_text = "Search Destinations",
            view_hint_text = "Choose from Destinations (Press Enter to Submit)",
            on_submit = handle_search_submit,
            on_tap = handle_search_tap,
            controls = [
              ft.ListTile(title = ft.Text(list(marker_info.values())[i]['name']), on_click = close_anchor, data = i) for i in range(len(marker_info))
            ],
            view_bgcolor = ft.Colors.WHITE,
            bar_overlay_color = ft.Colors.BLUE_100,
            view_surface_tint_color = ft.Colors.WHITE,
            bar_bgcolor = ft.Colors.BLUE_50,

    )

    page.add(

        ft.Row(controls = [nav_icon,
                           ft.Container(content = anchor_searchbar, alignment = ft.alignment.top_center, expand = True),
                           edit_markers_button, login_button, logout_button]),
        
        m:=map.Map(
            ref = map_ref,
            expand=True,
            initial_center=map.MapLatitudeLongitude(current_lat, current_lon),
            initial_zoom=14,
            interaction_configuration=map.MapInteractionConfiguration(flags=map.MapInteractiveFlag.ALL),
            on_tap=handle_map_tap,
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                map.MarkerLayer(
                    ref=marker_layer_ref,
                    markers=[
                        map.Marker(
                            content=ft.IconButton(ft.Icons.LOCATION_ON, icon_color = ft.Colors.RED, icon_size = 30, on_click=lambda e, values=[marker["coordinates"][0], marker["coordinates"][1], marker["name"], marker["image"], marker["contact"], marker["coordinates"], marker["rating"]]: handle_marker_tap(e, values)),
                            coordinates=map.MapLatitudeLongitude(marker["coordinates"][0], marker["coordinates"][1]),
                            alignment=ft.alignment.bottom_center
                        ) for marker in marker_info.values()
                    ],
                ),
            ],
        ),
        ft.Row(controls = [
            ft.OutlinedButton("Rotate 90", on_click=lambda e: m.rotate_from(90)),
            ft.OutlinedButton("Rotate -90", on_click=lambda e: m.rotate_from(-90)),
            ft.OutlinedButton("Zoom in", on_click=lambda e: m.zoom_in(animation_duration=ft.Duration(seconds=2))),
            ft.OutlinedButton("Zoom out", on_click=lambda e: m.zoom_out(animation_duration=ft.Duration(seconds=2)))
        ])
    )

    
ft.app(main, assets_dir = "assets", port=8000)