#!/usr/bin/env python3
"""
query_tag_silo.py

CLI tool to query and inspect the channel-isolated tag silos.

Usage:
  python3 query_tag_silo.py --stats
  python3 query_tag_silo.py --channel healthygamergg --tag samskara
  python3 query_tag_silo.py --channel theramintrees --tag double_bind
  python3 query_tag_silo.py --channel healthygamergg --video Ads8VOa0qKQ
"""

import os
import sys
import json
import yaml
import argparse

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TAG_SILO_ROOT = os.path.join(SCRATCH_DIR, 'tag_silo')

def print_stats():
    print("\n=======================================================")
    print("🏷️  CHANNEL TAG SILOS OVERVIEW")
    print("=======================================================")
    if not os.path.exists(TAG_SILO_ROOT):
        print("No tag silos found at tag_silo/. Run build_channel_tag_silo.py first.")
        return

    channels = sorted([d for d in os.listdir(TAG_SILO_ROOT) if os.path.isdir(os.path.join(TAG_SILO_ROOT, d))])
    if not channels:
        print("No channel directories inside tag_silo/.")
        return

    for ch in channels:
        ch_dir = os.path.join(TAG_SILO_ROOT, ch)
        tax_path = os.path.join(ch_dir, 'channel_taxonomy.yaml')
        if os.path.exists(tax_path):
            with open(tax_path, 'r', encoding='utf-8') as f:
                tax = yaml.load(f, Loader=SafeLoader)
            print(f"\n📁 Channel: {ch.upper()}")
            print(f" - Videos Tagged: {tax.get('total_videos_analyzed', 0)}")
            print(f" - Spoken Words: {tax.get('total_spoken_words', 0):,}")
            dims = tax.get('dimensions', {})
            for dname, dtags in dims.items():
                print(f"   * {dname}: {len(dtags)} tags ({', '.join(list(dtags.keys())[:5])}...)")

def query_tag(channel, tag_name):
    ch_dir = os.path.join(TAG_SILO_ROOT, channel)
    inv_path = os.path.join(ch_dir, 'inverted_tag_index.json')
    if not os.path.exists(inv_path):
        print(f"Error: Inverted index not found for channel '{channel}'.")
        return

    with open(inv_path, 'r', encoding='utf-8') as f:
        inv = json.load(f)

    index = inv.get('index', {})
    matches = index.get(tag_name)
    if not matches:
        # Partial match
        candidates = [t for t in index if tag_name in t]
        if candidates:
            print(f"Exact tag '{tag_name}' not found. Did you mean: {', '.join(candidates)}?")
            tag_name = candidates[0]
            matches = index[tag_name]
        else:
            print(f"Tag '{tag_name}' not found in channel '{channel}'.")
            return

    print(f"\n🎯 Tag '{tag_name}' in channel '{channel.upper()}' ({len(matches)} matching videos):")
    for m in matches:
        ts_str = ", ".join(m.get('timestamps', [])) or "Full video"
        print(f" - [{m['video_id']}] {m['title']}")
        print(f"   Timestamps: {ts_str}")

def inspect_video(channel, video_id):
    v_path = os.path.join(TAG_SILO_ROOT, channel, 'videos', f"{video_id}.yaml")
    if not os.path.exists(v_path):
        print(f"Error: Video tag record not found at {v_path}")
        return

    with open(v_path, 'r', encoding='utf-8') as f:
        rec = yaml.load(f, Loader=SafeLoader)

    print(f"\n🎬 [{rec['video_id']}] {rec['title']}")
    print(f"Channel: {rec['channel']} | Duration: {rec['duration']} | Words: {rec['word_count']:,}")
    print(f"URL: {rec['url']}")
    print(f"Hook: {rec['summary_hook']}")
    print(f"Domains: {', '.join(rec['domains'])}")
    print(f"Concepts: {', '.join(rec['concepts'])}")
    print(f"Pain Points: {', '.join(rec['pain_points'])}")
    print(f"Protocols: {', '.join(rec['actionable_protocols'])}")
    print(f"Modalities: {', '.join(rec['modalities'])}")
    print(f"Key Phrases: {', '.join(rec['key_phrases'])}")
    if rec.get('segment_tags'):
        print("\nTimestamped Tag Activations:")
        for st in rec['segment_tags'][:8]:
            print(f" - [{st['timestamp']}] #{st['tag']}: \"{st['context']}\"")

def main():
    parser = argparse.ArgumentParser(description="Query tag silos.")
    parser.add_argument("--channel", type=str, help="Channel slug (e.g. healthygamergg, theramintrees)")
    parser.add_argument("--tag", type=str, help="Tag name to lookup")
    parser.add_argument("--video", type=str, help="Video ID to inspect")
    parser.add_argument("--stats", action="store_true", help="Print tag silo overview statistics")
    args = parser.parse_args()

    if args.stats or (not args.channel and not args.tag and not args.video):
        print_stats()
        return

    if args.video:
        if not args.channel:
            print("Error: --channel required when using --video.")
            return
        inspect_video(args.channel, args.video)
        return

    if args.tag:
        if not args.channel:
            print("Error: --channel required when using --tag.")
            return
        query_tag(args.channel, args.tag)
        return

if __name__ == '__main__':
    main()
