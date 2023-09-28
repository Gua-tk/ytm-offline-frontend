#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flet import (
    ElevatedButton,
    Text,
    TextButton,
    Switch,
    IconButton,
    AlertDialog,
    MainAxisAlignment,
    View,
    Icon,
    AppBar,
    PopupMenuItem,
    PopupMenuButton,
    TextField,
    TextStyle,
    colors,
)


def open_dlg(page, dlg):
    page.dialog = dlg
    dlg.open = True
    page.update()


def close_dlg(page):
    dlg = page.dialog
    dlg.open = False
    page.update()


def create_switch(label_text, func):
    return Switch(
        label=label_text,
        on_change=func
    )


def create_icon_button(func, tooltip, icon, selected_icon, color, selected_color, selected=False, icon_size=35):
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


def create_simple_view(route_path, *controls):
    items = []
    for control in controls:
        items.append(control)

    return View(
        route_path,
        items
    )


def create_custom_view(result, view_path, view_name, view_function):
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
            create_button("Submit", view_function)
        ],
    )


def create_button(text, func, icon="", ref="", disabled=False):
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


def create_simple_alert_dialog(title, content_text, dismiss_func=lambda e: print("Dialog dismissed!"), alignment=MainAxisAlignment.END):
    return AlertDialog(
        title=Text(title),
        content=Text(content_text),
        on_dismiss=dismiss_func,
        actions_alignment=alignment
    )


def create_modal_alert_dialog(title, content_text, yes_func, no_func, dismiss_func=lambda e: print("Modal dialog dismissed!"), alignment=MainAxisAlignment.END):
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


def create_appbar(text, bg_color):
    return AppBar(
        title=Text(text),
        bgcolor=bg_color
    )


def create_popup_menu_item(text, icon, func):
    return PopupMenuItem(
        text=text,
        icon=icon,
        on_click=func
    )


def create_popup_menu_button(*popup_menu_items):
    menu_items = []

    for popup_menu_item in popup_menu_items:
        menu_items.append(popup_menu_item)
        # Add an empty PopupMenuButton
        menu_items.append(PopupMenuButton())

    return PopupMenuButton(
        items=menu_items[:-1]
    )


def create_simple_text(text):
    return Text(
        text
    )


def create_text(text, size, color="#000000"):
    return Text(
        text,
        size=size,
        color=color
    )


def create_text_style(color):
    return TextStyle(
        color=color
    )


def create_simple_textfield(label_text):
    return TextField(
        label=label_text
    )


def create_custom_textfield(hint_text, hint_style, bgcolor, text_style, border_radius, border_color,
                            focused_border_color, password=False, can_reveal_password=False):
    return TextField(
        hint_text=hint_text,
        hint_style=hint_style,
        bgcolor=bgcolor,
        text_style=text_style,
        border_radius=border_radius,
        border_color=border_color,
        focused_border_color=focused_border_color,
        password=password,
        can_reveal_password=can_reveal_password,
    )


def create_simple_icon(icon):
    return Icon(
        icon
    )


def create_colored_icon(icon, color):
    return Icon(
        icon,
        color=color
    )
