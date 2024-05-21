from pytube import YouTube
from app import daemon_threaded


class StreamsRetriever:
    def __init__(self, url: str, type="mp4"):
        self.url = url
        self.type = type
        self.stream_items_mp4 = {}
        self.stream_items_mp3 = {}

    @daemon_threaded
    def start_retrieving(self):
        target = YouTube(self.url)
        streams = target.streams
        for stream in streams:
            if stream.video_codec is None:
                audio_stream = [
                    f"Codec: {stream.audio_codec}, ",
                    f"ABR: {stream.abr}, ",
                    f"File Type: {stream.mime_type.split('/')[1]}, ",
                    f"File Size: {stream.filesize // 1024} KB",
                ]
                self.stream_items_mp3[stream.itag] = "".join(audio_stream)

            if stream.video_codec is not None and stream.audio_codec is not None:
                progressive_stream = [
                    "🔊 ",
                    f"Res: {stream.resolution}, ",
                    f"FPS: {stream.fps}, ",
                    f"Video Codec: {stream.video_codec}, ",
                    f"Audio Codec: {stream.audio_codec}, ",
                    f"File Type: {stream.mime_type.split('/')[1]}, ",
                    f"File Size: {stream.filesize // 1024} KB, ",
                    f"Video Type: {stream.type}, ",
                    "Stream Type: Progressive",
                ]
                self.stream_items_mp4[stream.itag] = "".join(progressive_stream)
            elif stream.video_codec is not None and stream.audio_codec is None:
                dash_stream = [
                    "🔇 ",
                    f"Res: {stream.resolution}, ",
                    f"FPS: {stream.fps}, ",
                    f"Video Codec: {stream.video_codec}, ",
                    f"Audio Codec: {stream.audio_codec}, ",
                    f"File Type: {stream.mime_type.split('/')[1]}, ",
                    f"File Size: {stream.filesize // 1024} KB, ",
                    f"Video Type: {stream.type}, ",
                    "Stream Type: Adaptive",
                ]
                self.stream_items_mp4[stream.itag] = "".join(dash_stream)

    def get_streams(self):
        if self.type == "mp4":
            return list(self.stream_items_mp4.values())
        else:
            return list(self.stream_items_mp3.values())
