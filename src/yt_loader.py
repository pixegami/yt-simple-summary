import json
from typing import Optional
from yt_dlp import YoutubeDL
from pydantic import BaseModel
from util import get_metadata_path, get_yt_dlp_path_template


class YouTubeVideo(BaseModel):
    title: Optional[str] = None
    display_id: Optional[str] = None
    description: Optional[str] = None


def load_youtube_video(video_url: str) -> YouTubeVideo:

    ydl_opts = {
        "skip_download": True,  # We don't need to download the video.
        "writesubtitles": True,  # Download the subtitles.
        "subtitleslangs": ["en.*"],  # Select English subtitles.
        "subtitlesformat": "vtt/best",  # Use .vtt format.
        "writeautomaticsub": True,  # Download automatic subtitles.
        "outtmpl": {
            "default": get_yt_dlp_path_template(),  # This is the template used for the output files.
        },
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)

        # Uncomment this if you want to see all the data:
        # print(json.dumps(ydl.sanitize_info(info)))

        # Extract the metadata we care about.
        video = YouTubeVideo(
            display_id=info.get("id"),
            title=info.get("title"),
            description=info.get("description"),
        )

        # Save the metadata to a file.
        with open(get_metadata_path(video.display_id), "w", encoding="utf-8") as f:
            json.dump(video.model_dump(), f, indent=2, ensure_ascii=False)

        return video
