import os, sys, json, time, subprocess

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def main():
    dir_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    queue_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json'
    
    with open(queue_path, 'r') as f: queue = json.load(f)
    
    real_items = [q for q in queue if q.get('video_id') and 'Essential Video' not in q.get('title','')]
    log(f"🎯 Found {len(real_items)} Real YouTube Video IDs to process.")

    # Get list of video IDs needing transcripts
    needed = []
    for item in real_items:
        v_id = item['video_id']
        existing = [f for f in os.listdir(dir_path) if v_id in f and not f.startswith('step_0001_lemondefr')]
        if not existing:
            needed.append(item)

    log(f"⚡ Transcripts needed for {len(needed)} real videos.")

    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/pending_real_video_downloads.json', 'w') as f:
        json.dump(needed, f, indent=2)

if __name__ == '__main__':
    main()
