import os
from flet import (
    AppBar,
    ElevatedButton,
    Page,
    Text,
    View,
    colors,
    TextField,
    FilePicker,
    Icon,
    PopupMenuButton,
    PopupMenuItem,
    FilePickerResultEvent,
    FilePickerUploadEvent,
    FilePickerUploadFile,
    ProgressRing,
    Ref,
    Column,
    Row,
    icons,
    app,
    AppView
)

import requests

from flet_core import theme

from typing import Dict


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

        self.prog_bars: Dict[str, ProgressRing] = {}
        self.files = Ref[Column]()
        self.upload_button = Ref[ElevatedButton]()

        self.file_picker = FilePicker(on_result=self.file_picker_result,
                                      on_upload=self.on_upload_progress)
        self.page.overlay.append(self.file_picker)

    def create_menu(self):
        return AppBar(
                        leading=Icon(icons.DOWNLOAD_FOR_OFFLINE),
                        leading_width=40,
                        title=Text("ytm-offline"),
                        center_title=False,
                        bgcolor=colors.SURFACE_VARIANT,
                        actions=[
                            PopupMenuButton(
                                items=[
                                    PopupMenuItem(
                                        text="Audio URL",
                                        on_click=lambda _: self.page.go("/audio")
                                    ),
                                    PopupMenuItem(),  # divider
                                    PopupMenuItem(
                                        text="Playlist URL",
                                        on_click=lambda _: self.page.go("/playlist")
                                    ),
                                    PopupMenuItem(),
                                    PopupMenuItem(
                                        text="Audio Upload",
                                        on_click=lambda _: self.page.go("/audio/upload")
                                    ),
                                    PopupMenuItem(),
                                    PopupMenuItem(
                                        text="Playlist Upload",
                                        on_click=lambda _: self.page.go("/playlist/upload")
                                    ),
                                    PopupMenuItem(),  # divider
                                    PopupMenuItem(
                                        text="Audio Upload 2",
                                        on_click=lambda _: self.page.go("/audio/upload2")
                                    ),
                                    PopupMenuItem(),
                                    PopupMenuItem(
                                        text="Playlist Upload 2",
                                        on_click=lambda _: self.page.go("/playlist/upload2")
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
                        AppBar(
                            title=Text(view_name),
                            bgcolor=colors.SURFACE_VARIANT
                        ),
                        Text("This is the " + view_name + " Page"),
                        result,
                        ElevatedButton(
                            "Submit",
                            on_click=lambda _: view_function)
                    ],
                )

    def file_picker_result(self, e: FilePickerResultEvent):
        self.upload_button.current.disabled = True if e.files is None else False
        self.prog_bars.clear()
        self.files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(
                    value=0,
                    bgcolor="#eeeeee",
                    width=20,
                    height=20
                )
                self.prog_bars[f.name] = prog
                self.files.current.controls.append(Row([prog, Text(f.name)]))
        self.page.update()

    def on_upload_progress(self, e: FilePickerUploadEvent):
        self.prog_bars[e.file_name].value = e.progress
        self.prog_bars[e.file_name].update()

    def upload_files(self, e):
        upload_list = []
        if self.file_picker.result is not None and self.file_picker.result.files is not None:
            for f in self.file_picker.result.files:
                upload_list.append(
                    FilePickerUploadFile(
                        f.name,
                        upload_url=self.page.get_upload_url(f.name, 600),
                    )
                )
            self.file_picker.upload(upload_list)

    def create_custom_upload_file_view(self, view_path, view_name):
        return View(
                    view_path,
                    [
                        AppBar(
                            title=Text(view_name),
                            bgcolor=colors.SURFACE_VARIANT
                        ),
                        Text("This is the " + view_name + " Page"),
                        ElevatedButton(
                            "Select files...",
                            icon=icons.FOLDER_OPEN,
                            on_click=lambda _: self.file_picker.pick_files(allow_multiple=True)
                        ),
                        Column(ref=self.files),
                        ElevatedButton(
                            "Upload",
                            ref=self.upload_button,
                            icon=icons.UPLOAD,
                            on_click=self.upload_files,
                            disabled=True
                        )
                    ],
                )

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
            self.page.views.append(
                self.create_custom_upload_file_view("/audio/upload", "Upload .mp3 audio")
            )

        if self.page.route == "/playlist/upload":
            self.page.views.append(
                self.create_custom_upload_file_view("/playlist/upload", "Upload .zip playlist")
            )

        if self.page.route == "/audio/upload2":
            self.page.views.append(
                self.create_custom_upload_file_view("/audio/upload2", "Upload .mp3 audio")
            )

        if self.page.route == "/playlist/upload2":
            self.page.views.append(
                self.create_custom_upload_file_view("/playlist/upload2", "Upload .zip playlist"))

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
    app(main, view=AppView.WEB_BROWSER, assets_dir="assets", port=5010, host="0.0.0.0", upload_dir="assets/uploads")
