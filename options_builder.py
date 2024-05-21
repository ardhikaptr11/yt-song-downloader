import customtkinter as ctk


class OptionsConstructor:
    def __init__(self):
        self.options = {}

    def add_radiobox_options(self, key: str, title: str, values: list):
        self.options[key] = RadiobuttonInfo(title, values)

    def add_dropdown_options(
        self, key: str, title: str, values: list, state: str = "normal"
    ):
        self.options[key] = DropdownInfo(title, values, state)

    def add_download_button(self, key: str, text: str, state: str = "disabled"):
        self.options[key] = DownloadButton(text, state)

    def add_progressbar(self, key: str, current_pos: float = 0, text="0 %"):
        self.options[key] = ProgressbarInfo(current_pos, text)

    def create_ui(self) -> ctk.CTkToplevel:
        from options_ui import OptionsUI

        return OptionsUI(self.options)


class RadiobuttonInfo:
    def __init__(self, title: str, values: list):
        self.title = title
        self.values = values


class DropdownInfo:
    def __init__(self, title: str, values: list, state: str):
        self.title = title
        self.values = values
        self.state = state


class DownloadButton:
    def __init__(self, text: str, state: str):
        self.text = text
        self.state = state


class ProgressbarInfo:
    def __init__(self, current_pos: float, text: str):
        self.current_pos = current_pos
        self.text = text
