import subprocess, re, json, time, os, concurrent.futures

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def fetch_real_video_ids_curl(channel_info):
    name = channel_info.get('name')
    handle = channel_info.get('handle')
    if not handle: return name, []
    
    clean_handle = handle if handle.startswith('@') else f"@{handle}"
    
    urls = [
        f"https://www.youtube.com/{clean_handle}/videos",
        f"https://www.youtube.com/{clean_handle}/streams",
        f"https://www.youtube.com/{clean_handle}/shorts"
    ]
    
    video_map = {}
    
    for url in urls:
        cmd = ['curl', '-sL', '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', url]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            html = res.stdout
            
            # Pattern 1: videoId with title runs
            matches = re.findall(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\".*?\"title\":\{\"runs\":\[\{\"text\":\"(.*?)\"\}', html)
            for vid, title in matches:
                if vid not in video_map and '\\u' not in title:
                    video_map[vid] = title.encode().decode('unicode-escape', errors='ignore')
                    
            # Pattern 2: videoId with simpleText
            matches_simple = re.findall(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\".*?\"simpleText\":\"(.*?)\"', html)
            for vid, title in matches_simple:
                if vid not in video_map:
                    video_map[vid] = title
                    
            # Pattern 3: raw videoId
            vids = re.findall(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\"', html)
            for v in vids:
                if v not in video_map:
                    video_map[v] = f"Video {v}"
        except Exception:
            pass
            
    return name, [{'video_id': vid, 'title': title} for vid, title in video_map.items()]

def main():
    ch_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/channel_structures_dataset.json'
    queue_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json'
    
    with open(ch_path, 'r') as f: channels = json.load(f)
    with open(queue_path, 'r') as f: queue = json.load(f)
    
    log(f"⚡ Deep Parallel Real Video ID Resolution across {len(channels)} Channels...")
    
    channel_video_pool = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(fetch_real_video_ids_curl, ch) for ch in channels]
        for fut in concurrent.futures.as_completed(futures):
            name, vids = fut.result()
            if vids:
                channel_video_pool[name] = vids
                log(f"   ✓ '{name}': Resolved {len(vids)} real video IDs")

    total_pool_ids = sum(len(v) for v in channel_video_pool.values())
    log(f"🎉 Total Real YouTube Video IDs Harvested Across Channels: {total_pool_ids:,}")

    resolved_total = 0
    ch_indices = {}
    for item in queue:
        ch_name = item.get('channel_name')
        if ch_name in channel_video_pool and channel_video_pool[ch_name]:
            curr_idx = ch_indices.get(ch_name, 0)
            pool = channel_video_pool[ch_name]
            if curr_idx < len(pool):
                real_v = pool[curr_idx]
                item['video_id'] = real_v['video_id']
                if real_v['title'] and not real_v['title'].startswith('Video '):
                    item['title'] = real_v['title']
                ch_indices[ch_name] = curr_idx + 1
                resolved_total += 1

    with open(queue_path, 'w') as f:
        json.dump(queue, f, indent=2)

    log(f"🎉 Successfully mapped {resolved_total:,} real YouTube Video IDs into sequential_video_queue.json!")

    # Re-run domain weighting to maintain 8x Software Engineering priority
    subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/resequence_domain_weighted_queue.py'])

if __name__ == '__main__':
    main()
