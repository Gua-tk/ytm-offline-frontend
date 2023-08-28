import os
import flet as ft
from flet import AppBar, ElevatedButton, Page, Text, View, colors, TextField
import requests


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
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        self.route_change()

        self.host_address = host_address
        self.host_port = host_port

    def route_change(self, e=None):
        self.page.views.clear()
        self.page.views.append(
            View(
                "/",
                [
                    AppBar(title=Text("ytm-offline"), bgcolor=colors.SURFACE_VARIANT),
                    ElevatedButton("Audio", on_click=lambda _: self.page.go("/audio")),
                    ElevatedButton("Playlist", on_click=lambda _: self.page.go("/playlist")),
                ],
            )
        )
        if self.page.route == "/audio":
            txt_url = TextField(label="Enter song URL")
            self.page.views.append(
                View(
                    "/audio",
                    [
                        AppBar(title=Text("Audio"), bgcolor=colors.SURFACE_VARIANT),
                        ElevatedButton("Go Home", on_click=lambda _: self.page.go("/")),
                        Text("This is the Audio Page"),
                        txt_url,
                        ElevatedButton("Submit", on_click=lambda _: self.submit_audio(txt_url.value)),
                    ],
                )
            )

        if self.page.route == "/playlist":
            txt_url = TextField(label="Enter playlist URL")
            self.page.views.append(
                View(
                    "/playlist",
                    [
                        AppBar(title=Text("Playlist"), bgcolor=colors.SURFACE_VARIANT),
                        ElevatedButton("Go Home", on_click=lambda _: self.page.go("/")),
                        Text("This is the Playlist Page"),
                        txt_url,
                        ElevatedButton("Submit", on_click=lambda _: self.submit_playlist(txt_url.value)),
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
        print(txt_url)

    def make_audio_upload_request(self, link):
        request_data = {"audio_url": link}
        # data = json.dumps(request_data)
        response = make_post_request('http://' + self.host_address + ':' + self.host_port + '/audio/upload', request_data)
        print("RESPEONSE:\t", response)


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
    ft.app(main, view=ft.AppView.WEB_BROWSER, port=5010, host="0.0.0.0")
