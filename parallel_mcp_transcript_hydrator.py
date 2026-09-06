import os, sys, json, time, subprocess, concurrent.futures

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def fetch_single_video_transcript(item):
    v_id = item['video_id']
    title = item['title']
    ch_name = item['channel_name']
    step_num = item['sequence_step']
    dir_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'

    # Check if already downloaded
    existing = [f for f in os.listdir(dir_path) if v_id in f and not f.startswith('step_0001_lemondefr')]
    if existing:
        return True, v_id, title, 0

    # Try local youtube_transcript_api Python fetch (Strict 3-retry limit, immediate skip on IP block)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            fetched = YouTubeTranscriptApi().fetch(v_id)
            segs = [{'text': s.text, 'offset': s.start, 'duration': s.duration} for s in fetched]
            full_text = ' '.join(s['text'] for s in segs)
            
            if full_text and len(full_text.split()) >= 10:
                pkt = {
                    'step_number': step_num,
                    'video_id': v_id,
                    'title': title,
                    'channel': ch_name,
                    'handle': item.get('channel_handle',''),
                    'duration': item.get('duration_min', 15),
                    'duration_seconds': int(item.get('duration_min', 15) * 60),
                    'url': f"https://www.youtube.com/watch?v={v_id}",
                    'transcript': full_text,
                    'raw_segments': segs
                }
                fn = f"step_{step_num:04d}_{v_id}.json"
                with open(os.path.join(dir_path, fn), 'w') as pf:
                    json.dump(pkt, pf, indent=2)
                return True, v_id, title, len(full_text.split())
        except Exception as e:
            err_str = str(e).lower()
            if 'ip' in err_str or 'blocked' in err_str or '403' in err_str or attempt >= max_retries:
                break # Give up immediately on IP block or after 3 retries
            time.sleep(1)

    return False, v_id, title, 0

def main():
    queue_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json'
    with open(queue_path, 'r') as f: queue = json.load(f)

    real_items = [q for q in queue if q.get('video_id') and 'Essential Video' not in q.get('title','')]
    log(f"⚡ Launching High-Speed Parallel Transcript Hydrator (8 Threads across {len(real_items)} Real Videos)...")

    saved_count = 0
    t0 = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_single_video_transcript, item) for item in real_items]
        for fut in concurrent.futures.as_completed(futures):
            success, v_id, title, w_count = fut.result()
            if success and w_count > 0:
                saved_count += 1
                log(f"  ✓ [{saved_count}] Saved '{title[:45]}' ({w_count:,} words)")

    t1 = time.time()
    log(f"🎉 Batch Finished in {round(t1 - t0, 1)} seconds! Saved {saved_count} new real transcripts.")

    # Rebuild datasets and dashboard HTML
    log("🔄 Rebuilding Live Dashboard Datasets...")
    subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py'])
    subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py'])
    subprocess.run(['cp', '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/'])

    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/hydrated_viewer_dataset.json', 'r') as f:
        hydrated = json.load(f)

    log(f"🏆 Live Server Hydrated! Total Real Videos in Dashboard: {len(hydrated)}")

if __name__ == '__main__':
    main()
