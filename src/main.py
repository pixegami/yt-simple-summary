import argparse
from yt_loader import load_youtube_video
from util import get_video_id
from yt_sub_to_transcript import extract_transcript


def main():
    parser = argparse.ArgumentParser(description="Summarize YouTube videos")
    parser.add_argument(
        "--video",
        "-v",
        required=True,
        help='YouTube video URL (e.g. "https://www.youtube.com/watch?v=xxxx")',
    )

    args = parser.parse_args()
    video_url = args.video
    video_id = get_video_id(video_url)

    load_youtube_video(video_url=video_url)
    extract_transcript(video_id=video_id)


if __name__ == "__main__":
    main()
