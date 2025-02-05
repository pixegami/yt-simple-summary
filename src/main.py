import argparse
from yt_loader import load_youtube_video


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

    load_youtube_video(video_url=video_url)


if __name__ == "__main__":
    main()
