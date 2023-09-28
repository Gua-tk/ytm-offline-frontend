#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid as uuid
from flet import (
    AppBar,
    Page,
    View,
    Container,
    Theme,
    FilePicker,
    Icon,
    FilePickerResultEvent,
    FilePickerUploadEvent,
    FilePickerUploadFile,
    ProgressRing,
    Ref,
    Column,
    Row,
    alignment,
    margin,
    icons,
    animation,
    Checkbox,
    ButtonStyle,
    TextStyle,
    MaterialState,
    RoundedRectangleBorder,
    app,
    AppView
)
import requests
from typing import Dict
from time import sleep

from flet_constructors import *


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


def make_post_file_request(url, file):
    """
    Make a POST request to the specified file with JSON data.

    Args:
        url (str): The URL to send the POST request to.
    """
    try:
        response = requests.post(url, files=file)
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
        #self.page.theme_mode = "light"
        #self.theme_mode_icon = icons.DARK_MODE

        self.page.theme = Theme(font_family="JetBrainsMono")
        self.page.dark_theme = Theme(font_family="JetBrainsMono")
        self.theme_mode_text = "Dark Mode"

        # Define route buttons
        # Audio URL PopupMenuItem
        self.audio_url_icon_button = create_icon_button(
            lambda _: self.page.go("/audio"),
            "Audio URL",
            icons.AUDIOTRACK,
            icons.AUDIOTRACK_OUTLINED,
            colors.GREY,
            colors.RED
        )

        # Playlist URL PopupMenuItem
        self.playlist_url_icon_button = create_icon_button(
            lambda _: self.page.go("/playlist"),
            "Playlist URL",
            icons.WEBHOOK,  # Replace with the appropriate icon for Playlist URL
            icons.WEBHOOK_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Audio Upload PopupMenuItem
        self.audio_upload_icon_button = create_icon_button(
            lambda _: self.page.go("/audio/upload"),
            "Audio Upload",
            icons.AUDIO_FILE,
            icons.AUDIO_FILE_OUTLINED,
            colors.GREY,
            colors.RED
        )

        # Playlist Upload PopupMenuItem
        self.playlist_upload_icon_button = create_icon_button(
            lambda _: self.page.go("/playlist/upload"),
            "Playlist Upload",
            icons.LIST,  # Replace with the appropriate icon for Playlist Upload
            icons.LIST_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Audio Upload 2 PopupMenuItem
        self.audio_upload_2_icon_button = create_icon_button(
            lambda _: self.page.go("/audio/download"),
            "Download Audio from YouTube Video",
            icons.DOWNLOAD,  # Replace with the appropriate icon for Audio Upload 2
            icons.DOWNLOAD_DONE_OUTLINED,  # Replace with the appropriate outlined icon
            colors.GREY,
            colors.RED
        )

        # Playlist Upload 2 PopupMenuItem
        self.playlist_upload_2_icon_button = create_icon_button(
            lambda _: self.page.go("/playlist/download"),
            "Download Playlist from YouTube",
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

    def change_theme(self, e):
        # Toggle between light and dark themes
        self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"

        self.page.update()

    def create_menu(self):
        """
        Create the main menu bar (AppBar).

        Returns:
            AppBar: The main menu bar.
        """

        return AppBar(
            leading=create_simple_icon(icons.DOWNLOAD_FOR_OFFLINE),
            leading_width=40,
            title=create_simple_text("ytm-manager"),
            center_title=False,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                self.audio_url_icon_button,
                self.playlist_url_icon_button,
                self.audio_upload_icon_button,
                self.playlist_upload_icon_button,
                self.audio_upload_2_icon_button,
                self.playlist_upload_2_icon_button,
                create_popup_menu_button(
                    create_popup_menu_item("Theme", icons.DARK_MODE, self.change_theme),
                    create_popup_menu_item("Log In", icons.ACCESSIBILITY_NEW, lambda _: self.page.go("/"))
                )
            ]
        )

    def create_register_page_body(self):
        self.page.vertical_alignment = "center"
        self.page.horizontal_alignment = "center"

        ctx = Container(
            bgcolor="red",
            alignment=alignment.center,
            border_radius=100,
            padding=20,
            height=800,
            animate=animation.Animation(duration=300, curve="easyInOut"),
            content=Column(
                controls=[
                    Container(
                        width=320,
                        margin=margin.only(left=110, right=10),
                        alignment=alignment.center,
                        content=create_text(
                            "Please enter your information below in order to create a new account",
                            14
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=15),
                        content=Column(
                            controls=[
                                create_custom_textfield(
                                    "Username",
                                    create_text_style("grey"),
                                    "white",
                                    create_text_style("black"),
                                    15,
                                    colors.BLACK,
                                    colors.ORANGE_700,
                                ),
                                create_custom_textfield(
                                    "Email",
                                    create_text_style("grey"),
                                    "white",
                                    create_text_style("black"),
                                    15,
                                    colors.BLACK,
                                    colors.ORANGE_700,
                                ),
                                create_custom_textfield(
                                    "Password",
                                    create_text_style("grey"),
                                    "white",
                                    create_text_style("black"),
                                    15,
                                    colors.BLACK,
                                    colors.ORANGE_700,
                                    True,
                                    True
                                ),
                                create_custom_textfield(
                                    "Confirm Password",
                                    create_text_style("grey"),
                                    "white",
                                    create_text_style("black"),
                                    15,
                                    colors.BLACK,
                                    colors.ORANGE_700,
                                    True,
                                    True
                                )
                            ]
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=10),
                        content=ElevatedButton(
                            "Sign Up",
                            width=300,
                            height=55,
                            on_click=lambda _:print("CONFIRM SIGN UP"),
                            style=ButtonStyle(
                                bgcolor=colors.ORANGE_700,
                                color=colors.WHITE,
                                shape={
                                    MaterialState.FOCUSED: RoundedRectangleBorder(radius=15),
                                    MaterialState.DEFAULT: RoundedRectangleBorder(radius=15),
                                    MaterialState.HOVERED: RoundedRectangleBorder(radius=15),
                                }
                            )
                        )
                    )
                ]
            )
        )
        return ctx

    def create_page_body(self):
        """
        Create the main content of the page.
        """
        self.page.vertical_alignment = "center"
        self.page.horizontal_alignment = "center"

        ctx = Container(
            bgcolor="red",
            alignment=alignment.center,
            border_radius=100,
            padding=20,
            height=800,
            animate=animation.Animation(
                duration=300,
                curve="easyInOut"
            ),
            content=Column(
                controls=[
                    Container(
                        width=300,
                        margin=margin.only(left=135, right=10, top=25),
                        content=Text(
                            "Login",
                            size=30,
                            color="white",
                            weight="w700"
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=35),
                        content=Column(
                            controls=[
                                Row([
                                    create_custom_textfield(
                                        "Username",
                                        create_text_style("grey"),
                                        "white",
                                        create_text_style("black"),
                                        15,
                                        colors.BLACK,
                                        colors.WHITE70
                                    ),
                                    create_colored_icon(icons.PERSON_ROUNDED, color="white")
                                ])
                            ]
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=5),
                        content=Column(
                            controls=[
                                Row([
                                    create_custom_textfield(
                                        "Password",
                                        create_text_style("grey"),
                                        "white",
                                        create_text_style("black"),
                                        15,
                                        colors.BLACK,
                                        colors.WHITE70,
                                        True,
                                        True
                                    ),
                                    create_colored_icon(icons.PASSWORD_ROUNDED, color="white")
                                ])
                            ]
                        )
                    ),
                    Row([
                        Checkbox(
                            value=False,
                            on_change=lambda _:print("checkbox toggle")
                        ),
                        create_text("Remember me", 14, "white"),
                        Container(
                            width=150,
                            margin=margin.only(left=25, right=10),
                            content=TextButton(
                                "Forgot Password?",
                                style=ButtonStyle(
                                    color="white",
                                ),
                                on_click=lambda _:print("You forgot your password")
                            )
                        )
                    ]),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=10),
                        content=ElevatedButton(
                            "Login",
                            width=300,
                            height=55,
                            style=ButtonStyle(
                                color="white",
                                bgcolor=colors.ORANGE_700,
                                shape={
                                    MaterialState.FOCUSED: RoundedRectangleBorder(radius=5),
                                    MaterialState.HOVERED: RoundedRectangleBorder(radius=5),
                                },
                                padding=20,
                            ),
                            on_click=lambda _: print("LOGIN BUTTON PRESSET")
                        )
                    ),
                    Container(
                        width=300,
                        margin=margin.only(left=20, right=20, top=15),
                        content=Text(
                            "Don't have an account?",
                            size=14,
                            text_align="center",
                            color="white",
                        )
                    ),
                    Container(
                        width=150,
                        margin=margin.only(left=100, right=20),
                        content=TextButton(
                            "Register",
                            style=ButtonStyle(
                                color="white"
                            ),
                            on_click=lambda _: self.page.go("/register")
                        )
                    ),

                ]
            )
        )
        return ctx

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

    def create_register_view(self):
        return View(
            "/register",
            [
                create_appbar("Register", colors.SURFACE_VARIANT),
                self.create_register_page_body()
            ]
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
        elif 1 < self.total_files_to_upload == self.successfully_uploaded_files:
            self.show_simple_alert_dialog(
                "Files Uploaded",
                f"All {self.total_files_to_upload} files have been uploaded!",
                False
            )

    def show_error_dialog(self, title_text, error_message):
        """
        Show an error dialog with a title and error message.

        Args:
            title_text (str): The title of the error dialog.
            error_message (str): The error message to display.
        """
        # Show the error dialog
        open_dlg(self.page, create_simple_alert_dialog(title_text, error_message))

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
                create_appbar(view_name, colors.SURFACE_VARIANT),
                create_simple_text("This is the " + view_name + " Page"),
                create_button(
                    "Select files...",
                    lambda _: self.file_picker.pick_files(
                        allow_multiple=False,
                        allowed_extensions=["mp3"],
                    ),
                    icon=icons.FOLDER_OPEN
                ),
                Column(ref=self.files),
                create_button("Upload", self.upload_files, icons.UPLOAD, self.upload_button, True)
            ],
        )

    def show_simple_alert_dialog(self, title_text, content_text, is_auto_closed=True, delay=2):
        # Create an alert dialog with the given title and content
        alert_dialog = create_simple_alert_dialog(title_text, content_text)

        # Show the dialog
        open_dlg(self.page, alert_dialog)

        # Close the dialog and print the message when all files are uploaded
        if is_auto_closed:
            sleep(delay)
            close_dlg(self.page)

    def show_modal_alert_dialog(self, title_text, content_text, yes_func, no_func):
        # Create an alert dialog with the given title and content
        alert_dialog = create_modal_alert_dialog(title_text, content_text, yes_func, no_func)

        # Show the dialog
        open_dlg(self.page, alert_dialog)

    def route_change(self, e=None):
        """
        Handle route changes and update views accordingly.

        Args:
            e: The event object (not used).
        """
        self.page.views.clear()
        self.page.views.append(self.create_main_view())

        if self.page.route == "/audio":
            self.txt_url = create_simple_textfield("Enter song URL")
            print("INITIALIZING TEXT URL WITH THE TEXT", self.txt_url.value)
            self.page.views.append(
                create_custom_view(self.txt_url, "/audio", "Audio URL", self.submit_audio)
            )
            print("View is created.")

        if self.page.route == "/playlist":
            self.txt_url = create_simple_textfield("Enter playlist URL")
            self.page.views.append(
                create_custom_view(self.txt_url, "/playlist", "Playlist URL", self.submit_playlist)
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
            self.txt_url = create_simple_textfield("Enter audio URL")
            self.page.views.append(
                create_custom_view(self.txt_url, "/audio/download", "Download Audio", self.download_audio)
            )

        if self.page.route == "/playlist/download":
            self.txt_url = create_simple_textfield("Enter playlist URL")
            self.page.views.append(
                create_custom_view(self.txt_url, "/playlist/download", "Download Playlist", self.download_playlist)
            )

        if self.page.route == "/login":
            print("login")
            self.txt_url = create_simple_textfield("Log In")
            self.page.views.append(
                create_custom_view(self.txt_url, "/login", "Log In", self.submit_playlist)
            )

        if self.page.route == "/register":
            self.page.views.append(
                self.create_register_view()
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

    def submit_playlist(self, e=None):
        """
        Handle playlist submission when the "Submit" button is clicked.

        Args:
            e: The event object (not used).
        """
        print("HERE WE SUBMIT THE PLAYLIST")
        self.make_playlist_upload_request(self.txt_url.value)
        print("DONE")

    def download_audio(self, e):
        """


        :return:
        """
        self.make_download_audio_request(self.txt_url.value)

    def download_playlist(self, e):
        self.make_download_playlist_request(self.txt_url.value)

    def upload_audio(self):
        self.make_audio_file_upload_request()

    def upload_playlist(self):
        self.make_playlist_file_upload_request(self.file_picker)

    def make_audio_upload_request(self, link):
        """
        Make a POST request to upload an audio file.

        Args:make_audio_upload_request
            link (str): The audio URL to upload.
        """
        print("MAKE AUDIO UPLOAD REQUEST")
        request_data = {"audio_url": link}
        print("the request data:\n", request_data)
        response = make_post_request(
            'http://' + self.host_address + ':' + self.host_port + '/api/global/uploadAudio',
            request_data
        )
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
            self.show_error_dialog(
                "Unauthorized",
                "The audio was not uploaded because your YouTube Music token was not authorized to do the upload."
                "Refresh your token and try again."
            )
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
        response = make_post_request(
            'http://' + self.host_address + ':' + self.host_port + '/api/global/uploadPlaylist',
            request_data
        )
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
                                   "The playlist was not uploaded because your YouTube Music token was not authorized "
                                   "to do the upload."
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

            url = "http://" + self.self_host_address + ":" + self.self_host_port + "/assets/uploads/" + str(file_name)
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
        request_data = {"playlist_url": link}
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

            url = "http://" + self.self_host_address + ":" + self.self_host_port + "/assets/uploads/" + str(file_name)
            self.page.launch_url(url)
        elif response.status_code == 401:
            # If the request failed, show an error dialog
            self.show_error_dialog("Unauthorized",
                                   "The playlist was not downloaded")
        else:
            self.show_error_dialog("Error", "There server responded:\t" + str(response.status_code))

    def make_audio_file_upload_request(self, file_picker_upload_file):
        url = 'http://' + self.host_address + ':' + self.host_port + '/api/global/uploadReceivedAudio'
        file_path = 'assets/uploads/' + file_picker_upload_file.name
        with open(file_path, 'rb') as f:
            r1 = {file_picker_upload_file.name: f}
            response = make_post_file_request(
                url,
                r1
            )
        print("THE RESPONSE:")
        print(response)

    def make_playlist_file_upload_request(self, files):
        pass


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
