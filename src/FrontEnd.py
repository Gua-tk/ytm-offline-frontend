#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from uuid import UUID

import uuid as uuid
from flet import (
    AppBar,
    ElevatedButton,
    Page,
    Text,
    View,
    colors,
    TextField,
    TextButton,
    FilePicker,
    Icon,
    Switch,
    IconButton,
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
        return response  # Return response data in JSON format
    except requests.exceptions.RequestException as e:
        print("POST request failed:", e)
        return None


class FrontEnd:
    def __init__(self, page: Page, host_address, host_port, self_host_address, self_host_port):
        self.txt_url: TextField = None
        self.page = page
        self.page.title = "ytm-manager"

        # Configure the theme of the page
        # self.page.theme = theme.Theme(color_scheme_seed="green")
        self.page.theme_mode = "light"

        # Define route buttons
        # Audio URL PopupMenuItem
        self.audio_url_icon_button = self.create_icon_button(
            lambda _: self.page.go("/audio"),
            "Audio URL",
            icons.AUDIOTRACK,
            icons.AUDIOTRACK_OUTLINED,
            colors.GREY,
            colors.RED
        )

        # Playlist URL PopupMenuItem
        self.playlist_url_icon_button = self.create_icon_button(
            lambda _: self.page.go("/playlist"),
            "Playlist URL",
            icons.WEBHOOK,  # Replace with the appropriate icon for Playlist URL
            icons.WEBHOOK_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Audio Upload PopupMenuItem
        self.audio_upload_icon_button = self.create_icon_button(
            lambda _: self.page.go("/audio/upload"),
            "Audio Upload",
            icons.AUDIO_FILE,
            icons.AUDIO_FILE_OUTLINED,
            colors.GREY,
            colors.RED
        )

        # Playlist Upload PopupMenuItem
        self.playlist_upload_icon_button = self.create_icon_button(
            lambda _: self.page.go("/playlist/upload"),
            "Playlist Upload",
            icons.LIST,  # Replace with the appropriate icon for Playlist Upload
            icons.LIST_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Audio Upload 2 PopupMenuItem
        self.audio_upload_2_icon_button = self.create_icon_button(
            lambda _: self.page.go("/audio/download"),
            "Download Audio",
            icons.DOWNLOAD,  # Replace with the appropriate icon for Audio Upload 2
            icons.DOWNLOAD_DONE_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Playlist Upload 2 PopupMenuItem
        self.playlist_upload_2_icon_button = self.create_icon_button(
            lambda _: self.page.go("/playlist/download"),
            "Download Playlist",
            icons.DOWNLOADING,  # Replace with the appropriate icon for Playlist Upload 2
            icons.DOWNLOAD_FOR_OFFLINE,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Define event handlers
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        # Initialize properties
        self.route_change()

        self.host_address = host_address
        self.host_port = host_port

        self.self_host_address = self_host_address
        self.self_host_port = self_host_port

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

    def create_icon_button(self, func, tooltip, icon, selected_icon, color, selected_color, selected=False, icon_size=35):
        return IconButton(
            icon=icon,
            selected_icon=selected_icon,
            icon_color=color,
            selected_icon_color=selected_color,
            selected=selected,
            icon_size=icon_size,
            tooltip=tooltip,
            on_click=func,
        )

    def toggle_dark_mode(self, e):
        # Toggle between light and dark themes
        self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"
        self.page.update()

    def create_switch(self, label_text, func):
        return Switch(
            label=label_text,
            on_change=func
        )

    def create_menu(self):
        """
        Create the main menu bar (AppBar).

        Returns:
            AppBar: The main menu bar.
        """

        # dark_mode_switch = self.create_switch("Dark Mode", self.toggle_dark_mode)

        return AppBar(
            leading=Icon(icons.DOWNLOAD_FOR_OFFLINE),
            leading_width=40,
            title=Text("ytm-offline"),
            center_title=False,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                self.audio_url_icon_button,
                self.playlist_url_icon_button,
                self.audio_upload_icon_button,
                self.playlist_upload_icon_button,
                self.audio_upload_2_icon_button,
                self.playlist_upload_2_icon_button,
                PopupMenuButton(
                    items=[
                        PopupMenuItem(
                            text="Dark Mode",
                            icon=icons.DARK_MODE,
                            on_click=self.toggle_dark_mode
                        ),
                        PopupMenuButton(),
                        PopupMenuItem(
                            text="Sign In",
                            icon=icons.SUPERVISED_USER_CIRCLE,
                            on_click=self.toggle_dark_mode
                        ),
                        PopupMenuButton(),
                        PopupMenuItem(
                            text="Create Account",
                            icon=icons.ACCESSIBILITY_NEW,
                            on_click=self.toggle_dark_mode
                        )
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
        print("CREATING BUTTON")
        print("The func ref:\t", func)
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
                self.create_button("Submit", view_function)
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
            self.show_simple_alert_dialog("File Uploaded", "File has been uploaded!", False)
            # self.show_modal_alert_dialog("File Uploaded", "File has been uploaded!", lambda _: self.close_dlg(), lambda _: self.close_dlg())
        elif self.total_files_to_upload > 1 and self.successfully_uploaded_files == self.total_files_to_upload:
            self.show_simple_alert_dialog("Files Uploaded",
                                   f"All {self.total_files_to_upload} files have been uploaded!",
                                   False)

    def show_error_dialog(self, title_text, error_message):
        """
        Show an error dialog with a title and error message.

        Args:
            title_text (str): The title of the error dialog.
            error_message (str): The error message to display.
        """
        # Create an error alert dialog with the given title and error message
        error_dialog = self.create_simple_alert_dialog(title_text, error_message)

        # Show the error dialog
        self.open_dlg(error_dialog)

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

    def close_dlg(self):
        dlg = self.page.dialog
        dlg.open = False
        self.page.update()

    def create_simple_alert_dialog(self, title, content_text, dismiss_func=lambda e: print("Dialog dismissed!"), alignment=MainAxisAlignment.END):
        return AlertDialog(
            title=Text(title),
            content=Text(content_text),
            on_dismiss=dismiss_func,
            actions_alignment=alignment
        )

    def create_modal_alert_dialog(self, title, content_text, yes_func, no_func, dismiss_func=lambda e: print("Modal dialog dismissed!"), alignment=MainAxisAlignment.END):
        return AlertDialog(
            modal=True,
            title=Text(title),
            content=Text(content_text),
            actions=[
                TextButton("Yes", on_click=yes_func),
                TextButton("No", on_click=no_func),
            ],
            actions_alignment=alignment,
            on_dismiss=dismiss_func,
        )

    def show_simple_alert_dialog(self, title_text, content_text, is_auto_closed=True, delay=2):
        # Create an alert dialog with the given title and content
        alert_dialog = self.create_simple_alert_dialog(title_text, content_text)

        # Show the dialog
        self.open_dlg(alert_dialog)

        # Close the dialog and print the message when all files are uploaded
        if is_auto_closed:
            sleep(delay)
            self.close_dlg()

    def show_modal_alert_dialog(self, title_text, content_text, yes_func, no_func):
        # Create an alert dialog with the given title and content
        alert_dialog = self.create_modal_alert_dialog(title_text, content_text, yes_func, no_func)

        # Show the dialog
        self.open_dlg(alert_dialog)

    def route_change(self, e=None):
        """
        Handle route changes and update views accordingly.

        Args:
            e: The event object (not used).
        """
        self.page.views.clear()
        self.page.views.append(self.create_main_view())

        if self.page.route == "/audio":
            self.txt_url = TextField(label="Enter song URL")
            print("INITIALIZING TEXT URL WITH THE TEXT", self.txt_url.value)
            self.page.views.append(
                self.create_custom_view(self.txt_url, "/audio", "Audio URL", self.submit_audio)
            )
            print("View is created.")

        if self.page.route == "/playlist":
            self.txt_url = TextField(label="Enter playlist URL")
            self.page.views.append(
                self.create_custom_view(self.txt_url, "/playlist", "Playlist URL", self.submit_playlist)
            )

        if self.page.route == "/audio/upload":
            self.page.views.append(
                self.create_custom_upload_file_view("/audio/upload", "Upload .mp3 audio")
            )

        if self.page.route == "/playlist/upload":
            self.page.views.append(
                self.create_custom_upload_file_view("/playlist/upload", "Upload .zip playlist")
            )

        if self.page.route == "/audio/download":
            self.txt_url = TextField(label="Enter playlist URL")
            self.page.views.append(
                self.create_custom_view(self.txt_url, "/audio/download", "Download Audio", self.download_audio)
            )

        if self.page.route == "/playlist/download":
            self.txt_url = TextField(label="Enter playlist URL")
            self.page.views.append(
                self.create_custom_view(self.txt_url, "/playlist/download", "Download Playlist", self.download_audio)
            )

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
        self.make_audio_upload_request(self.txt_url.value)

    def submit_playlist(self, txt_url, e=None):
        """
        Handle playlist submission when the "Submit" button is clicked.

        Args:
            txt_url (str): The entered playlist URL.
            e: The event object (not used).
        """
        print("HERE WE SUBMIT THE PLAYLIST")
        self.make_playlist_upload_request(self.txt_url.value)
        print("DONE")

    def download_audio(self, empty):
        """


        :return:
        """
        self.make_download_audio_request(self.txt_url.value)

    def download_playlist(self, empty):
        self.make_download_playlist_request(self.txt_url.value)

    def make_audio_upload_request(self, link):
        """
        Make a POST request to upload an audio file.

        Args:make_audio_upload_request
            link (str): The audio URL to upload.
        """
        print("MAKE AUDIO UPLOAD REQUEST")
        request_data = {"audio_url": link}
        print("the request data:\n", request_data)
        response = make_post_request('http://' + self.host_address + ':' + self.host_port + '/api/global/uploadAudio', request_data)
        print("RESPONSE:\t", response)
        if response is None:
            # If the request failed, show an error dialog
            self.show_error_dialog("Error", "Failed to upload audio.")
        elif response.status_code == 200:
            #  TODO: Success dialog with a custom message
            print(200)
            self.show_simple_alert_dialog("File uploaded!", "Audio uploaded successfully.", True, 10)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized", "The audio was not uploaded because your YouTube Music token was not authorized to do the upload."
                                                   "Refresh your token and try again.")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))

    def make_playlist_upload_request(self, link):
        """
        Make a POST request to upload a playlist.

        Args:
            link (str): The playlist URL to upload (not implemented).
        """
        print("MAKE AUDIO UPLOAD REQUEST")
        request_data = {"playlist_url": link}
        print("the request data:\n", request_data)
        response = make_post_request('http://' + self.host_address + ':' + self.host_port + '/api/global/uploadPlaylist',
                                     request_data)
        print("RESPONSE:\t", response)
        if response is None:
            # If the request failed, show an error dialog
            self.show_error_dialog("Error", "Failed to upload playlist.")
        elif response.status_code == 200:
            #  TODO: Success dialog with a custom message
            print(200)
            self.show_simple_alert_dialog("Playlist uploaded!", "Success.", True, 10)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized",
                                   "The playlist was not uploaded because your YouTube Music token was not authorized to do the upload."
                                   "Refresh your token and try again.")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))

    def make_download_audio_request(self, link):
        """
        Make a POST request to download an audio.

        Args:
            link (str): The playlist URL to upload (not implemented).
        """
        print("MAKE AUDIO DOWNLOAD REQUEST")
        request_data = {"audio_url": link}
        print("the request data:\n", request_data)
        response = make_post_request(
            'http://' + self.host_address + ':' + self.host_port + '/api/global/downloadAudio',
            request_data)
        print("RESPONSE:\t", response)
        if response is None:
            # If the request failed, show an error dialog
            self.show_error_dialog("Error", "Failed to download audio.")
        elif response.status_code == 200:
            #  TODO: Success dialog with a custom message
            print(200)
            self.show_simple_alert_dialog("Audio downloaded!", "Success.", True, 10)
            data = response.content
            file_name = uuid.uuid4()
            with open("assets/uploads/" + str(file_name), 'wb') as s:
                s.write(data)

            url = "http://" + self.self_host_address + ":" +  self.self_host_port + "/assets/uploads/" + str(file_name)
            self.page.launch_url(url)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized",
                                   "The audio was not downloaded")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))

    def make_download_playlist_request(self, link):
        """
        Make a POST request to download a playlist.

        Args:
            link (str): The playlist URL to upload (not implemented).
        """
        print("MAKE PLAYLIST DOWNLOAD REQUEST")
        request_data = {"audio_url": link}
        print("the request data:\n", request_data)
        response = make_post_request(
            'http://' + self.host_address + ':' + self.host_port + '/api/global/downloadPlaylist',
            request_data)
        print("RESPONSE:\t", response)
        if response is None:
            # If the request failed, show an error dialog
            self.show_error_dialog("Error", "Failed to download playlist.")
        elif response.status_code == 200:
            #  TODO: Success dialog with a custom message
            print(200)
            self.show_simple_alert_dialog("Playlist downloaded!", "Success.", True, 10)
            data = response.content
            file_name = uuid.uuid4()
            with open("assets/uploads/" + str(file_name), 'wb') as s:
                s.write(data)

            url = "http://" + self.self_host_address + ":" +  self.self_host_port + "/assets/uploads/" + str(file_name)
            self.page.launch_url(url)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized",
                                   "The playlist was not downloaded")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))


def main(page: Page):
    host_address = os.environ.get("BACKEND_HOST")
    host_port = os.environ.get("BACKEND_PORT")

    self_host_address = os.environ.get("FRONTEND_HOST")
    self_host_port = os.environ.get("FRONTEND_PORT")

    if host_address is None:
        host_address = "127.0.0.1"

    if host_port is None:
        host_port = "5000"

    if self_host_address is None:
        self_host_address = "127.0.0.1"

    if self_host_port is None:
        self_host_port = "5010"


    frontend = FrontEnd(page, host_address, host_port, self_host_address, self_host_port)
    page.go(page.route)


if __name__ == '__main__':
    app(main, view=AppView.WEB_BROWSER, assets_dir="assets", port=5010, host="0.0.0.0", upload_dir="assets/uploads")
