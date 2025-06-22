import argparse
from yt_loader import load_youtube_video
from util import get_video_id, invoke_ai
from yt_sub_to_transcript import extract_transcript
from summary_generator import generate_summary, GENERATE_DESCRIPTIVE_NAME_SYSTEM_PROMPT


def main():
    parser = argparse.ArgumentParser(description="Summarize YouTube videos")
    parser.add_argument(
        "--video",
        "-v",
        required=True,
        help='YouTube video URL (e.g. "https://www.youtube.com/watch?v=xxxx")',
    )
    parser.add_argument(
        "--prompt",
        "-p",
        help="Custom prompt instruction to guide the analysis and summary generation",
    )

    args = parser.parse_args()
    video_url = args.video
    custom_prompt = args.prompt
    video_id = get_video_id(video_url)

    # First load video to get title and description for name generation
    video = load_youtube_video(video_url=video_url)
    
    # Generate descriptive name for folder/file naming
    video_prompt_content = f"<video_title>\n{video.title}\n</video_title>\n"
    video_prompt_content += f"<description>\n{video.description}\n</description>\n"
    descriptive_name_result = invoke_ai(
        system_prompt=GENERATE_DESCRIPTIVE_NAME_SYSTEM_PROMPT,
        user_prompt=video_prompt_content,
    )
    descriptive_name = descriptive_name_result.content.strip()
    print(f"📁 Generated name: {descriptive_name}")
    
    # Now load video again with the descriptive name to save files properly
    video = load_youtube_video(video_url=video_url, descriptive_name=descriptive_name)
    transcript = extract_transcript(video_id=video_id, descriptive_name=descriptive_name)
    generate_summary(video=video, transcript=transcript, custom_prompt=custom_prompt, descriptive_name=descriptive_name)


if __name__ == "__main__":
    main()
