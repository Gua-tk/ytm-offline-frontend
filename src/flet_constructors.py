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
    AppBar,
    colors,
)


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
