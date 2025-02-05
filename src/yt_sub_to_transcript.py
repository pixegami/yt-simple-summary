import glob
import webvtt

from util import get_transcript_path


def extract_transcript(video_id: str) -> str:
    vtt_path = get_vtt_file_name(video_id)
    transcript_str = get_transcript_from_vtt(vtt_path)

    # Save the transcript to a file.
    transcript_path = get_transcript_path(video_id)
    with open(transcript_path, "w") as f:
        f.write(transcript_str)

    print(f"✅ Transcript saved to {transcript_path}")
    return transcript_str


def get_vtt_file_name(video_id: str) -> str:
    """
    Get the path to the vtt (subtitle) file for the given video id.
    """
    srt_files = glob.glob(f"tmp/{video_id}/*.vtt")
    if len(srt_files) == 0:
        raise ValueError(f"No subtitle files (.vtt) found for {video_id}")

    # If there's multiple files, prefer the ones with the preferred languages.
    PREFERRED_LANG = ["en-US", "en-GB", "en"]
    for lang in PREFERRED_LANG:
        for file in srt_files:
            if lang in file:
                return file

    # If no preferred language is found, return the first one.
    return srt_files[0]


def get_transcript_from_vtt(vtt_path: str) -> str:
    vtt = webvtt.read(vtt_path)
    transcript_arr = []

    lines = []
    for line in vtt:
        lines.extend(line.text.strip().splitlines())

    # For some reason, VTT files have repeated lines. Remove them.
    previous = None
    for line in lines:
        if line == previous:
            continue
        transcript_arr.append(line)
        previous = line

    transcript_str = "\n".join(transcript_arr)
    return transcript_str
