#!/usr/bin/env python3
import os
import json
import subprocess
import time
import concurrent.futures
import hydrate_single_video

DESKTOP_JSON = "/Users/austinrognes/Desktop/alex_hormozi_transcripts.json"
QUEUE_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json"
TRANSCRIPTS_DIR = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts"

def hydrate_item(item):
    v_url = item.get('url') or f"https://www.youtube.com/watch?v={item.get('video_id')}"
    try:
        res = hydrate_single_video.hydrate_video(v_url, budget_cap=5.50, skip_rebuild=True)
        return (item.get('video_id'), True)
    except Exception as e:
        print(f"  ⚠️ Error hydrating {v_url}: {e}", flush=True)
        return (item.get('video_id'), False)

def import_and_hydrate_hormozi():
    print("=======================================================", flush=True)
    print("🏛️ IMPORTING ALEX HORMOZI CATALOG FROM DESKTOP", flush=True)
    print("=======================================================", flush=True)

    if not os.path.exists(DESKTOP_JSON):
        print(f"❌ Error: {DESKTOP_JSON} not found!", flush=True)
        return

    with open(DESKTOP_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    videos = data.get("videos", [])
    print(f"📁 Found {len(videos)} Alex Hormozi video records in Desktop file.", flush=True)

    # 1. Identify missing videos
    existing_ids = set()
    for fname in os.listdir(TRANSCRIPTS_DIR):
        if fname.endswith('.json'):
            try:
                with open(os.path.join(TRANSCRIPTS_DIR, fname), 'r', encoding='utf-8') as f_in:
                    v_id = json.load(f_in).get('video_id')
                    if v_id:
                        existing_ids.add(v_id)
            except Exception:
                pass

    missing = [v for v in videos if v.get('video_id') not in existing_ids]
    print(f"🎯 {len(existing_ids)} videos already in dataset. {len(missing)} NEW Alex Hormozi videos to hydrate!", flush=True)

    # 2. Ingest into queue with complete schema fields
    queue_data = []
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f_q:
            queue_data = json.load(f_q)

    new_queue_items = []
    for v in missing:
        v_id = v.get('video_id')
        if v_id:
            new_queue_items.append({
                "video_id": v_id,
                "title": v.get('title'),
                "channel": "Alex Hormozi",
                "duration": v.get('duration'),
                "url": v.get('url') or f"https://www.youtube.com/watch?v={v_id}",
                "priority_weight": 8.0,
                "domain_category": "Software Engineering & Entrepreneurship",
                "is_free_covered": True,
                "cumulative_cost": 0.0,
                "cost_usd": 0.0
            })

    q_ids = set(q.get('video_id') for q in queue_data)
    for nq in new_queue_items:
        if nq['video_id'] not in q_ids:
            queue_data.insert(0, nq)

    with open(QUEUE_FILE, 'w', encoding='utf-8') as f_out:
        json.dump(queue_data, f_out, indent=2, ensure_ascii=False)

    print(f"✅ Ingested {len(new_queue_items)} Alex Hormozi videos to priority queue!", flush=True)

    # 3. Parallel Hydration with 16 Workers
    print(f"⚡ Launching 16 Parallel Hydration Workers for {len(missing)} Alex Hormozi videos...", flush=True)
    success_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(hydrate_item, item) for item in missing]
        for fut in concurrent.futures.as_completed(futures):
            v_id, success = fut.result()
            if success:
                success_count += 1

    print(f"\n🎉 Successfully imported & hydrated {success_count}/{len(missing)} Alex Hormozi videos!", flush=True)
    print("🔄 Rebuilding Universal Intelligence Studio & Dashboard...", flush=True)

    subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_channel_intelligence_studio.py'])
    subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py'])
    subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py'])
    subprocess.run(['cp', '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html'])

    print("✅ All Done! Explore Alex Hormozi on http://localhost:8080/youtube_channel_overview_dashboard.html!", flush=True)

if __name__ == '__main__':
    import_and_hydrate_hormozi()
