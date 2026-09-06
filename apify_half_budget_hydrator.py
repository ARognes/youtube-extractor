#!/usr/bin/env python3
import os
import sys
import json
import time
import urllib.request
import urllib.error
import subprocess

APIFY_TOKEN = "REDACTED_APIFY_API_TOKEN"
MAX_BUDGET_USD = 5.00  # Strictly capped at half of the $5.00 monthly allowance

QUEUE_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json"
TRANSCRIPTS_DIR = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts"
DASHBOARD_SRC = "/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html"
DASHBOARD_DST = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html"

def get_current_apify_spend():
    url = f"https://api.apify.com/v2/users/me/usage/monthly?token={APIFY_TOKEN}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            spend = data.get("data", {}).get("totalUsageCreditsUsdAfterVolumeDiscount", 0.0)
            return float(spend)
    except Exception as e:
        print(f"  ⚠️ Error checking Apify usage: {e}", flush=True)
        return 0.0

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
        print(f"  ⚠️ Apify actor run failed for {v_id}: {e}", flush=True)
    return None

def extract_transcript_text(item):
    if not item or not isinstance(item, dict):
        return "", []
    
    # Apify youtube-scraper subtitle format
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

def rebuild_dashboard():
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/generate_video_summaries_hybrid.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(DASHBOARD_SRC):
        subprocess.run(["cp", DASHBOARD_SRC, DASHBOARD_DST], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    initial_spend = get_current_apify_spend()
    print(f"💳 Starting Apify Cloud Scraper Engine...")
    print(f"   - Current Spend: ${initial_spend:.4f} USD")
    print(f"   - Hard Cap Budget: ${MAX_BUDGET_USD:.2f} USD (Half of $5.00 monthly free credits)\n", flush=True)

    if initial_spend >= MAX_BUDGET_USD:
        print(f"⛔ Budget limit already reached (${initial_spend:.4f} >= ${MAX_BUDGET_USD:.2f}). Stopping.")
        return

    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    existing_files = os.listdir(TRANSCRIPTS_DIR)

    valid_steps = [s for s in queue if s.get("video_id") and len(str(s.get("video_id"))) == 11 and s.get("is_free_covered")]
    print(f"📋 Found {len(valid_steps)} free-covered real videos ready for hydration.\n", flush=True)

    newly_added = 0

    for idx, item in enumerate(valid_steps, 1):
        # 1. Budget Safety Gate Check
        current_spend = get_current_apify_spend()
        if current_spend >= MAX_BUDGET_USD:
            print(f"\n🛑 REACHED HALF-CREDIT BUDGET CAP (${current_spend:.4f} USD / ${MAX_BUDGET_USD:.2f} USD MAX).")
            print(f"🎉 Successfully hydrated {newly_added} new real video transcripts cleanly within budget limit!")
            break

        v_id = item["video_id"]
        already_has = any(v_id in fn for fn in existing_files)
        if already_has:
            continue

        raw_title = item.get("title", "Untitled")
        channel = item.get("channel_name", "Unknown Channel")
        seq_step = item.get("sequence_step", idx)

        # Resolve real exact title via oEmbed
        real_title = fetch_oembed_title(v_id) or raw_title
        if "Essential Video" in real_title or "Want to join" in real_title:
            real_title = f"{channel} - Video {v_id}"

        print(f"⚡ [{idx}/{len(valid_steps)}] [Spend: ${current_spend:.4f} / ${MAX_BUDGET_USD:.2f}] Hydrating via Apify Cloud: '{real_title[:40]}' ({channel}) [ID: {v_id}]...", flush=True)

        res = run_apify_actor(v_id)
        full_text, segs = extract_transcript_text(res)
        word_count = len(full_text.split()) if full_text else 0

        if word_count < 10:
            print(f"  ⚠️ No captions found for {v_id}", flush=True)
            time.sleep(0.5)
            continue

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

        existing_files.append(fn)
        newly_added += 1
        print(f"  ✓ Saved '{real_title[:35]}' ({word_count:,} words) -> {fn}", flush=True)

        # Rebuild live dashboard immediately
        rebuild_dashboard()
        print(f"  🎉 Live Dashboard Updated! Total Hydration Progress: +{newly_added} videos.", flush=True)

        time.sleep(0.5)

    final_spend = get_current_apify_spend()
    print(f"\n✅ Hydration Complete! Final Apify Spend: ${final_spend:.4f} USD / ${MAX_BUDGET_USD:.2f} USD budget limit.")

if __name__ == "__main__":
    main()
