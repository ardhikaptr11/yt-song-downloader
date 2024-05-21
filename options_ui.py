import os
import subprocess
import time
from typing import Dict

import customtkinter as ctk
import windows_toasts as wt
from app import App, daemon_threaded
from downloader import download_song
from options_builder import (
    DownloadButton,
    DropdownInfo,
    ProgressbarInfo,
    RadiobuttonInfo,
)
from streams_retriever import StreamsRetriever
from windows_toasts import ToastActivatedEventArgs, ToastButton


class OptionsUI(ctk.CTkToplevel):
    WIDTH = 700
    HEIGHT = 350

    def __init__(self, option_info: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Escape>", self.close)
        self.geometry(f"{OptionsUI.WIDTH}x{OptionsUI.HEIGHT}")
        self.title("YTSong Downloader by Ardhika - Download Options")

        self.after(250, self.set_icon)
        self.resizable(False, False)

        self.AUMID: str = None
        self.url: str = None
        self.itag: int = None
        self.__selected_choice: list = []
        self.selected_item: str = None
        self.dropdown_mp4_active: bool = True

        self.download_complete: bool = False

        self.widgets: Dict[str, ctk.CTkBaseClass] = {}
        self.labels: Dict[str, ctk.CTkLabel] = {}
        self.frames: Dict[str, ctk.CTkFrame] = {}

        self.n_options = len(option_info.keys())

        for i in range(self.n_options):
            self.rowconfigure(i + 1, weight=0)
        self.rowconfigure(self.n_options + 1, weight=1)
        self.rowconfigure(self.n_options + 2, weight=0)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        for row, (key, value) in enumerate(option_info.items(), start=1):
            if isinstance(value, RadiobuttonInfo):
                self.create_radiobuttons(key, value, row)
            elif isinstance(value, DropdownInfo):
                self.create_dropdown(key, value, row)
            elif isinstance(value, DownloadButton):
                self.create_download_button(key, value)
            elif isinstance(value, ProgressbarInfo):
                self.create_progressbar(key, value)
            else:
                raise ValueError("Invalid Option Type")

    def set_icon(self):
        icon_path = App.resource_path(App.relative_to_assets("Apps-logo.ico"))
        self.iconbitmap(icon_path)

    def create_radiobuttons(self, key, value, row):
        self.labels[key] = ctk.CTkLabel(
            master=self,
            text=value.title,
            font=("Helvetica", 18 * -1, "bold"),
            text_color="#D4CBB8",
        )
        self.labels[key].grid(row=row, column=0, padx=10, pady=20)
        self.frames[key] = ctk.CTkFrame(
            master=self,
            fg_color="#242424",
        )

        for i in range(len(value.values)):
            self.frames[key].columnconfigure(i, weight=1)

        self.frames[key].grid(row=row, column=1, sticky="ew", padx=(0, 10))
        self.widgets[key] = []
        self.radio_var = ctk.StringVar(value=value.values[0])

        for i, value in enumerate(value.values):
            self.widgets[key].append(
                ctk.CTkRadioButton(
                    master=self.frames[key],
                    text=value,
                    variable=self.radio_var,
                    value=value,
                    text_color="#BCA0DC",
                    fg_color="#6C59C9",
                    hover_color="#2E9599",
                    border_color="#6D5ACA",
                    font=("Helvetica", 16 * -1, "bold"),
                    command=self.get_selected_option,
                )
            )
            self.widgets[key][i].grid(row=0, column=i, sticky="ew", padx=10, pady=5)

    def create_dropdown(self, key, value, row):
        self.labels[key] = ctk.CTkLabel(
            master=self,
            text=value.title,
            font=("Helvetica", 18 * -1, "bold"),
            text_color="#D4CBB8",
        )
        self.labels[key].grid(row=row, column=0, padx=10, pady=0)

        self.dropdown_var = ctk.StringVar(value="Select an option")

        self.widgets[key] = ctk.CTkOptionMenu(
            master=self,
            values=value.values,
            variable=self.dropdown_var,
            corner_radius=20,
            fg_color="#BCA0DC",
            text_color="#311155",
            font=("Helvetica", 14 * -1, "bold"),
            dropdown_font=("Helvetica", 16 * -1, "bold"),
            dropdown_text_color="#311155",
            dropdown_hover_color="#bca0dc",
            dropdown_fg_color="#FFFFFF",
            button_color="#6d5aca",
            button_hover_color="#d4cbb8",
            text_color_disabled="#4d4d4d",
            state=value.state,
            command=self.get_selected_item,
        )
        self.widgets[key].grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=10)

    def create_download_button(self, key, value):
        self.labels[key] = ctk.CTkLabel(
            master=self,
            text="",
            font=("Helvetica", 16 * -1, "normal"),
            text_color="#D4CBB8",
        )

        self.labels[key].place(anchor="center", x=350, y=190)

        self.widgets[key] = ctk.CTkButton(
            master=self,
            width=150,
            height=50,
            text=value.text,
            fg_color="#242424",
            text_color="#FFFDD0",
            hover_color="#BCA0DC",
            font=("Helvetica", 18 * -1, "bold"),
            border_width=5,
            border_color="#6D5ACA",
            text_color_disabled="#4d4d4d",
            state=value.state,
            command=self.download_now,
        )
        self.widgets[key].place(anchor="center", x=350, y=300)

    def create_progressbar(self, key, value):
        self.labels[key] = ctk.CTkLabel(
            master=self,
            text=value.text,
            font=("Helvetica", 18 * -1, "bold"),
            text_color="#6D5ACA",
        )
        self.labels[key].place(anchor="center", x=350, y=230)

        self.widgets[key] = ctk.CTkProgressBar(
            master=self, width=600, corner_radius=20, progress_color="#BCA0DC"
        )
        self.widgets[key].set(value.current_pos)
        self.widgets[key].place(anchor="center", x=350, y=250)

    def get_selected_option(self):
        current_selected = self.radio_var.get()
        if current_selected == "Video File":
            self.widgets["audio_quality_mp3"].configure(state="disabled")
            self.widgets["video_quality_mp4"].configure(state="normal")
            self.dropdown_mp4_active = True
        else:
            self.widgets["audio_quality_mp3"].configure(state="normal")
            self.widgets["video_quality_mp4"].configure(state="disabled")
            self.dropdown_mp4_active = False

    def get_selected_item(self, choice):
        self.selected_item = choice

        if self.download_complete:
            self.widgets["download"].configure(state="normal")
            self.labels["download"].configure(text="")
            self.labels["progress"].configure(text="0 %")
            self.widgets["progress"].set(0)

        if self.selected_item not in self.__selected_choice:
            self.widgets["download"].configure(state="normal")
        else:
            self.widgets["download"].configure(state="disabled")

    @daemon_threaded
    def get_itag_from_selected(self):
        retriever = StreamsRetriever(
            self.url, "mp4" if self.dropdown_mp4_active else "mp3"
        )

        retrieval_thread = retriever.start_retrieving()

        retrieval_thread.join()

        all_stream = {
            **retriever.stream_items_mp4,
            **retriever.stream_items_mp3,
        }

        for key, value in all_stream.items():
            if value == self.selected_item:
                self.itag = key
                break

    @daemon_threaded
    def download_now(self):
        self.grab_set_global()

        get_itag_thread = self.get_itag_from_selected()
        get_itag_thread.join()

        user_profile = os.environ["USERPROFILE"]

        root_path = os.path.realpath(os.path.join(user_profile, "music"))

        self.destination_path = (
            os.path.realpath(f"{root_path}/Video - YTDownloader by Ardhika")
            if self.dropdown_mp4_active
            else os.path.realpath(f"{root_path}/Audio - YTDownloader by Ardhika")
        )

        try:
            downloaded_song = os.listdir(self.destination_path)
        except FileNotFoundError:
            os.mkdir(self.destination_path)
            downloaded_song = os.listdir(self.destination_path)

        self.labels["download"].configure(
            text="Sebentar yaa aku cek dulu lagu punya kamu!\n",
            font=("Helvetica", 16 * -1, "bold"),
            text_color="#D4CBB8",
        )

        if self.dropdown_mp4_active:
            song = download_song(
                url=self.url,
                itag=self.itag,
                progress_callback=self.on_progress,
                path=self.destination_path,
            )
        elif not self.dropdown_mp4_active:
            song = download_song(
                url=self.url,
                itag=self.itag,
                progress_callback=self.on_progress,
                path=self.destination_path,
                is_video=False,
            )

        if song in downloaded_song:
            self.labels["download"].configure(
                text="Setelah aku telusuri, lagumu sudah ada di penyimpanan."
            )
            self.grab_release()
            time.sleep(2)

        if self.labels["progress"].cget("text") == "100 %":
            interactableToaster = wt.InteractableWindowsToaster(
                "YTSong Downloader By Ardhika", self.AUMID
            )
            text_fields = ["Lagumu sudah aku downloadin yaa, selamat mendengarkan!"]
            toast = wt.Toast(text_fields)
            toast.AddAction(
                ToastButton("Terima kasih ! Aku buka yaa", self.destination_path)
            )
            toast.on_activated = self.open_destination_path
            interactableToaster.show_toast(toast)
            self.grab_release()

        self.labels["download"].configure(text="")

    # A callback function to make the progress bar work
    def on_progress(self, stream, chunk, bytes_remaining):
        self.total_size = stream.filesize
        self.bytes_downloaded = self.total_size - bytes_remaining
        self.progress = (self.bytes_downloaded / self.total_size) * 100
        self.percentage = str(int(self.progress))
        self.labels["progress"].configure(text=f"{self.percentage} %")
        self.labels["progress"].update()

        self.after(0, self.update_progress)

    # To update the progress bar
    def update_progress(self):
        self.labels["progress"].configure(text=f"{self.percentage} %")
        self.widgets["progress"].set(float(self.progress) / 100)

        self.widgets["download"].configure(state="disabled")
        self.__selected_choice.append(self.selected_item)
        self.download_complete = True

    def open_destination_path(self, event: ToastActivatedEventArgs):
        subprocess.Popen(f'explorer "{event.arguments}"')

    def close(self, event):
        self.destroy()
