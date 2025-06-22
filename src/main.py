import argparse
from yt_loader import load_youtube_video
from util import get_video_id, invoke_ai
from yt_sub_to_transcript import extract_transcript
from summary_generator import generate_summary, GENERATE_DESCRIPTIVE_NAME_SYSTEM_PROMPT, GENERATE_AGGREGATE_NAME_SYSTEM_PROMPT


def main():
    parser = argparse.ArgumentParser(description="Summarize YouTube videos")
    parser.add_argument(
        "--video",
        "-v",
        required=True,
        nargs='+',
        help='YouTube video URL(s) (up to 5 URLs, e.g. "https://www.youtube.com/watch?v=xxxx")',
    )
    parser.add_argument(
        "--prompt",
        "-p",
        help="Custom prompt instruction to guide the analysis and summary generation",
    )

    args = parser.parse_args()
    video_urls = args.video
    custom_prompt = args.prompt
    
    # Validate number of URLs
    if len(video_urls) > 5:
        print("❌ Error: Maximum of 5 URLs allowed")
        return
    
    print(f"🎬 Processing {len(video_urls)} video(s)...")

    # First, load all videos to get their titles and descriptions for aggregate name generation
    videos_metadata = []
    for video_url in video_urls:
        video = load_youtube_video(video_url=video_url)
        videos_metadata.append({
            'url': video_url,
            'video': video,
            'video_id': get_video_id(video_url)
        })
    
    # Generate aggregate descriptive name based on all videos
    if len(video_urls) == 1:
        # Single video - use the original logic
        video_prompt_content = f"<video_title>\n{videos_metadata[0]['video'].title}\n</video_title>\n"
        video_prompt_content += f"<description>\n{videos_metadata[0]['video'].description}\n</description>\n"
        descriptive_name_result = invoke_ai(
            system_prompt=GENERATE_DESCRIPTIVE_NAME_SYSTEM_PROMPT,
            user_prompt=video_prompt_content,
        )
    else:
        # Multiple videos - use aggregate naming
        videos_prompt_content = "Multiple videos to analyze:\n\n"
        for i, metadata in enumerate(videos_metadata, 1):
            videos_prompt_content += f"Video {i}:\n"
            videos_prompt_content += f"<video_title>\n{metadata['video'].title}\n</video_title>\n"
            videos_prompt_content += f"<description>\n{metadata['video'].description}\n</description>\n\n"
        
        descriptive_name_result = invoke_ai(
            system_prompt=GENERATE_AGGREGATE_NAME_SYSTEM_PROMPT,
            user_prompt=videos_prompt_content,
        )
    
    descriptive_name = descriptive_name_result.content.strip()
    print(f"📁 Generated aggregate name: {descriptive_name}")
    
    # Now process each video with the shared descriptive name
    for metadata in videos_metadata:
        print(f"\n🎯 Processing: {metadata['video'].title}")
        
        # Load video again with descriptive name for proper file placement
        video = load_youtube_video(video_url=metadata['url'], descriptive_name=descriptive_name)
        transcript = extract_transcript(video_id=metadata['video_id'], descriptive_name=descriptive_name)
        generate_summary(video=video, transcript=transcript, custom_prompt=custom_prompt, descriptive_name=descriptive_name)


if __name__ == "__main__":
    main()
