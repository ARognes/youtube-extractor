import urllib.request, re, json, time, os

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def fetch_real_video_ids_for_handle(handle):
    if not handle: return []
    clean_handle = handle if handle.startswith('@') else f"@{handle}"
    url = f"https://www.youtube.com/{clean_handle}/videos"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    
    video_map = {}
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract videoId and title pairings from initial JSON payload
            matches = re.findall(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\".*?\"title\":\{\"runs\":\[\{\"text\":\"(.*?)\"\}', html)
            for vid, title in matches:
                if vid not in video_map:
                    clean_t = title.encode().decode('unicode-escape', errors='ignore')
                    video_map[vid] = clean_t
            
            # Fallback simple regex
            if not video_map:
                vids = re.findall(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\"', html)
                for v in vids:
                    if v not in video_map:
                        video_map[v] = f"Video {v}"
    except Exception as e:
        log(f"  Error fetching handle {clean_handle}: {e}")
        
    return [{'video_id': vid, 'title': title} for vid, title in video_map.items()]

def main():
    ch_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/channel_structures_dataset.json'
    queue_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json'
    
    with open(ch_path, 'r') as f: channels = json.load(f)
    with open(queue_path, 'r') as f: queue = json.load(f)
    
    log(f"Starting Real YouTube Video ID Resolution across {len(channels)} Channels...")
    
    resolved_total = 0
    channel_video_pool = {}
    
    for ch in channels:
        handle = ch.get('handle')
        name = ch.get('name')
        if not handle: continue
        
        log(f"🔍 Fetching Real Video IDs for '{name}' ({handle})...")
        vids = fetch_real_video_ids_for_handle(handle)
        channel_video_pool[name] = vids
        log(f"   Found {len(vids)} real video IDs for '{name}'.")
        time.sleep(0.5)

    # Populate sequential_video_queue with real video_ids
    ch_indices = {}
    for item in queue:
        ch_name = item.get('channel_name')
        if ch_name in channel_video_pool and channel_video_pool[ch_name]:
            curr_idx = ch_indices.get(ch_name, 0)
            pool = channel_video_pool[ch_name]
            if curr_idx < len(pool):
                real_v = pool[curr_idx]
                item['video_id'] = real_v['video_id']
                item['title'] = real_v['title']
                ch_indices[ch_name] = curr_idx + 1
                resolved_total += 1

    with open(queue_path, 'w') as f:
        json.dump(queue, f, indent=2)

    log(f"🎉 Successfully populated {resolved_total} real YouTube Video IDs into sequential_video_queue.json!")

if __name__ == '__main__':
    main()
