#!/usr/bin/env python3
"""
search_transcripts.py

Instant Deep-Link Timestamp Searcher CLI across all 1,740 YAML transcripts.
Uses the `timestamps: [[char_offset, seconds], ...]` index to binary-search
the exact playback second for any keyword or phrase match and produces
direct YouTube jump links (`https://youtu.be/{id}?t={seconds}s`).

Usage:
  python3 search_transcripts.py "borrow checker"
  python3 search_transcripts.py "docker" --type short
  python3 search_transcripts.py "dopamine" --channel "HealthyGamerGG"
  python3 search_transcripts.py "pricing" --domain "business_systems"
"""

import os
import sys
import re
import bisect
import argparse
import yaml

try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader

FORMATTED_DIR = "formatted_transcripts"
TAXONOMY_FILE = "taxonomy/video_metadata_registry.yaml"

# ANSI color codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def format_seconds(seconds):
    hh = seconds // 3600
    mm = (seconds % 3600) // 60
    ss = seconds % 60
    if hh > 0:
        return f"{hh:02d}:{mm:02d}:{ss:02d}"
    return f"{mm:02d}:{ss:02d}"


def build_youtube_jump_url(base_url, seconds, video_id=""):
    if not base_url and video_id:
        base_url = f"https://www.youtube.com/watch?v={video_id}"
    if not base_url:
        return ""
    # Strip any existing timestamp param
    clean_url = re.sub(r'[?&]t=\d+s?', '', base_url)
    sep = "&" if "?" in clean_url else "?"
    return f"{clean_url}{sep}t={seconds}s"


def find_timestamp_for_char(timestamps, char_index, text=""):
    """
    Given a list of [char_pos, seconds], finds the cue matching char_index
    via binary search. If timestamps list is empty, falls back to scanning
    inline timestamp tags like [26.64s] or 01:23 in the preceding text.
    """
    if timestamps:
        keys = [item[0] for item in timestamps]
        idx = bisect.bisect_right(keys, char_index) - 1
        if idx >= 0:
            return timestamps[idx][1]
    
    # Fallback to inline timestamp markers if present in raw transcript
    if text:
        prefix = text[:char_index]
        inline_matches = list(re.finditer(r'\[(\d+(?:\.\d+)?)s?\]', prefix))
        if inline_matches:
            return int(round(float(inline_matches[-1].group(1))))
        ts_matches = list(re.finditer(r'\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b', prefix))
        if ts_matches:
            m = ts_matches[-1]
            if m.group(3):
                return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            return int(m.group(1)) * 60 + int(m.group(2))

    return 0


def extract_snippet(text, match_start, match_end, radius=90):
    start = max(0, match_start - radius)
    end = min(len(text), match_end + radius)
    
    prefix = ("..." if start > 0 else "") + text[start:match_start]
    match = text[match_start:match_end]
    suffix = text[match_end:end] + ("..." if end < len(text) else "")
    
    # Clean newlines for terminal display
    prefix = prefix.replace('\n', ' ')
    match = match.replace('\n', ' ')
    suffix = suffix.replace('\n', ' ')
    
    return f"{prefix}{BOLD}{YELLOW}{match}{RESET}{suffix}"


def main():
    parser = argparse.ArgumentParser(
        description="Search across 1,740 YouTube transcripts with instant deep-link timestamps."
    )
    parser.add_argument("query", help="Keyword or regex phrase to search for")
    parser.add_argument("--channel", help="Filter by channel name (case-insensitive substring)")
    parser.add_argument("--domain", help="Filter by domain (e.g. software_engineering, business_systems)")
    parser.add_argument("--type", choices=["short", "video"], help="Filter by content type")
    parser.add_argument("--limit", type=int, default=10, help="Maximum results to return (default: 10)")
    parser.add_argument("--exact", action="store_true", help="Match exact word boundaries")
    parser.add_argument("--regex", action="store_true", help="Treat query as regular expression")

    args = parser.parse_args()

    # Load video_metadata_registry if domain filter is specified
    domain_map = {}
    if args.domain:
        if os.path.exists(TAXONOMY_FILE):
            with open(TAXONOMY_FILE, 'r', encoding='utf-8') as tf:
                reg = yaml.load(tf, Loader=Loader)
                for vid, meta in reg.items():
                    domain_map[vid] = meta.get('domain', '')

    if not os.path.exists(FORMATTED_DIR):
        print(f"Error: Directory '{FORMATTED_DIR}' not found.")
        sys.exit(1)

    # Compile search pattern
    flags = re.IGNORECASE
    if args.regex:
        pattern_str = args.query
    elif args.exact:
        pattern_str = r'\b' + re.escape(args.query) + r'\b'
    else:
        pattern_str = re.escape(args.query)

    try:
        search_regex = re.compile(pattern_str, flags)
    except re.error as e:
        print(f"Invalid regex: {e}")
        sys.exit(1)

    files = sorted([f for f in os.listdir(FORMATTED_DIR) if f.endswith('.yaml')])
    results = []
    scanned_count = 0

    print(f"\n🔍 Searching for '{args.query}' across {len(files)} formatted transcripts...")

    for f in files:
        fpath = os.path.join(FORMATTED_DIR, f)
        with open(fpath, 'r', encoding='utf-8') as fp:
            doc = yaml.load(fp, Loader=Loader)

        scanned_count += 1
        v_type = doc.get('type', 'video')
        channel = doc.get('channel', 'Unknown')
        video_id = doc.get('video_id', '')

        # Apply filters
        if args.type and v_type != args.type:
            continue
        if args.channel and args.channel.lower() not in channel.lower():
            continue
        if args.domain and domain_map.get(video_id) != args.domain:
            continue

        transcript = doc.get('transcript', '')
        if not transcript:
            continue

        match = search_regex.search(transcript)
        if match:
            timestamps = doc.get('timestamps', [])
            matched_char_start = match.start()
            matched_char_end = match.end()

            seconds = find_timestamp_for_char(timestamps, matched_char_start, transcript)
            time_str = format_seconds(seconds)
            jump_url = build_youtube_jump_url(doc.get('url', ''), seconds, video_id)
            snippet = extract_snippet(transcript, matched_char_start, matched_char_end)

            results.append({
                'title': doc.get('title', 'Untitled'),
                'channel': channel,
                'type': v_type,
                'duration': doc.get('duration', '00:00'),
                'time_str': time_str,
                'seconds': seconds,
                'jump_url': jump_url,
                'snippet': snippet,
                'video_id': video_id
            })

            if len(results) >= args.limit:
                break

    print(f"🎯 Found {len(results)} matches (scanned {scanned_count} files):\n")

    if not results:
        print("   No matching transcripts found. Try broadening your query or removing filters.")
        return

    for i, res in enumerate(results, 1):
        type_badge = f"{MAGENTA}[SHORT]{RESET}" if res['type'] == 'short' else f"{CYAN}[VIDEO]{RESET}"
        print(f"{BOLD}{i}. {res['title']}{RESET} {type_badge}")
        print(f"   {DIM}Channel:{RESET} {res['channel']}  |  {DIM}Duration:{RESET} {res['duration']}  |  {DIM}Timestamp:{RESET} {GREEN}{res['time_str']}{RESET} ({res['seconds']}s)")
        print(f"   {DIM}Context:{RESET} \"{res['snippet']}\"")
        if res['jump_url']:
            print(f"   👉 {BOLD}{CYAN}Jump to video:{RESET} {res['jump_url']}")
        print()


if __name__ == '__main__':
    main()
