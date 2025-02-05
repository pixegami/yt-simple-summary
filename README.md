# Simple YouTube Video Summarizer

A Python tool that uses AI to generate concise summaries of YouTube videos, including key takeaways and Markdown exports.

## Overview

This tool automates the process of creating summaries from YouTube videos by:

1. Downloading video metadata and subtitles
2. Converting subtitles to a readable transcript
3. Using AI to generate summaries and key takeaways
4. Exporting results in Markdown format

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

3. Run the summarizer:

```bash
python src/main.py --video "https://www.youtube.com/watch?v=VIDEO_ID"
```

## YouTube Loading

The tool uses `yt-dlp` to handle YouTube video processing. It downloads video metadata and subtitles (both manual and auto-generated) in VTT format. The relevant code can be found in `src/yt_loader.py`.

## Converting Transcript

Subtitles are processed from VTT format into a clean, readable transcript. The system:

- Handles multiple subtitle file formats
- Removes duplicate lines
- Prioritizes specific English language variants (US, GB)

See the implementation in `src/yt_sub_to_transcript.py`

## OpenAI Setup

The tool uses OpenAI's API to generate summaries. Configuration includes:

- Model selection (currently using `o3-mini`)
- Cost tracking for API usage
- Structured prompt templates for consistent output

Configuration can be found in `src/util.py`

## Generate Summary

The summary generation process creates:

- A concise 1-2 paragraph summary
- 3-5 key takeaways

The summary generation logic is implemented in `src/summary_generator.py`

## Export Results

Results are exported in as a Markdown file. You can preview it in VSCode, or use an extension to export it to PDF.

Output files are organized in the `tmp/` directory with the following structure:

```text
tmp/
  └── VIDEO_ID/
      ├── metadata_VIDEO_ID.json
      ├── transcript_VIDEO_ID.txt
      └── summary_VIDEO_ID.md
```

## Examples

| Video Title                                                   | Link                         | Summary                                               |
| ------------------------------------------------------------- | ---------------------------- | ----------------------------------------------------- |
| Steve Jobs introduces iPhone in 2007                          | https://youtu.be/MnrJzXM7a6o | 🔗 [Example Summary](examples/summary_MnrJzXM7a6o.md) |
| The Ultimate (Beginner) Programming Language Tier List (2024) | https://youtu.be/HHyOWJh1aQU | 🔗 [Example Summary](examples/summary_HHyOWJh1aQU.md) |
| Top 5 Productivity Tips for Work!                             | https://youtu.be/1LOlJay5Sbw | 🔗 [Example Summary](examples/summary_1LOlJay5Sbw.md) |
| Supabase Full Project ⚡️ The FASTEST Way to Ship a SaaS App? | https://youtu.be/Q4rXmxQ1AUM | 🔗 [Example Summary](examples/summary_Q4rXmxQ1AUM.md) |
