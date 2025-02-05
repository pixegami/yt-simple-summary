import argparse
from yt_loader import load_youtube_video
from util import get_video_id
from yt_sub_to_transcript import extract_transcript
from summary_generator import generate_summary


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

    video = load_youtube_video(video_url=video_url)
    transcript = extract_transcript(video_id=video_id)
    generate_summary(video=video, transcript=transcript)


if __name__ == "__main__":
    main()
