import flet as ft
from flet import AppBar, ElevatedButton, Page, Text, View, colors, TextField
import requests

class FrontEnd:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "ytm-offline"
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        self.route_change()

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

    def submit_playlist(self, txt_url, e=None):
        print(txt_url)


def main(page: Page):
    frontend = FrontEnd(page)
    page.go(page.route)

if __name__ == '__main__':
    ft.app(main, view=ft.AppView.WEB_BROWSER)
