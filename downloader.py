import os
import subprocess

import windows_toasts as wt
from pytube import YouTube
from windows_toasts import ToastActivatedEventArgs, ToastButton


def download_song(
    url: str,
    itag: int,
    progress_callback,
    path: str,
    is_video: bool = True,
) -> str:
    """
    Downloads a song or video from YouTube.

    Args:
        url (str): The address where YouTube video is located.
        itag (int): A YouTube video stream format code.
        progress_callback: A callback function to track the download progress.
        path (str): The path to save the downloaded song or video.
        is_video (bool, optional): Indicates whether the download is for a video or audio. Defaults to True.

    Returns:
        str: The filename of the downloaded song or video.
    """

    video = YouTube(
        url,
        on_progress_callback=progress_callback,
    )

    stream = video.streams.get_by_itag(itag)

    filename = stream.default_filename
    name, extension = os.path.splitext(filename)  # Output: list['filename', '.mp4']

    if not is_video:
        extension = ".mp3"
        filename = f"{name}{extension}"

    # A list of downloaded video or audio files in the path
    downloaded_songs = os.listdir(path)

    downloaded_songs_size = [
        os.path.getsize(os.path.join(path, song)) for song in downloaded_songs
    ]

    # An approach to handle if the video or audio file is already downloaded indicated from the filename and its filesize.
    if filename in downloaded_songs and stream.filesize in downloaded_songs_size:
        interactableToaster = wt.toasters.InteractableWindowsToaster(
            "YTSong Downloader by Ardhika", "YTSongDownloaderByArdhika"
        )
        toast = wt.Toast(["Lagumu sudah pernah aku downloadin, dicek dulu ya!"])
        toast.AddAction(ToastButton("Buka Folder", path))
        toast.on_activated = open_destination_path
        interactableToaster.show_toast(toast)

    # If the filename is exists in the path but has the different filesize, then add a prefix to the filename
    elif filename in downloaded_songs and stream.filesize not in downloaded_songs_size:
        prefix = 1
        filename = f"{name} ({prefix}){extension}"

        while filename in downloaded_songs:
            prefix += 1
            filename = f"{name} ({prefix}){extension}"
        stream.download(output_path=path, filename=filename)
        return filename

    else:
        stream.download(output_path=path, filename=filename)

    return filename


# A Callback function to open the path where the downloaded video or audio is located directly from the toast notification
def open_destination_path(event: ToastActivatedEventArgs):
    destination_path = event.arguments
    subprocess.Popen(f'explorer "{destination_path}"')
