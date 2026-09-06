#!/usr/bin/env python3
import json
import os
import subprocess

QUEUE_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json"
PENDING_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/pending_real_video_downloads.json"
HYDRATOR_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/apify_half_budget_hydrator.py"

TARGET_CREATORS = ["alex hormozi", "a life engineered", "leila hormozi"]

def main():
    print("⚡ Prioritizing Alex Hormozi & A Life Engineered to Top Priority (100x Weight)...")

    if not os.path.exists(QUEUE_FILE):
        print("Queue file not found.")
        return

    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    target_items = []
    other_items = []

    for item in queue:
        ch_name = str(item.get('channel_name', '')).lower()
        handle = str(item.get('channel_handle', '')).lower()
        title = str(item.get('title', '')).lower()

        is_target = any(tc in ch_name or tc in handle for tc in TARGET_CREATORS)

        if is_target:
            item['priority_weight'] = 100.0
            target_items.append(item)
        else:
            other_items.append(item)

    print(f"🎯 Found {len(target_items)} Target Creator Queue Items (Alex Hormozi & A Life Engineered).")
    print(f"🔹 Found {len(other_items)} Other Queue Items.")

    # Combine: Target items first, then others
    new_queue = target_items + other_items

    # Re-index sequence steps
    for idx, item in enumerate(new_queue, 1):
        item['sequence_step'] = idx

    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_queue, f, indent=2, ensure_ascii=False)

    # Update pending_real_video_downloads.json
    pending_real = [item for item in new_queue if item.get('video_id') and len(str(item.get('video_id'))) == 11]
    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump(pending_real, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved updated queue with Target Creators at the front ({len(pending_real):,} pending real videos).")

    # Update apify_half_budget_hydrator.py to set MAX_BUDGET_USD = 5.00
    if os.path.exists(HYDRATOR_FILE):
        with open(HYDRATOR_FILE, 'r', encoding='utf-8') as f:
            code = f.read()

        code = code.replace("MAX_BUDGET_USD = 2.50", "MAX_BUDGET_USD = 5.00")
        with open(HYDRATOR_FILE, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"✅ Updated {HYDRATOR_FILE} setting MAX_BUDGET_USD = $5.00 USD (consuming remaining $2.50 credits).")

if __name__ == '__main__':
    main()
