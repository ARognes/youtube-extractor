#!/usr/bin/env python3
"""
reformat_transcripts_to_yaml.py

Converts raw YouTube transcript JSON files from `downloaded_transcripts/` into a unified,
clean YAML format in `formatted_transcripts/`.

Schema:
  video_id: str
  title: str
  channel: str
  handle: str (optional)
  url: str
  duration: str ("MM:SS" or "HH:MM:SS")
  published: str (optional)
  type: "short" | "video"
  transcript: str
  timestamps: [[char_offset, seconds], ...]
"""

import os
import sys
import json
import re
import time
import argparse
import yaml

# Custom PyYAML Dumper to format FlowList as flow sequence and multiline strings cleanly
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


def parse_srt(srt_text):
    """
    Parses SRT subtitle text into list of (seconds, text_chunk).
    """
    blocks = srt_text.strip().split('\n\n')
    entries = []
    for b in blocks:
        lines = [l.strip() for l in b.strip().split('\n') if l.strip()]
        if len(lines) >= 2:
            time_line = lines[1] if '-->' in lines[1] else (lines[0] if '-->' in lines[0] else '')
            if not time_line:
                continue
            text_lines = lines[2:] if lines[1] == time_line else lines[1:]
            text = ' '.join(text_lines).strip()
            if not text:
                continue
            m = re.search(r'(?:(\d+):)?(\d+):(\d+)[,\.](\d+)', time_line)
            if m:
                hh = int(m.group(1)) if m.group(1) else 0
                mm = int(m.group(2))
                ss = int(m.group(3))
                total_seconds = hh * 3600 + mm * 60 + ss
                entries.append((total_seconds, text))
    return entries


def format_duration(seconds):
    """Formats integer seconds into MM:SS or HH:MM:SS."""
    seconds = int(round(seconds))
    hh = seconds // 3600
    mm = (seconds % 3600) // 60
    ss = seconds % 60
    if hh > 0:
        return f"{hh:02d}:{mm:02d}:{ss:02d}"
    return f"{mm:02d}:{ss:02d}"


def parse_duration_to_seconds(dur_val, dur_sec_val):
    """Extracts duration in integer seconds from multiple raw formats."""
    if dur_sec_val is not None and isinstance(dur_sec_val, (int, float)):
        return int(dur_sec_val)
    if isinstance(dur_val, (int, float)):
        return int(dur_val * 60)
    if isinstance(dur_val, str):
        parts = [int(p) for p in dur_val.split(':') if p.isdigit()]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 1:
            return parts[0]
    return 0


def classify_content_type(url, title, duration_seconds):
    """
    Identifies whether a video is a YouTube Short or a standard Video.
    """
    if '/shorts/' in url:
        return "short"
    if re.search(r'#shorts?\b', title, re.IGNORECASE):
        return "short"
    if 0 < duration_seconds <= 60:
        return "short"
    return "video"


def extract_transcript_and_timestamps(data):
    """
    Reconstructs clean plain spoken text and pointer pairs: [[char_offset, seconds], ...].
    """
    raw = data.get('raw_segments')

    # 1. SRT format in raw_segments (e.g. Apify / YouTube SRT downloads)
    if raw and isinstance(raw, list) and len(raw) > 0 and isinstance(raw[0], dict) and raw[0].get('srt'):
        entries = parse_srt(raw[0]['srt'])
        if entries:
            chunks = []
            pairs = []
            curr_char = 0
            for sec, txt in entries:
                if chunks:
                    curr_char += 1  # delimiter space
                pairs.append([curr_char, sec])
                chunks.append(txt)
                curr_char += len(txt)
            return ' '.join(chunks), FlowList(pairs)

    # 2. Segment dictionary list with offset (ms) or start (sec)
    if raw and isinstance(raw, list) and len(raw) > 0 and isinstance(raw[0], dict):
        chunks = []
        pairs = []
        curr_char = 0
        for s in raw:
            txt = s.get('text', '').strip()
            if not txt:
                continue
            if 'offset' in s and s['offset'] is not None:
                sec = int(round(s['offset'] / 1000.0))
            elif 'start' in s and s['start'] is not None:
                sec = int(round(float(s['start'])))
            else:
                sec = 0
            if chunks:
                curr_char += 1
            pairs.append([curr_char, sec])
            chunks.append(txt)
            curr_char += len(txt)
        if chunks:
            return ' '.join(chunks), FlowList(pairs)

    # 3. Fallback to data['transcript']
    transcript = data.get('transcript') or ''
    # Filter out 408 error text
    if 'Error 408' in transcript or 'Request failed' in transcript:
        return "", FlowList([])

    # Check for embedded timestamps in description/transcript (e.g. 00:01:34 - Title)
    timestamp_matches = list(re.finditer(r'(?:^|\n|\s)(\d{1,2}:\d{2}(?::\d{2})?)(?:\s*-\s*|\s+)', transcript))
    if timestamp_matches:
        pairs = []
        for m in timestamp_matches:
            ts_str = m.group(1)
            parts = [int(p) for p in ts_str.split(':')]
            sec = parts[0] * 3600 + parts[1] * 60 + parts[2] if len(parts) == 3 else parts[0] * 60 + parts[1]
            char_pos = m.start(1)
            pairs.append([char_pos, sec])
        return transcript.strip(), FlowList(pairs)

    return transcript.strip(), FlowList([])


