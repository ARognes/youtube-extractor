#!/usr/bin/env python3
"""
save_defranco_transcript.py

Takes a video metadata JSON and a raw transcript JSON payload, and produces:
1. downloaded_transcripts/step_manual_<video_id>.json
2. formatted_transcripts/step_manual_<video_id>.yaml
"""

import os
import sys
import json
import yaml
import re

class FlowList(list):
    pass

class CleanYamlDumper(yaml.CSafeDumper if hasattr(yaml, 'CSafeDumper') else yaml.SafeDumper):
    pass

def flow_list_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(FlowList, flow_list_representer, Dumper=CleanYamlDumper)
yaml.add_representer(str, str_representer, Dumper=CleanYamlDumper)

def format_duration(seconds):
    seconds = int(round(seconds))
    hh = seconds // 3600
    mm = (seconds % 3600) // 60
    ss = seconds % 60
    if hh > 0:
        return f"{hh:02d}:{mm:02d}:{ss:02d}"
    return f"{mm:02d}:{ss:02d}"

def process_file(meta_path, transcript_path):
    with open(meta_path, 'r', encoding='utf-8') as f:
        video_meta = json.load(f)
    with open(transcript_path, 'r', encoding='utf-8') as f:
        raw_transcript_payload = json.load(f)

    video_id = video_meta["videoId"]
    title = video_meta.get("title", "")
    channel = video_meta.get("author", "Philip DeFranco")
    published = video_meta.get("published", "")
    url = video_meta.get("link", f"https://www.youtube.com/watch?v={video_id}")
    thumbnail = video_meta.get("thumbnail", {}).get("url", f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")
    description = video_meta.get("description", "")

    segments = []
    # Can be {"content": {"transcript": [...]}} or {"content": [...]} or {"transcript": [...]}
    if isinstance(raw_transcript_payload, dict):
        c = raw_transcript_payload.get("content")
        if isinstance(c, dict) and "transcript" in c and isinstance(c["transcript"], list):
            segments = c["transcript"]
        elif isinstance(c, list):
            segments = c
        elif "transcript" in raw_transcript_payload and isinstance(raw_transcript_payload["transcript"], list):
            segments = raw_transcript_payload["transcript"]
        elif isinstance(c, str):
            try:
                parsed_c = json.loads(c)
                if isinstance(parsed_c, dict) and "transcript" in parsed_c:
                    segments = parsed_c["transcript"]
                elif isinstance(parsed_c, list):
                    segments = parsed_c
            except Exception:
                pass
    elif isinstance(raw_transcript_payload, list):
        segments = raw_transcript_payload

    chunks = []
    pairs = []
    curr_char = 0
    max_sec = 0

    for seg in segments:
        text = seg.get("text", "").replace('\n', ' ').strip()
        if not text:
            continue
        start_sec = int(round(float(seg.get("start", 0))))
        if start_sec > max_sec:
            max_sec = start_sec

        if chunks:
            curr_char += 1  # space delimiter
        pairs.append([curr_char, start_sec])
        chunks.append(text)
        curr_char += len(text)

    full_transcript = " ".join(chunks)
    duration_str = format_duration(max_sec)

    chapter_list = []
    for line in description.split("\n"):
        m = re.match(r'^(?:TODAY’S STORIES|\s*)*(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–]\s*(.+)$', line.strip())
        if m:
            chapter_list.append({
                "timestamp": m.group(1),
                "title": m.group(2).strip()
            })

    tags = re.findall(r'#(\w+)', description)

    json_path = f"downloaded_transcripts/step_manual_{video_id}.json"
    raw_json_data = {
        "video_id": video_id,
        "title": title,
        "channel": channel,
        "handle": "@PhilipDeFranco",
        "url": url,
        "thumbnail": thumbnail,
        "duration": duration_str,
        "word_count": len(full_transcript.split()),
        "published": published,
        "raw_segments": segments,
        "video_summary": {
            "executive_synopsis": f"Philip DeFranco daily news coverage discussing {title}.",
            "core_takeaways": [c["title"] for c in chapter_list[:4]] if chapter_list else [title],
            "key_concepts": tags,
            "chapters": chapter_list
        }
    }
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(raw_json_data, jf, indent=2, ensure_ascii=False)

    yaml_path = f"formatted_transcripts/step_manual_{video_id}.yaml"
    clean_yaml_data = {
        "video_id": video_id,
        "title": title,
        "channel": channel,
        "handle": "@PhilipDeFranco",
        "url": url,
        "duration": duration_str,
        "published": published,
        "type": "video",
        "transcript": full_transcript,
        "timestamps": FlowList(pairs)
    }
    with open(yaml_path, "w", encoding="utf-8") as yf:
        yaml.dump(clean_yaml_data, yf, Dumper=CleanYamlDumper, sort_keys=False, allow_unicode=True, width=120)

    print(f"Successfully processed {video_id}: {len(chunks)} segments, {len(full_transcript.split())} words.")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 save_defranco_transcript.py <meta_json> <transcript_json>")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])
