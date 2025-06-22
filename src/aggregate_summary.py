import os
import glob
from typing import Dict, List
from markdown_pdf import MarkdownPdf, Section
from util import invoke_ai, get_output_path, calculate_cost_usd


GENERATE_AGGREGATE_SUMMARY_SYSTEM_PROMPT = """
You are analyzing multiple video summaries to create a comprehensive aggregate summary. Your task is to identify common themes, patterns, and insights that appear across the videos while avoiding duplication.

Generate a general summary paragraph that captures the overarching themes and key insights that are common across all or most of the videos. Focus on the big picture and main concepts that tie the videos together.
"""

GENERATE_AGGREGATE_TAKEAWAYS_SYSTEM_PROMPT = """
Extract common takeaways, insights, and lessons that appear across multiple videos. Focus on:
- Patterns and themes that repeat across videos
- Core principles or concepts mentioned in multiple sources
- Key insights that are reinforced by multiple videos
- Best practices or recommendations that appear consistently

Generate this content in markdown format using a list (*), with an emoji for each takeaway, and a bold title for each takeaway (e.g. * **💡 Title**: Content).

Avoid duplicating points that are specific to only one video.
"""

GENERATE_AGGREGATE_TABLE_SYSTEM_PROMPT = """
Create a useful table that synthesizes information from across all the videos. Consider what type of comparison or overview would be most valuable:
- Comparison table showing how different videos approach the same topic
- Summary table of key concepts with examples from multiple videos
- Framework or methodology table that combines insights from all sources

Generate the table in markdown format. Only include information that draws from multiple videos or shows interesting contrasts/comparisons.
"""

GENERATE_UNIQUE_DIFFERENCES_SYSTEM_PROMPT = """
For each video, identify what is unique or different about that specific video that wasn't captured in the common themes above. Focus on:
- Unique perspectives, approaches, or methodologies
- Specific examples, case studies, or details not found elsewhere
- Different viewpoints or alternative approaches
- Specialized content that only appears in that video

For each video, provide 1-2 paragraphs or a short list highlighting what makes it distinctive. Use the format:

## Video: [Title]
[1-2 paragraphs or bullet points about unique aspects]
"""

GENERIC_OUTPUT_FORMAT = """\n\n
Show your thinking process in <thinking>...</thinking> tags.
Then return a concise response in <output>...</output> tags.\n
"""


def generate_aggregate_summary(descriptive_name: str, video_titles: List[str]) -> str:
    """
    Generate an aggregate summary from all markdown files in the folder.
    """
    print(f"🔄 Generating aggregate summary for {descriptive_name}...")
    
    # Read all markdown files from the folder
    markdown_contents = read_all_markdown_files(descriptive_name)
    
    if not markdown_contents:
        print("❌ No markdown files found to aggregate")
        return None
    
    # Prepare content for AI processing
    all_content = prepare_content_for_ai(markdown_contents, video_titles)
    
    # Generate each section of the aggregate summary
    summary_result = invoke_ai(
        system_prompt=GENERATE_AGGREGATE_SUMMARY_SYSTEM_PROMPT + GENERIC_OUTPUT_FORMAT,
        user_prompt=all_content,
    )
    
    takeaways_result = invoke_ai(
        system_prompt=GENERATE_AGGREGATE_TAKEAWAYS_SYSTEM_PROMPT + GENERIC_OUTPUT_FORMAT,
        user_prompt=all_content,
    )
    
    table_result = invoke_ai(
        system_prompt=GENERATE_AGGREGATE_TABLE_SYSTEM_PROMPT + GENERIC_OUTPUT_FORMAT,
        user_prompt=all_content,
    )
    
    differences_result = invoke_ai(
        system_prompt=GENERATE_UNIQUE_DIFFERENCES_SYSTEM_PROMPT + GENERIC_OUTPUT_FORMAT,
        user_prompt=all_content,
    )
    
    # Combine all sections
    aggregate_sections = {
        "Aggregate Summary": summary_result.content,
        "Common Takeaways": takeaways_result.content,
        "Comparative Analysis": table_result.content,
        "Unique Aspects by Video": differences_result.content,
    }
    
    # Save the aggregate markdown
    aggregate_path = get_aggregate_markdown_path(descriptive_name)
    markdown_text = generate_aggregate_markdown(
        title=f"Aggregate Summary: {descriptive_name.replace('-', ' ').title()}",
        sections=aggregate_sections,
        path=aggregate_path,
    )
    print(f"✅ Aggregate Markdown: {aggregate_path}")
    
    # Generate PDF
    pdf_path = get_aggregate_pdf_path(descriptive_name)
    generate_aggregate_pdf(
        title=f"Aggregate Summary: {descriptive_name.replace('-', ' ').title()}", 
        markdown_text=markdown_text, 
        path=pdf_path
    )
    print(f"✅ Aggregate PDF: {pdf_path}")
    
    # Calculate cost
    total_cost = calculate_cost_usd(summary_result, takeaways_result, table_result, differences_result)
    print(f"💵 Aggregate summary cost: ${total_cost}")
    
    return aggregate_path


def read_all_markdown_files(descriptive_name: str) -> Dict[str, str]:
    """
    Read all markdown files from the output folder.
    """
    output_path = get_output_path("", descriptive_name)
    markdown_files = glob.glob(f"{output_path}/*.md")
    
    # Filter out the aggregate summary file itself
    markdown_files = [f for f in markdown_files if not f.endswith("_aggregate.md")]
    
    contents = {}
    for file_path in markdown_files:
        filename = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            contents[filename] = f.read()
    
    return contents


def prepare_content_for_ai(markdown_contents: Dict[str, str], video_titles: List[str]) -> str:
    """
    Prepare the markdown contents for AI processing.
    """
    content = "Multiple video summaries to analyze:\n\n"
    
    for i, (filename, markdown_content) in enumerate(markdown_contents.items(), 1):
        content += f"=== VIDEO {i} SUMMARY ===\n"
        content += f"Filename: {filename}\n"
        content += f"Content:\n{markdown_content}\n\n"
    
    return content


def generate_aggregate_markdown(title: str, sections: Dict[str, str], path: str) -> str:
    """
    Generate the aggregate markdown file.
    """
    markdown_output_arr = [f"# {title}"]
    
    for section_name, section_content in sections.items():
        markdown_output_arr.append(f"## {section_name}\n{section_content}")
    
    markdown_text = "\n\n".join(markdown_output_arr)
    with open(path, "w", encoding="utf-8") as markdown_file:
        markdown_file.write(markdown_text)
    
    return markdown_text


def generate_aggregate_pdf(title: str, markdown_text: str, path: str) -> None:
    """
    Generate the aggregate PDF file.
    """
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path, "r") as css_file:
        css_text = css_file.read()
    
    pdf = MarkdownPdf()
    pdf.meta["title"] = title
    pdf.add_section(Section(markdown_text, toc=False), user_css=css_text)
    pdf.save(path)


def get_aggregate_markdown_path(descriptive_name: str) -> str:
    """
    Get the path for the aggregate markdown file.
    """
    output_path = get_output_path("", descriptive_name)
    return f"{output_path}/{descriptive_name}_aggregate.md"


def get_aggregate_pdf_path(descriptive_name: str) -> str:
    """
    Get the path for the aggregate PDF file.
    """
    output_path = get_output_path("", descriptive_name)
    return f"{output_path}/{descriptive_name}_aggregate.pdf"