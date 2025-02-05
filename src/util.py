import os
from urllib.parse import urlparse, parse_qs


def get_video_id(url):
    """
    Get the YouTube video ID from a URL.
    """
    try:
        # Parse the URL
        parsed_url = urlparse(url)

        # Handle standard watch URLs (youtube.com/watch?v=VIDEO_ID)
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]

        # Handle short URLs (youtu.be/VIDEO_ID)
        if parsed_url.netloc == "youtu.be":
            return parsed_url.path[1:]

        # Handle embedded URLs (youtube.com/embed/VIDEO_ID)
        if parsed_url.path.startswith("/embed/"):
            return parsed_url.path.split("/")[2]

        # Handle short form URLs (youtube.com/shorts/VIDEO_ID)
        if parsed_url.path.startswith("/shorts/"):
            return parsed_url.path.split("/")[2]

        return url
    except Exception:
        return url


def get_output_path(video_id: str) -> str:
    # Get the output path, and ensure it exists.
    output_path = f"tmp/{video_id}"
    os.makedirs(output_path, exist_ok=True)
    return output_path


def get_metadata_path(video_id: str) -> str:
    return f"{get_output_path(video_id)}/metadata_{video_id}.json"


def get_transcript_path(video_id: str) -> str:
    return f"{get_output_path(video_id)}/transcript_{video_id}.txt"


def get_markdown_path(video_id: str) -> str:
    return f"{get_output_path(video_id)}/summary_{video_id}.md"


def get_pdf_path(video_id: str) -> str:
    return f"{get_output_path(video_id)}/summary_{video_id}.pdf"


def get_yt_dlp_path_template() -> str:
    # Based on https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#output-template
    return f"tmp/%(id)s/video_%(id)s.%(ext)s"
