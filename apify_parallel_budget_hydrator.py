#!/usr/bin/env python3
import os
import sys
import json
import time
import urllib.request
import urllib.error
import subprocess
import concurrent.futures
import threading

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
MAX_BUDGET_USD = 5.00  # Hard cap limit for total Apify spend
MAX_PARALLEL_WORKERS = 12  # Run up to 12 parallel cloud scraper threads!

QUEUE_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json"
TRANSCRIPTS_DIR = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts"
DASHBOARD_SRC = "/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html"
DASHBOARD_DST = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html"

stop_flag = False
lock = threading.Lock()
newly_added_count = 0

def get_current_apify_spend():
    url = f"https://api.apify.com/v2/users/me/usage/monthly?token={APIFY_TOKEN}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            spend = data.get("data", {}).get("totalUsageCreditsUsdAfterVolumeDiscount", 0.0)
            return float(spend)
    except Exception as e:
        return 0.0

def fetch_oembed_title(v_id):
    if not v_id or len(str(v_id)) != 11:
        return None
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={v_id}&format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            title = data.get("title")
            if title:
                return title.strip()
    except Exception:
        pass
    return None

def run_apify_actor(v_id):
    url = f"https://api.apify.com/v2/acts/streamers~youtube-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}"
    payload = {
        "startUrls": [{"url": f"https://www.youtube.com/watch?v={v_id}"}],
        "maxResults": 1,
        "downloadSubtitles": True
    }
    data_bytes = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            items = json.loads(resp.read().decode('utf-8'))
            if isinstance(items, list) and len(items) > 0:
                return items[0]
    except Exception as e:
        pass
    return None

def extract_transcript_text(item):
    if not item or not isinstance(item, dict):
        return "", []
    subtitles = item.get("subtitles") or item.get("transcript") or item.get("caption") or []
    segs = []
    if isinstance(subtitles, list):
        segs = subtitles
    elif isinstance(subtitles, dict):
        for lang, seg_list in subtitles.items():
            if isinstance(seg_list, list):
                segs = seg_list
                break
    full_text = " ".join([s.get("text", "") for s in segs if isinstance(s, dict)])
    if not full_text:
        full_text = item.get("text") or item.get("description") or ""
    return full_text.strip(), segs

def rebuild_dashboard_batch():
    try:
        subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/generate_video_summaries_hybrid.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(DASHBOARD_SRC):
            subprocess.run(["cp", DASHBOARD_SRC, DASHBOARD_DST], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        pass

def process_video_item(item):
    global stop_flag, newly_added_count

    if stop_flag:
        return None

    # Check budget before launching
    spend = get_current_apify_spend()
    if spend >= MAX_BUDGET_USD:
        with lock:
            stop_flag = True
        print(f"\n🛑 REACHED BUDGET CAP (${spend:.4f} USD / ${MAX_BUDGET_USD:.2f} USD). Stopping parallel workers.", flush=True)
        return None

    v_id = item["video_id"]
    raw_title = item.get("title", "Untitled")
    channel = item.get("channel_name", "Unknown Channel")
    seq_step = item.get("sequence_step", 0)

    real_title = fetch_oembed_title(v_id) or raw_title
    if "Essential Video" in real_title or "Want to join" in real_title:
        real_title = f"{channel} - Video {v_id}"

    print(f"⚡ [PARALLEL] [Spend: ${spend:.4f} / ${MAX_BUDGET_USD:.2f}] Fetching '{real_title[:35]}' ({channel}) [ID: {v_id}]...", flush=True)

    res = run_apify_actor(v_id)
    full_text, segs = extract_transcript_text(res)
    word_count = len(full_text.split()) if full_text else 0

    if word_count < 10:
        print(f"  ⚠️ No captions for {v_id} ({channel})", flush=True)
        return None

    pkt = {
        "step_number": seq_step,
        "video_id": v_id,
        "title": real_title,
        "channel": channel,
        "handle": item.get("channel_handle", ""),
        "duration": item.get("duration_min", 15),
        "duration_seconds": int(round(item.get("duration_min", 15) * 60)),
        "url": f"https://www.youtube.com/watch?v={v_id}",
        "transcript": full_text,
        "raw_segments": segs
    }

    fn = f"step_{seq_step:04d}_{v_id}.json"
    out_path = os.path.join(TRANSCRIPTS_DIR, fn)
    with open(out_path, 'w', encoding='utf-8') as out_f:
        json.dump(pkt, out_f, indent=2, ensure_ascii=False)

    with lock:
        newly_added_count += 1
        curr_total = newly_added_count

    print(f"  ✓ [SAVED #{curr_total}] '{real_title[:30]}' ({word_count:,} words) -> {fn}", flush=True)
    return fn

def main():
    initial_spend = get_current_apify_spend()
    print(f"🚀 Launching Parallel Multi-Threaded Apify Scraper Engine ({MAX_PARALLEL_WORKERS} Workers)...")
    print(f"   - Current Account Spend: ${initial_spend:.4f} USD")
    print(f"   - Hard Cap Budget: ${MAX_BUDGET_USD:.2f} USD\n", flush=True)

    if initial_spend >= MAX_BUDGET_USD:
        print(f"⛔ Budget cap already reached (${initial_spend:.4f} >= ${MAX_BUDGET_USD:.2f}). Exiting.")
        return

    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    existing_vids = {fn.split('_')[-1].replace('.json', '') for fn in os.listdir(TRANSCRIPTS_DIR) if fn.endswith('.json')}

    pending_items = [s for s in queue if s.get("video_id") and len(str(s.get("video_id"))) == 11 and s.get("video_id") not in existing_vids]

    print(f"📋 Queued {len(pending_items):,} pending real videos for parallel hydration.", flush=True)
    print(f"⚡ Processing top target videos with {MAX_PARALLEL_WORKERS} concurrent cloud threads...\n", flush=True)

    batch_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_PARALLEL_WORKERS) as executor:
        futures = []
        for item in pending_items:
            if stop_flag:
                break
            futures.append(executor.submit(process_video_item, item))
            time.sleep(0.1)  # Stagger thread dispatch by 100ms

        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res:
                batch_count += 1
                if batch_count % 5 == 0:
                    print(f"\n🔄 Batch Update (#{batch_count} videos downloaded): Rebuilding Live Dashboard...", flush=True)
                    rebuild_dashboard_batch()
                    print("🎉 Live Dashboard Rebuilt & Streaming!\n", flush=True)

    # Final rebuild when done
    print("\n🏁 Parallel Batch Execution Complete! Rebuilding final live dashboard...", flush=True)
    rebuild_dashboard_batch()
    final_spend = get_current_apify_spend()
    print(f"✅ Finished! Final Apify Spend: ${final_spend:.4f} USD / ${MAX_BUDGET_USD:.2f} USD cap.")
    print("🎉 Explore updated dashboard at http://localhost:8080/youtube_channel_overview_dashboard.html")

if __name__ == '__main__':
    main()
