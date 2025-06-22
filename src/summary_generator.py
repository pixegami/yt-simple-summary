import os
from typing import Dict
from markdown_pdf import MarkdownPdf, Section
from util import (
    calculate_cost_usd,
    get_markdown_path,
    get_pdf_path,
    invoke_ai,
)
from yt_loader import YouTubeVideo


GENERATE_SUMMARY_SYSTEM_PROMPT = """
Generate a short one paragraph summary of the video. This meant to be a concise executive summary, highlighting the important points and outcomes. If the video is asking a question, or using a clickbait title, then ensure that all the results/answers are revealed in the summary. Get straight to the point with the summary — don't say things like 'in this video [...]', just go directly to the outcome.

If a custom instruction is provided, follow that guidance while generating the summary.
"""

GENERATE_TAKEAWAYS_SYSTEM_PROMPT = """
Distill the key content into a list (for top-N, takeaways, insights).
First, decide what is the key content (appropriate to the video). What is the thing the viewer most likely wants to know?

Then generate this distilled content in markdown format — using a list (*), use an emoji for each takeaway, and use a bold title for each takeaway (e.g. * **💡 Title**: Content). 

If a custom instruction is provided, follow that guidance while generating the takeaways.
"""

GENERATE_GENERATE_TABLE_SYSTEM_PROMPT = """
Think if there's a way to express extract the information from the video in the form of a table. What is the data the user wants to consume at a glance? First, think about what type of table would be most useful (e.g. comparison table, tier-list, etc). Then, think about what data/columns should be in the table (only use content from the video). Generate the table in markdown format. Generate the table only.

If a custom instruction is provided, follow that guidance while generating the table.
"""

EXTRACT_CORE_DATA_SYSTEM_PROMPT = """
Extract 3-5 core data points (about a paragraph each) from the video. This could be a combination of quotes, excerpts, or a summary of ideas. Use a H4 header to mark the start of each data point. This is the most valuable, specific content from the video that we want to take away.

If a custom instruction is provided, follow that guidance while extracting the core data.
"""

GENERIC_OUTPUT_FORMAT = """\n\n
Show your thinking process in <thinking>...</thinking> tags.
Then return a concise response in <output>...</output> tags.\n
"""


def generate_summary(video: YouTubeVideo, transcript: str, custom_prompt: str = None) -> str:

    print(f"✨ Generating Summary For: {video.title}")
    video_id = video.display_id

    video_prompt_content = f"<video_title>\n{video.title}\n</video_title>\n"
    video_prompt_content += f"<description>\n{video.description}\n</description>\n"
    video_prompt_content += f"<transcript>\n{transcript}\n</transcript>\n"
    
    if custom_prompt:
        video_prompt_content += f"<custom_instruction>\n{custom_prompt}\n</custom_instruction>\n"

    summary_result = invoke_ai(
        system_prompt=GENERATE_SUMMARY_SYSTEM_PROMPT + GENERIC_OUTPUT_FORMAT,
        user_prompt=video_prompt_content,
    )

    takeaways_result = invoke_ai(
        system_prompt=GENERATE_TAKEAWAYS_SYSTEM_PROMPT + GENERIC_OUTPUT_FORMAT,
        user_prompt=video_prompt_content,
    )

    core_data_result = invoke_ai(
        system_prompt=EXTRACT_CORE_DATA_SYSTEM_PROMPT + GENERIC_OUTPUT_FORMAT,
        user_prompt=video_prompt_content,
    )

    table_result = invoke_ai(
        system_prompt=GENERATE_GENERATE_TABLE_SYSTEM_PROMPT + GENERIC_OUTPUT_FORMAT,
        user_prompt=video_prompt_content,
    )

    markdown_sections = {
        "Summary": summary_result.content,
        "Takeaways": takeaways_result.content,
        "Core Data": core_data_result.content,
        "Extracted Data": table_result.content,
    }

    # Save the markdown to a file.
    markdown_path = get_markdown_path(video_id)
    markdown_text = generate_markdown(
        title=video.title,
        video_id=video.display_id,
        sections=markdown_sections,
        path=markdown_path,
    )
    print(f"✅ Markdown Summary: {markdown_path}")

    # Also save it as a PDF.
    pdf_path = get_pdf_path(video_id)
    generate_pdf(title=video.title, markdown_text=markdown_text, path=pdf_path)
    print(f"✅ PDF Summary: {pdf_path}")

    # Calculate the cost.
    total_cost = calculate_cost_usd(summary_result, takeaways_result, table_result)
    print(f"💵 Total cost: ${total_cost}")


def generate_markdown(
    title: str, video_id: str, sections: Dict[str, str], path: str
) -> str:
    markdown_output_arr = [f"# {title}", f"🔗 Video: https://youtu.be/{video_id}"]
    for section_name, section_content in sections.items():
        markdown_output_arr.append(f"## {section_name}\n{section_content}")

    markdown_text = "\n\n".join(markdown_output_arr)
    with open(path, "w") as markdown_file:
        markdown_file.write(markdown_text)

    return markdown_text


def generate_pdf(title: str, markdown_text: str, path: str) -> None:

    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path, "r") as css_file:
        css_text = css_file.read()

    pdf = MarkdownPdf()
    pdf.meta["title"] = title
    pdf.add_section(Section(markdown_text, toc=False), user_css=css_text)
    pdf.save(path)