def reformat_file(json_path, output_dir):
    """Processes a single JSON transcript and writes the unified YAML document."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    video_id = str(data.get('video_id') or '').strip()
    title = str(data.get('title') or data.get('video_title') or '').strip()
    channel = str(data.get('channel') or data.get('channel_name') or '').strip()
    handle = data.get('handle') or data.get('channel_handle')
    if handle:
        handle = str(handle).strip()

    url = data.get('url') or data.get('video_url')
    if not url and video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"

    dur_sec = parse_duration_to_seconds(data.get('duration'), data.get('duration_seconds'))
    duration_str = format_duration(dur_sec) if dur_sec > 0 else (str(data.get('duration')) if data.get('duration') else "00:00")
    content_type = classify_content_type(url or '', title, dur_sec)

    transcript, timestamps = extract_transcript_and_timestamps(data)

    doc = {
        'video_id': video_id,
        'title': title,
        'channel': channel,
    }
    if handle:
        doc['handle'] = handle
    doc['url'] = url
    doc['duration'] = duration_str

    published = data.get('published') or data.get('hydrated_at')
    if published:
        doc['published'] = str(published).strip()

    doc['type'] = content_type
    doc['transcript'] = transcript
    doc['timestamps'] = timestamps

    base_name = os.path.splitext(os.path.basename(json_path))[0]
    out_path = os.path.join(output_dir, f"{base_name}.yaml")

    yaml_str = yaml.dump(
        doc,
        Dumper=CleanYamlDumper,
        sort_keys=False,
        allow_unicode=True,
        width=10000000  # Avoid splitting individual flow items across lines
    )

    with open(out_path, 'w', encoding='utf-8') as out_f:
        out_f.write(yaml_str)

    return content_type, len(timestamps)


def main():
    parser = argparse.ArgumentParser(description="Reformat JSON transcripts to clean YAML.")
    parser.add_argument(
        "--input-dir",
        default="/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts",
        help="Path to source JSON transcripts"
    )
    parser.add_argument(
        "--output-dir",
        default="/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/formatted_transcripts",
        help="Path to output YAML transcripts"
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    files = sorted([f for f in os.listdir(args.input_dir) if f.endswith('.json')])
    total_files = len(files)
    print(f"🚀 Starting reformatting of {total_files} transcripts...")
    print(f"   Source: {args.input_dir}")
    print(f"   Destination: {args.output_dir}")

    t0 = time.time()
    shorts_count = 0
    videos_count = 0
    with_timestamps_count = 0
    errors = 0

    for idx, f in enumerate(files, 1):
        json_path = os.path.join(args.input_dir, f)
        try:
            c_type, num_ts = reformat_file(json_path, args.output_dir)
            if c_type == 'short':
                shorts_count += 1
            else:
                videos_count += 1
            if num_ts > 0:
                with_timestamps_count += 1
        except Exception as e:
            errors += 1
            print(f"⚠️ Error reformatting {f}: {e}")

        if idx % 200 == 0 or idx == total_files:
            print(f"   Processed {idx}/{total_files} files ({(idx/total_files)*100:.1f}%)...")

    elapsed = time.time() - t0
    print(f"\n✅ Reformatting Complete in {elapsed:.2f}s!")
    print(f"   - Total YAML Files Written: {total_files - errors}")
    print(f"   - Standard Videos: {videos_count}")
    print(f"   - YouTube Shorts: {shorts_count}")
    print(f"   - Transcripts with Timestamp Pointers: {with_timestamps_count}")
    print(f"   - Failed / Errors: {errors}")


if __name__ == '__main__':
    main()
