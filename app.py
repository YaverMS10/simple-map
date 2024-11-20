import flet as ft
import flet.map as map
from flet.auth.providers import GoogleOAuthProvider
from dotenv import load_dotenv
import os

load_dotenv()
clientID = os.getenv('CLIENT_ID')
clientSecret = os.getenv('CLIENT_SECRET')

def main(page: ft.Page):

    page.bgcolor = ft.colors.WHITE
    page.theme_mode = "light"

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    provider = GoogleOAuthProvider(
        client_id = clientID,
        client_secret = clientSecret,
        redirect_url = "http://localhost:50334/oauth_callback"
    )

    def logingoogle(e):
        page.login(provider)

    def on_login(e):
        global credentials
        credentials = {"Name": page.auth.user['given_name'], "Family_Name": page.auth.user['family_name'], "Picture": page.auth.user['picture'], "Email": page.auth.user['email']}
        toggle_login_buttons()

    def logoutgoogle(e):
        page.logout()

    def on_logout(e):
        toggle_login_buttons()

    def toggle_login_buttons():
        login_button.visible = page.auth is None
        logout_button.visible = page.auth is not None
        page.update()
    
    login_button = ft.ElevatedButton("Login with Google", bgcolor = ft.colors.BLUE_50, on_click = logingoogle)
    logout_button = ft.ElevatedButton("Logout", bgcolor = ft.colors.BLUE_50, on_click = logoutgoogle)

    toggle_login_buttons()

    page.on_login = on_login
    page.on_logout = on_logout

    def change_mode(e):
        if e.control.value == 'Dark Mode':
            page.bgcolor = ft.colors.BLACK
            page.theme_mode = "dark"
            page.update()
        else:
            page.bgcolor = ft.colors.WHITE
            page.theme_mode = "light"
            page.update()

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
                    ],
                ), on_change = change_mode
            )], height = 100)

            dlg = ft.AlertDialog(content=content, adaptive = True, shape = ft.RoundedRectangleBorder(radius = 2))

            dlg.open = True
            page.add(dlg)
            page.update()

        elif int(e.data) == 2:
            if page.auth is None:
                dlg = ft.AlertDialog(content=ft.Container(ft.Text("Please Login First!")), adaptive = True, shape = ft.RoundedRectangleBorder(radius = 2))
                dlg.open = True
                page.add(dlg)
                page.update()
            
            else:
                content = ft.Column([ft.Image(src = credentials['Picture'], height = 400, width = 400),
                                    ft.Container(ft.Text("Name: " + credentials["Name"], size = 15)),
                                    ft.Container(ft.Text("Surname: " + credentials['Family_Name'], size = 15)),
                                    ft.Container(ft.Text("Email: " + credentials['Email'], size = 15))], height = 500)
                dlg = ft.AlertDialog(title = ft.Text("Profile"), content = content)
                dlg.open = True
                page.add(dlg)
                page.update()

    drawer = ft.NavigationDrawer(
        on_change = handle_navigation_change,
        controls=[
            ft.Container(height=25),
            ft.NavigationDrawerDestination(
                label= "Home",
                icon=ft.icons.HOME,
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                label="Settings",
                icon_content=ft.Icon(ft.icons.SETTINGS),
            ),
            ft.NavigationDrawerDestination(
                label="Profile",
                icon_content=ft.Icon(ft.icons.PERSON),
            ),
        ],
        indicator_color = ft.colors.BLUE_200,
        bgcolor = ft.colors.WHITE,
    )

    marker_layer_ref = ft.Ref[map.MarkerLayer]()

    marker_info = {
        (40.38, 49.86): {
            "name": "Destination 1",
            "contact": "John Doe, +123456789",
            "image": "https://fastly.picsum.photos/id/395/1600/900.jpg?hmac=bJOgSJj9Wcer3NohLohpCmeu9DQ2TbTySNTQFN6Xgqo",  # Placeholder image
            "rating": "3.8/5",
            "coordinates": (40.38, 49.86),
        },
        (40.42, 49.85): {
            "name": "Destination 2",
            "contact": "Jane Doe, +987654321",
            "image": "https://fastly.picsum.photos/id/448/1600/900.jpg?hmac=_0zJFjqxt97haLD-sbu9uh-vHKoFVLVlK1uIReRXJnQ",  # Placeholder image
            "rating": "4.2/5",
            "coordinates": (40.42, 49.85),
        },
        (40.41, 49.88): {
            "name": "Destination 3",
            "contact": "Alice Smith, +1122334455",
            "image": "https://fastly.picsum.photos/id/925/1600/900.jpg?hmac=bmVlszRjAVCbzNGgLNa5uGHJvITkssCIlwLDweV6-m0",  # Placeholder image
            "rating": "4.8/5",
            "coordinates": (40.41, 49.88),
        },
    }


    def generate_dialog(latitude, longitude, title, image, contact, coordinates, rating):
        content = ft.Column([
            ft.Container(ft.Image(src=image, width=800, height=450)),
            ft.Container(ft.Text(f"Contact: {contact}"), alignment = ft.alignment.center_left),
            ft.Container(ft.Text(f"Rating: {rating}"), alignment = ft.alignment.center_left),
            ft.Container(ft.Text(f"Coordinates: {coordinates}"), alignment = ft.alignment.center_left)
        ], height = 500)

        dlg = ft.AlertDialog(
            title=ft.Text(f"Details for {title}"),
            content=content,
        )

        
        dlg.open = True
        page.add(dlg)
        page.update()

    def handle_map_tap(e: map.MapTapEvent):
        for coord, info in marker_info.items():
            if abs(e.coordinates.latitude - coord[0]) < 0.01 and abs(e.coordinates.longitude - coord[1]) < 0.01:
                ref_latitude = coord[0]
                ref_longitude = coord[1]
                
                info = marker_info.get((ref_latitude, ref_longitude), None)
                if info:
                    generate_dialog(ref_latitude, ref_longitude, info["name"], info["image"], info["contact"], info["coordinates"], info["rating"])

                break

    def handle_search_submit(e):

        for dct in list(marker_info.values()):
            if dct['name'] == e.data:
                image = dct['image']
                contact = dct['contact']
                coordinates = dct['coordinates']
                rating = dct['rating']
                break

        if coordinates:
            generate_dialog(coordinates[0], coordinates[1], e.data, image, contact, coordinates, rating)

    def handle_search_tap(e):
        anchor_searchbar.open_view()

    def close_anchor(e):
        text = e.control.title.value
        anchor_searchbar.close_view(text)

    anchor_searchbar = ft.SearchBar(
            view_elevation = 4,
            divider_color = ft.colors.BLUE,
            bar_hint_text = "Search Destinations",
            view_hint_text = "Choose from Destinations (Press Enter to Submit)",
            on_submit = handle_search_submit,
            on_tap = handle_search_tap,
            controls = [
              ft.ListTile(title = ft.Text(list(marker_info.values())[i]['name']), on_click = close_anchor, data = i) for i in range(len(marker_info))
            ],
            view_bgcolor = ft.colors.WHITE,
            bar_overlay_color = ft.colors.BLUE_100,
            view_surface_tint_color = ft.colors.WHITE,
            bar_bgcolor = ft.colors.BLUE_50,

    )

    page.add(

        ft.Row(controls = [ft.Container(content = ft.IconButton(ft.icons.MENU, on_click=lambda e: page.open(drawer), icon_size = 40, icon_color = ft.colors.BLUE_200), alignment = ft.alignment.top_left),
                           ft.Container(content = anchor_searchbar, alignment = ft.alignment.top_center, expand = True),
                           login_button, logout_button]),
        
        map.Map(
            expand=True,
            configuration=map.MapConfiguration(
                initial_center=map.MapLatitudeLongitude(40.41, 49.87),
                initial_zoom=11,
                interaction_configuration=map.MapInteractionConfiguration(
                    flags=map.MapInteractiveFlag.ALL
                ),
                on_init=lambda e: print(f"Initialized Map"),
                on_tap = handle_map_tap,
            ),
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                map.MarkerLayer(
                    ref=marker_layer_ref,
                    markers=[
                        map.Marker(
                            content=ft.Icon(ft.icons.LOCATION_ON, color = ft.cupertino_colors.DESTRUCTIVE_RED, size = 40),
                            coordinates=map.MapLatitudeLongitude(40.38, 49.86),
                        ),
                        map.Marker(
                            content=ft.Icon(ft.icons.LOCATION_ON, color = ft.cupertino_colors.DESTRUCTIVE_RED, size = 40),
                            coordinates=map.MapLatitudeLongitude(40.42, 49.85),
                        ),
                        map.Marker(
                            content=ft.Icon(ft.icons.LOCATION_ON, color = ft.cupertino_colors.DESTRUCTIVE_RED, size = 40),
                            coordinates=map.MapLatitudeLongitude(40.41, 49.88),
                        ),
                    ],
                ),
            ],
        )
    )

    
ft.app(main)