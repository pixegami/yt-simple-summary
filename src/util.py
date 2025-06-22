from dataclasses import dataclass
import os
from typing import List
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import google.generativeai as genai


# https://ai.google.dev/gemini-api/docs/pricing
MODEL = "gemini-2.5-flash-preview-05-20"
MODEL_INPUT_COST_PER_1M_TOKENS = 0.15  # Cost in USD
MODEL_OUTPUT_COST_PER_1M_TOKENS = 3.50  # Cost in USD


@dataclass
class InvokeAIResult:
    content: str
    input_tokens: int
    output_tokens: int


def invoke_ai(system_prompt: str, user_prompt: str) -> InvokeAIResult:
    """
    Invoke the AI model.
    """
    model = genai.GenerativeModel(MODEL)

    # Combine system and user prompts
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    # Generate content
    response = model.generate_content(full_prompt)

    # Get token counts from the response
    input_tokens = response.usage_metadata.prompt_token_count
    output_tokens = response.usage_metadata.candidates_token_count

    print(f"✨ AI Response: {response.text}")

    return InvokeAIResult(
        content=extract_xml_tag(content=response.text),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def calculate_cost_usd(*invoke_results: List[InvokeAIResult]) -> float:
    """
    Calculate the cost in USD for a list of InvokeAIResult objects.
    """
    total_input_tokens = sum([result.input_tokens for result in invoke_results])
    total_output_tokens = sum([result.output_tokens for result in invoke_results])
    input_cost = total_input_tokens / 1_000_000 * MODEL_INPUT_COST_PER_1M_TOKENS
    output_cost = total_output_tokens / 1_000_000 * MODEL_OUTPUT_COST_PER_1M_TOKENS
    total_cost = input_cost + output_cost
    return total_cost


def extract_xml_tag(tag: str = "output", content: str = ""):
    """
    Extract the trimmed output from the xml tag.
    If tag isn't found then return the whole thing.
    """
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start_index = content.find(start_tag)
    end_index = content.find(end_tag)
    if start_index == -1 or end_index == -1:
        return content
    return content[start_index + len(start_tag) : end_index]


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


def get_output_path(video_id: str, descriptive_name: str = None) -> str:
    # Get the output path with date prefix and descriptive name, and ensure it exists.
    date_prefix = datetime.now().strftime("%y%m%d")
    folder_name = f"{date_prefix}-{descriptive_name or 'yt-summary'}"
    output_path = f"tmp/{folder_name}"
    os.makedirs(output_path, exist_ok=True)
    return output_path


def get_metadata_path(video_id: str, descriptive_name: str = None) -> str:
    return f"{get_output_path(video_id, descriptive_name)}/{descriptive_name or 'metadata'}_{video_id}.json"


def get_transcript_path(video_id: str, descriptive_name: str = None) -> str:
    return f"{get_output_path(video_id, descriptive_name)}/{descriptive_name or 'transcript'}_{video_id}.txt"


def get_markdown_path(video_id: str, descriptive_name: str = None) -> str:
    return f"{get_output_path(video_id, descriptive_name)}/{descriptive_name or 'summary'}_{video_id}.md"


def get_pdf_path(video_id: str, descriptive_name: str = None) -> str:
    return f"{get_output_path(video_id, descriptive_name)}/{descriptive_name or 'summary'}_{video_id}.pdf"


def get_yt_dlp_path_template(descriptive_name: str = None) -> str:
    # Based on https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#output-template
    date_prefix = datetime.now().strftime("%y%m%d")
    folder_name = f"{date_prefix}-{descriptive_name or 'yt-summary'}"
    return f"tmp/{folder_name}/video_%(id)s.%(ext)s"
