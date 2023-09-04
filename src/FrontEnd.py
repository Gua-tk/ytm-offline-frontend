import os
import flet as ft
from flet import AppBar, ElevatedButton, Page, Text, View, colors, TextField, FilePicker, Icon, PopupMenuButton, PopupMenuItem
import requests

from flet_core import theme


def make_post_request(url, data):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors (non-2xx status codes)
        return response.json()  # Return response data in JSON format
    except requests.exceptions.RequestException as e:
        print("POST request failed:", e)
        return None


class FrontEnd:
    def __init__(self, page: Page, host_address, host_port):
        self.page = page
        self.page.title = "ytm-offline"

        # self.page.splash = None
        self.page.theme = theme.Theme(color_scheme_seed="green")

        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        self.route_change()

        self.host_address = host_address
        self.host_port = host_port

        self.file_picker = FilePicker(on_result=self.on_dialog_result)
        self.page.overlay.append(self.file_picker)

    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        # print("Selected files:", e.files)
        # print("Selected file or directory:", e.path)
        print("A file has been selected.")

    def create_menu(self):
        return AppBar(
                        leading=Icon(ft.icons.AIR),
                        leading_width=40,
                        title=Text("ytm-offline"),
                        center_title=False,
                        bgcolor=colors.SURFACE_VARIANT,
                        actions=[
                            # IconButton(ft.icons.WB_SUNNY_OUTLINED),
                            # IconButton(ft.icons.FILTER_3),
                            PopupMenuButton(
                                items=[
                                    PopupMenuItem(
                                        text="Audio URL", on_click=lambda _: self.page.go("/audio")
                                    ),
                                    PopupMenuItem(),  # divider
                                    PopupMenuItem(
                                        text="Playlist URL", on_click=lambda _: self.page.go("/playlist")
                                    ),
                                    PopupMenuItem(),  # divider
                                    PopupMenuItem(
                                        text="Audio Upload", on_click=lambda _: self.page.go("/audio/upload")
                                    ),
                                    PopupMenuItem(),  # divider
                                    PopupMenuItem(
                                        text="Playlist Upload", on_click=lambda _: self.page.go("/playlist/upload")
                                    ),
                                    PopupMenuItem(),  # divider
                                    PopupMenuItem(
                                        text="Audio Upload 2", on_click=lambda _: self.page.go("/audio/upload2")
                                    ),
                                    PopupMenuItem(),  # divider
                                    PopupMenuItem(
                                        text="Playlist Upload 2", on_click=lambda _: self.page.go("/playlist/upload2")
                                    ),
                                ],
                            )
                        ]
                    )

    def create_page_body(self):
        return Text("Body!")

    def create_main_view(self):
        return View(
                "/",
                [
                    self.create_menu(),
                    self.create_page_body()
                ],
            )

    def create_custom_view(self, result, view_path, view_name, view_function):
        return View(
                    view_path,
                    [
                        AppBar(title=Text(view_name), bgcolor=colors.SURFACE_VARIANT),
                        Text("This is the " + view_name + " Page"),
                        result,
                        ElevatedButton("Submit", on_click=lambda _: view_function),
                    ],
                )

    def create_custom_upload_file_view(self, result, view_path, view_name):
        return View(
                    view_path,
                    [
                        AppBar(title=Text(view_name), bgcolor=colors.SURFACE_VARIANT),
                        Text("This is the " + view_name + " Page"),
                        ElevatedButton("Choose files...", on_click=lambda _: self.file_picker.pick_files(allow_multiple=True)),
                        ElevatedButton("Upload", on_click=lambda _: self.test_function(
                            "NAME: " + str(self.file_picker.result.files[0].path),
                            "PATH: " + str(self.file_picker.result.files[0].name),
                            "SIZE: " + str(self.file_picker.result.files[0].size)
                        )
                                       )
                    ],
                )

    def test_function(self, text, text2, text3):
        print(text)
        print("_" * 50)
        print(text2)
        print("_" * 50)
        print(text3)
        print("START UPLOAD!")

    def route_change(self, e=None):
        self.page.views.clear()
        self.page.views.append(self.create_main_view())

        if self.page.route == "/audio":
            txt_url = TextField(label="Enter song URL")
            self.page.views.append(
                self.create_custom_view(txt_url, "/audio", "Audio URL", self.submit_audio(txt_url.value))
            )

        if self.page.route == "/playlist":
            txt_url = TextField(label="Enter playlist URL")
            self.page.views.append(
                self.create_custom_view(txt_url, "/playlist", "Playlist URL", self.submit_playlist(txt_url.value))
            )

        if self.page.route == "/audio/upload":
            result = self.file_picker.result
            self.page.views.append(
                self.create_custom_upload_file_view(result, "/audio/upload", "Upload .mp3 audio")
            )

        if self.page.route == "/playlist/upload":
            result = self.file_picker.result
            self.page.views.append(
                self.create_custom_upload_file_view(result, "/playlist/upload", "Upload .zip playlist")
            )

        if self.page.route == "/audio/upload2":
            result = self.file_picker.result
            self.page.views.append(
                View(
                    "/audio/upload2",
                    [
                        AppBar(title=Text("Upload .mp3 audio"), bgcolor=colors.SURFACE_VARIANT),
                        Text("This is the Upload Audio Page"),
                        ElevatedButton("Choose files...", on_click=lambda _: self.file_picker.pick_files(allow_multiple=True)),
                        #ElevatedButton("Submit", on_click=lambda _: self.make_audio_upload_request()),
                    ],
                )
            )

        if self.page.route == "/playlist/upload2":
            result = self.file_picker.result
            self.page.views.append(
                View(
                    "/playlist/upload2",
                    [
                        AppBar(title=Text("Upload .zip playlist"), bgcolor=colors.SURFACE_VARIANT),
                        Text("This is the Upload Playlist Page"),
                        ElevatedButton("Choose files...", on_click=lambda _: self.file_picker.pick_files(allow_multiple=True)),
                        #ElevatedButton("Submit", on_click=lambda _: self.make_playlist_upload_request()),
                    ],
                )
            )
        self.page.update()

    def view_pop(self, e=None):
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def submit_audio(self, txt_url, e=None):
        print(txt_url)
        self.make_audio_upload_request(txt_url)
        print("DONE")

    def submit_playlist(self, txt_url, e=None):
        self.make_playlist_upload_request(txt_url)
        print("DONE")

    def make_audio_upload_request(self, link):
        request_data = {"audio_url": link}
        # data = json.dumps(request_data)
        response = make_post_request('http://' + self.host_address + ':' + self.host_port + '/audio/upload', request_data)
        print("RESPEONSE:\t", response)

    def make_playlist_upload_request(self, link):
        pass


def main(page: Page):
    host_address = os.environ.get("BACKEND_HOST")
    host_port = os.environ.get("BACKEND_PORT")

    if host_address is None:
        host_address = "127.0.0.1"

    if host_port is None:
        host_port = "5000"

    frontend = FrontEnd(page, host_address, host_port)
    page.go(page.route)


if __name__ == '__main__':
    ft.app(main, view=ft.AppView.WEB_BROWSER, assets_dir="assets", port=5010, host="0.0.0.0")
