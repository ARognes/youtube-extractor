import os, sys, json, time, urllib.request, subprocess

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def fetch_transcript_via_mcp_or_api(v_id):
    # Call transcriptapi service
    url = f"https://transcriptapi.com/api/transcript?v={v_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if isinstance(data, list):
                segs = [{'text': s.get('text',''), 'offset': s.get('start', s.get('offset', 0)), 'duration': s.get('duration', 0)} for s in data]
                full_text = ' '.join(s['text'] for s in segs)
                return full_text, segs
    except Exception:
        pass

    # Retry cap on local youtube_transcript_api (Max 3 attempts, immediate skip on IP block)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            fetched = YouTubeTranscriptApi().fetch(v_id)
            segs = [{'text': s.text, 'offset': s.start, 'duration': s.duration} for s in fetched]
            full_text = ' '.join(s['text'] for s in segs)
            if full_text and len(full_text.split()) >= 10:
                return full_text, segs
        except Exception as e:
            err_str = str(e).lower()
            if 'ip' in err_str or 'blocked' in err_str or '403' in err_str or attempt >= max_retries:
                break # Immediate give-up on IP rate limits or max retries
            time.sleep(1)

    return None, []

def main():
    dir_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    queue_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json'
    
    with open(queue_path, 'r') as f: queue = json.load(f)
    
    real_queue_items = [q for q in queue if q.get('video_id') and 'Essential Video' not in q.get('title','')]
    log(f"🚀 Starting Real YouTube Video Transcript Scraper Engine ({len(real_queue_items)} Real YouTube Video IDs)")

    processed_count = 0

    for item in queue:
        v_id = item.get('video_id')
        title = item.get('title', '')
        ch_name = item.get('channel_name', 'Unknown')
        step_num = item.get('sequence_step', 0)

        if not v_id or 'Essential Video' in title:
            continue

        # Check if already downloaded
        existing = [f for f in os.listdir(dir_path) if v_id in f and not f.startswith('step_0001_lemondefr')]
        if existing:
            continue

        log(f"⚡ Fetching Transcript for Step #{step_num:04d}: '{title[:50]}' ({ch_name}) [ID: {v_id}]")

        full_text, raw_segs = fetch_transcript_via_mcp_or_api(v_id)

        if not full_text:
            log(f"   ⚠️ Could not retrieve transcript for video {v_id} (Skipping...)")
            continue

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
            'raw_segments': raw_segs
        }

        fn = f"step_{step_num:04d}_{v_id}.json"
        with open(os.path.join(dir_path, fn), 'w') as pf:
            json.dump(pkt, pf, indent=2)

        processed_count += 1
        log(f"   ✓ Saved {len(full_text.split())} words transcript for '{title[:40]}'")

        # Rebuild datasets & update live web server
        subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py'], stdout=subprocess.DEVNULL)
        subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py'], stdout=subprocess.DEVNULL)
        subprocess.run(['cp', '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/'])

        time.sleep(0.5)

    log(f"🎉 Complete! Processed {processed_count} new real YouTube video transcripts!")

if __name__ == '__main__':
    main()
