import os


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
