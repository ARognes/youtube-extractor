#!/usr/bin/env python3
import os
import json
import urllib.request
import concurrent.futures
import time
import subprocess

TRANSCRIPTS_DIR = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts"
QUEUE_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json"
PENDING_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/pending_real_video_downloads.json"
DASHBOARD_SRC = "/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html"
DASHBOARD_DST = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html"

GENERIC_TITLES = [
    "Want to join this channel?", "Keyboard shortcuts", "Interview Shorts",
    "Our Other Channels!", "noclip_2cast", "Just The Big Docs", "Hyper Light Development"
]

def fetch_oembed_title(v_id):
    if not v_id or len(str(v_id)) != 11:
        return v_id, None
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={v_id}&format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            title = data.get("title")
            if title:
                return v_id, title.strip()
    except Exception:
        pass
    return v_id, None

def main():
    print("⚡ Resolving Real Exact YouTube Video Titles via YouTube oEmbed API...")

    # 1. Process files in downloaded_transcripts/
    files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    print(f"📁 Inspecting {len(files)} transcript packets in {TRANSCRIPTS_DIR}...")

    file_vids_to_resolve = []
    for fname in files:
        fpath = os.path.join(TRANSCRIPTS_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            t = data.get("title") or data.get("video_title") or ""
            v_id = data.get("video_id")
            if v_id and (any(gt in t for gt in GENERIC_TITLES) or "Essential Video" in t):
                file_vids_to_resolve.append((fname, fpath, v_id, t))
        except Exception:
            pass

    print(f"🎯 Found {len(file_vids_to_resolve)} transcript packets with generic/placeholder titles.")

    resolved_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(fetch_oembed_title, item[2]): item for item in file_vids_to_resolve}
        for fut in concurrent.futures.as_completed(futures):
            v_id, real_t = fut.result()
            if real_t:
                resolved_map[v_id] = real_t

    updated_files = 0
    for fname, fpath, v_id, old_t in file_vids_to_resolve:
        if v_id in resolved_map:
            real_t = resolved_map[v_id]
            print(f"  ✨ Updated [{v_id}]: '{old_t}' ➜ '{real_t}'")
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data["title"] = real_t
                data["video_title"] = real_t
                with open(fpath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                updated_files += 1
            except Exception as e:
                print(f"  ⚠️ Failed to write {fname}: {e}")

    print(f"\n✅ Resolved and updated real titles for {updated_files} transcript files!")

    # 2. Update sequential_video_queue.json & pending_real_video_downloads.json
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        for item in queue:
            v_id = item.get("video_id")
            if v_id in resolved_map:
                item["title"] = resolved_map[v_id]
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)

    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            pending = json.load(f)
        for item in pending:
            v_id = item.get("video_id")
            if v_id in resolved_map:
                item["title"] = resolved_map[v_id]
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(pending, f, indent=2, ensure_ascii=False)

    # 3. Re-run hybrid summaries & dashboard rebuild
    print("\n🔄 Re-running hybrid summaries & updating live dashboard...")
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/generate_video_summaries_hybrid.py"])
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py"])
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py"])

    if os.path.exists(DASHBOARD_SRC):
        subprocess.run(["cp", DASHBOARD_SRC, DASHBOARD_DST])
        print("🎉 Dashboard successfully updated at http://localhost:8080/youtube_channel_overview_dashboard.html!")

if __name__ == '__main__':
    main()
