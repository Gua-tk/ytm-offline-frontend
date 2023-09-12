#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    AlertDialog,
    MainAxisAlignment,
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
from time import sleep


def make_post_request(url, data):
    """
    Make a POST request to the specified URL with JSON data.

    Args:
        url (str): The URL to send the POST request to.
        data (dict): The JSON data to include in the request body.

    Returns:
        dict or None: The JSON response if the request is successful, None otherwise.
    """
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

        # Configure the theme of the page
        self.page.theme = theme.Theme(color_scheme_seed="green")

        # Define event handlers
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        # Initialize properties
        self.route_change()

        self.host_address = host_address
        self.host_port = host_port

        self.prog_bars: Dict[str, ProgressRing] = {}
        self.files = Ref[Column]()
        self.total_files_to_upload = 0
        self.successfully_uploaded_files = 0
        self.upload_button = Ref[ElevatedButton]()

        self.dialog = Ref[AlertDialog]()

        # Initialize the file picker
        self.file_picker = FilePicker(on_result=self.file_picker_result,
                                      on_upload=self.on_upload_progress)
        self.page.overlay.append(self.file_picker)

    def create_menu(self):
        """
        Create the main menu bar (AppBar).

        Returns:
            AppBar: The main menu bar.
        """
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
                        PopupMenuItem(),  # Divider
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
                        PopupMenuItem(),  # Divider
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
        """
        Create the main content of the page.

        Returns:
            Text: A Text component representing the main content.
        """
        return Text("Body!")

    def create_main_view(self):
        """
        Create the main view that includes the menu bar and page body.

        Returns:
            View: The main view.
        """
        return View(
            "/",
            [
                self.create_menu(),
                self.create_page_body()
            ],
        )

    def create_button(self, text, func, icon="", ref="", disabled=False):
        """
            Create a button with optional parameters.

            Args:
                text (str): The text to display on the button.
                func (callable): The function to execute when the button is clicked.
                icon (str, optional): The icon to display on the button.
                ref (Ref, optional): A reference to associate with the button.
                disabled (bool, optional): Whether the button should be initially disabled.

            Returns:
                ElevatedButton: The created button.
            """
        return ElevatedButton(
            text,
            on_click=func,
            icon=icon,
            ref=ref,
            disabled=disabled
        )

    def create_custom_view(self, result, view_path, view_name, view_function):
        """
        Create a custom view for a specific route.

        Args:
            result (Component): The result component for the custom view.
            view_path (str): The route path for the custom view.
            view_name (str): The name of the custom view.
            view_function (callable): The function to execute when the "Submit" button is clicked.

        Returns:
            View: The custom view.
        """
        return View(
            view_path,
            [
                AppBar(
                    title=Text(view_name),
                    bgcolor=colors.SURFACE_VARIANT
                ),
                Text("This is the " + view_name + " Page"),
                result,
                self.create_button("Submit", lambda _: view_function)
            ],
        )

    def file_picker_result(self, e: FilePickerResultEvent):
        """
        Handle file picker results.

        Args:
            e (FilePickerResultEvent): The event object containing file picker results.
        """
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
        """
        Handle file upload progress.

        Args:
            e (FilePickerUploadEvent): The event object containing file upload progress information.
        """
        self.prog_bars[e.file_name].value = e.progress
        self.prog_bars[e.file_name].update()

        if e.progress == 1:  # Check if the upload progress is 100%
            self.increment_uploaded_files_count()  # Call the function to increment the count

    def show_success_dialog(self):
        if self.total_files_to_upload == 1 and self.successfully_uploaded_files == self.total_files_to_upload:
            self.show_alert_dialog("File Uploaded", "File has been uploaded!", False)
        elif self.total_files_to_upload > 1 and self.successfully_uploaded_files == self.total_files_to_upload:
            self.show_alert_dialog("Files Uploaded",
                                   f"All {self.total_files_to_upload} files have been uploaded!",
                                   False)

    def increment_uploaded_files_count(self):
        self.successfully_uploaded_files += 1
        self.show_success_dialog()


    def upload_files(self, e):
        """
        Upload selected files when the "Upload" button is clicked.

        Args:
            e: The event object (not used).
        """
        self.total_files_to_upload = 0
        self.successfully_uploaded_files = 0
        upload_list = []

        if self.file_picker.result is not None and self.file_picker.result.files is not None:
            self.total_files_to_upload = len(self.file_picker.result.files)  # Update the total count of files
            for f in self.file_picker.result.files:
                upload_list.append(
                    FilePickerUploadFile(
                        f.name,
                        upload_url=self.page.get_upload_url(f.name, 600),
                    )
                )
            self.file_picker.upload(upload_list)

    def create_custom_upload_file_view(self, view_path, view_name):
        """
        Create a view for uploading files.

        Args:
            view_path (str): The route path for the upload view.
            view_name (str): The name of the upload view.

        Returns:
            View: The upload file view.
        """
        return View(
            view_path,
            [
                AppBar(
                    title=Text(view_name),
                    bgcolor=colors.SURFACE_VARIANT
                ),
                Text("This is the " + view_name + " Page"),
                self.create_button(
                    "Select files...",
                    lambda _: self.file_picker.pick_files(allow_multiple=True),
                    icon=icons.FOLDER_OPEN
                ),
                Column(ref=self.files),
                self.create_button("Upload", self.upload_files, icons.UPLOAD, self.upload_button, True)
            ],
        )

    def open_dlg(self, dlg):
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dlg(self, dlg):
        dlg.open = False
        self.page.update()

    def create_simple_alert_dialog(self, title, content_text, dismiss_func, alignment=MainAxisAlignment.END):
        return AlertDialog(
            title=Text(title),
            content=Text(content_text),
            on_dismiss=dismiss_func,
            actions_alignment=alignment
        )

    def show_alert_dialog(self, title_text, content_text, is_auto_closed=True, delay=2):
        # Create an alert dialog with the given title and content
        alert_dialog = self.create_simple_alert_dialog(title_text, content_text, lambda e: print("Dialog closed!"))

        # Show the dialog
        self.open_dlg(alert_dialog)

        # Close the dialog and print the message when all files are uploaded
        if is_auto_closed:
            sleep(delay)
            self.close_dlg(alert_dialog)

    def route_change(self, e=None):
        """
        Handle route changes and update views accordingly.

        Args:
            e: The event object (not used).
        """
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
        """
        Handle view popping (removing the top view).

        Args:
            e: The event object (not used).
        """
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def submit_audio(self, txt_url, e=None):
        """
        Handle audio submission when the "Submit" button is clicked.

        Args:
            txt_url (str): The entered audio URL.
            e: The event object (not used).
        """
        print(txt_url)
        self.make_audio_upload_request(txt_url)
        print("DONE")

    def submit_playlist(self, txt_url, e=None):
        """
        Handle playlist submission when the "Submit" button is clicked.

        Args:
            txt_url (str): The entered playlist URL.
            e: The event object (not used).
        """
        self.make_playlist_upload_request(txt_url)
        print("DONE")

    def make_audio_upload_request(self, link):
        """
        Make a POST request to upload an audio file.

        Args:
            link (str): The audio URL to upload.
        """
        request_data = {"audio_url": link}
        response = make_post_request('http://' + self.host_address + ':' + self.host_port + '/audio/upload', request_data)
        print("RESPONSE:\t", response)

    def make_playlist_upload_request(self, link):
        """
        Make a POST request to upload a playlist.

        Args:
            link (str): The playlist URL to upload (not implemented).
        """
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
