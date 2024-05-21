import os
import re
import sys
import tkinter as tk
import winreg
from ctypes import byref, c_int, sizeof, windll
from pathlib import Path
from threading import Thread
from typing import Optional

import customtkinter as ctk
import windows_toasts as wt
from pytube import YouTube

windll.shcore.SetProcessDpiAwareness(2)
ctk.deactivate_automatic_dpi_awareness()


def daemon_threaded(func):
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread

    return wrapper


class App(tk.Tk):
    WIDTH = 600
    HEIGHT = 400

    OUTPUT_PATH = Path(__file__).parent
    ASSETS_PATH = OUTPUT_PATH / Path(
        "E:\\Folder Dhika\\Python Project\\YTDownloader\\ytdownloader-app\\assets"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.AUMID = self.register_hkey(
            "YTSongDownloaderByArdhika",
            "YTSong Downloader by Ardhika",
            self.relative_to_assets("Apps-logo.ico"),
        )
        
        self.bind("<Escape>", self.close)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.title("YTSong Downloader By Ardhika")
        self.resizable(False, False)
        self.iconbitmap(self.resource_path(self.relative_to_assets("Apps-logo.ico")))
        self.placeholder_text = "e.g. https://www.youtube.com/watch?v=qSRA0snXbOg"

        self.HWND = windll.user32.GetParent(self.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(
            self.HWND, 35, byref(c_int(0x00202020)), sizeof(c_int)
        )

        self.options_ui = None
        self.options_ui_is_open = False
        self.init_ui()

    def init_ui(self):
        self.canvas = tk.Canvas(
            self,
            bg="#FFFFFF",
            height=400,
            width=600,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )

        self.appsBgImg = tk.PhotoImage(
            file=self.resource_path(self.relative_to_assets("apps-bg.png"))
        )
        self.cartoonFigure = tk.PhotoImage(
            file=self.resource_path(self.relative_to_assets("cartoon-bg.png"))
        )
        self.contactMe = tk.PhotoImage(
            file=self.resource_path(self.relative_to_assets("contact_me.png"))
        )
        self.entryImg = tk.PhotoImage(
            file=self.resource_path(self.relative_to_assets("entry_1.png"))
        )
        self.downloadBtnBg = tk.PhotoImage(
            file=self.resource_path(self.relative_to_assets("download_button.png"))
        )

        self.canvas.create_image(300.0, 200.0, image=self.appsBgImg)
        self.canvas.create_image(304.0, 48.0, image=self.cartoonFigure, anchor="n")
        self.canvas.create_image(8.0, 296.0, image=self.contactMe, anchor="nw")
        self.entryBg = self.canvas.create_image(300.0, 235.0, image=self.entryImg)

        self.canvas.create_text(
            300.0,
            122.0,
            anchor="n",
            text="Download lagumu sekarang!",
            fill="#6C59C9",
            font=("Montserrat", 28 * -1, "bold"),
        )

        self.canvas.create_text(
            300.0,
            156.0,
            anchor="n",
            text="Nikmati kemudahan download lagu dari YouTube tanpa ribet",
            fill="#FFFFFF",
            font=("Montserrat", 12 * -1, "bold"),
        )

        self.canvas.create_text(
            300.0,
            193.0,
            anchor="n",
            text="Masukkan link YouTube:",
            fill="#FFFFFF",
            font=("MontserratRoman", 12 * -1, "bold"),
        )
        # <-----Create the Entry Box----->
        self.entryBox = self.link_entrybox()
        self.entryBox.bind("<Button-1>", self.on_click)
        self.entryBox.bind("<Leave>", self.on_leave)

        # <-----Create the Download Button----->
        self.downloadBtn = self.download_button()

        self.canvas.place(x=0, y=0)

    def link_entrybox(self):
        self.entry = tk.Entry(
            font=("Montserrat", 14 * -1, "normal"),
            relief="flat",
            bg="#bca0dc",
            fg="#52515B",
            justify="center",
        )
        self.entry.insert(0, self.placeholder_text)
        self.entry.pack(side="top", pady=(215, 0), ipady=8.5, ipadx=100)
        return self.entry

    def download_button(self):
        self.button = tk.Button(
            image=self.downloadBtnBg,
            borderwidth=0,
            highlightthickness=0,
            command=self.downloadBtnClicked,
            relief="flat",
            cursor="hand2",
        )
        self.button.pack(side="bottom", pady=(0, 84))
        return self.button

    def downloadBtnClicked(self):
        url = self.entryBox.get()
        url_is_valid = self.validate_ytlink(url)

        interactableToaster = wt.InteractableWindowsToaster(
            "YTSong Downloader by Ardhika", self.AUMID
        )

        if url == self.placeholder_text:
            text_fields = ["Kamu belum masukkin link nih, coba lagi ya!"]
            toast = wt.Toast(text_fields)
            interactableToaster.show_toast(toast)
            return

        if not url_is_valid:
            text_fields = [
                "Nampaknya kamu memasukkan link yang tidak sah deh, coba lagi ya! "
            ]
            toast = wt.Toast(text_fields)
            interactableToaster.show_toast(toast)
            return

        downloaded_item_is_song = self.song_identifier(url)

        if url_is_valid and not downloaded_item_is_song:
            text_fields = [
                "Maaf, link yang kamu masukkan ga dikategorikan sebagai musik oleh YouTube.",
                "\nMasukkan link lainnya, dan coba lagi yaa!",
            ]
            toast = wt.Toast(text_fields)
            interactableToaster.show_toast(toast)
            return

        if url_is_valid and downloaded_item_is_song and not self.options_ui_is_open:
            self.options_ui_is_open = True
            self.build_options_ui()

    def build_options_ui(self):
        from options_builder import OptionsConstructor
        from streams_retriever import StreamsRetriever

        url = self.entryBox.get()
        option_info = OptionsConstructor()

        mp4_retriever, mp3_retriever = (
            StreamsRetriever(url),
            StreamsRetriever(url, "mp3"),
        )

        mp4_retrieval_thread, mp3_retrieval_thread = (
            mp4_retriever.start_retrieving(),
            mp3_retriever.start_retrieving(),
        )

        mp4_retrieval_thread.join()
        mp3_retrieval_thread.join()

        video_streamlist, audio_streamlist = (
            mp4_retriever.get_streams(),
            mp3_retriever.get_streams(),
        )

        option_info.add_radiobox_options(
            "format", "Download sebagai", ["Video File", "Audio File"]
        )
        option_info.add_dropdown_options(
            "video_quality_mp4",
            "Pilih variasi",
            video_streamlist,
        )
        option_info.add_dropdown_options(
            "audio_quality_mp3",
            "Pilih variasi",
            audio_streamlist,
            "disabled",
        )
        option_info.add_download_button("download", "Download")
        option_info.add_progressbar("progress")

        self.options_ui = option_info.create_ui()
        self.options_ui.AUMID = self.AUMID
        self.options_ui.url = url

        self.options_ui.grab_set() 
        self.options_ui.after(250, self.options_ui.lift)

        if self.options_ui_is_open:
            self.options_ui.protocol("WM_DELETE_WINDOW", self.on_options_ui_close)

    def on_options_ui_close(self):
        self.options_ui_is_open = False
        self.options_ui.grab_release()
        self.options_ui.destroy()

    def validate_ytlink(self, url):
        formats = [
            "https://www.youtube.com/watch?v=",
            "https://www.youtube.com/embed/",
            "https://youtu.be/",
        ]

        if any([format in url for format in formats]):
            pattern = r"(?:watch\?v=|embed\/|be\/)([0-9A-Za-z_-]{11})"
            regex = re.compile(pattern)
            watch_id = regex.search(url).group(1)
            if len(watch_id) != 11:
                return
            valid = True
            return valid
        return

    def song_identifier(self, title):
        yt = YouTube(title)
        videoDetails = yt.vid_info["videoDetails"]
        is_song = False
        if "heartbeatParams" in list(yt.vid_info.keys()) or "musicVideoType" in list(
            videoDetails.keys()
        ):
            is_song = True
            return is_song
        return is_song

    def on_click(self, event):
        if self.entryBox.get() == self.placeholder_text:
            self.entryBox.delete(0, "end")
            self.entryBox.configure(fg="#6d5aca", font=("Montserrat", 17 * -1, "bold"))

    def on_leave(self, event):
        if not self.entryBox.get():
            self.entryBox.configure(
                fg="#52515B", font=("Montserrat", 14 * -1, "normal")
            )
            self.entryBox.insert(0, self.placeholder_text)
            self.button.focus_set()

    # Credit: https://github.com/DatGuy1/Windows-Toasts/blob/main/scripts/register_hkey_aumid.py
    # Modified to fit the needs of the app
    def register_hkey(self, appId: str, appName: str, iconPath: Optional[Path]):
        winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"

        key_exists = self.check_key_exists(winreg.HKEY_CURRENT_USER, keyPath)

        if not key_exists:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as masterKey:
                winreg.SetValueEx(masterKey, "DisplayName", 0, winreg.REG_SZ, appName)
                if iconPath is not None:
                    winreg.SetValueEx(
                        masterKey, "IconUri", 0, winreg.REG_SZ, str(iconPath.resolve())
                    )
        return appId

    def check_key_exists(self, hive, key_path):
        try:
            winreg.OpenKey(hive, key_path)
            return True
        except FileNotFoundError:
            return False

    # Credit: https://stackoverflow.com/questions/22472124/what-is-sys-meipass-in-python
    @staticmethod
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    @staticmethod
    def relative_to_assets(path: str) -> Path:
        return App.ASSETS_PATH / Path(path)

    def run(self):
        self.mainloop()

    def close(self, event):
        self.destroy()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
