import json, os, urllib.request, urllib.parse, time

def run():
    out_dir = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    os.makedirs(out_dir, exist_ok=True)

    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/real_home_videos.json', 'r') as f:
        videos = json.load(f)

    api_key = 'sk_JaAysZu79sqC3_fBTneaD3FcFXuhiz1Br9a862wb8JM'

    # Select batch of 25 real videos
    batch = videos[3:28]

    print(f"==================================================")
    print(f"FREE TIER TRANSCRIPT BATCH DOWNLOADER")
    print(f"Targeting {len(batch)} real videos from Home Feed Discovery Map")
    print(f"Using TranscriptAPI (100 Free Starter Credits)")
    print(f"==================================================\n", flush=True)

    success = 0
    skipped = 0

    for idx, v in enumerate(batch, start=4):
        v_url = v['url']
        v_id = v['video_id']
        v_title = v['title']
        v_ch = v['channel']
        v_dur = v['duration']
        
        print(f"[{idx}/207] Fetching: '{v_title}' ({v_ch}, {v_dur})...", flush=True)
        
        req_url = f"https://transcriptapi.com/api/v1/transcript?video_url={urllib.parse.quote(v_url)}&format=text&include_timestamp=true"
        req = urllib.request.Request(req_url, headers={
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'Antigravity/2.0'
        })
        
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                
                pkt_filename = f"step_{idx:04d}_{v_id}.json"
                pkt_path = os.path.join(out_dir, pkt_filename)
                
                packet = {
                    'sequence_step': idx,
                    'video_id': v_id,
                    'video_url': v_url,
                    'title': v_title,
                    'channel': v_ch,
                    'handle': v['handle'],
                    'duration': v_dur,
                    'views': v['views'],
                    'published': v['published'],
                    'status': '100% FREE TIER DOWNLOADED',
                    'metadata': data.get('metadata', {}),
                    'transcript_length_chars': len(data.get('transcript', '') or data.get('content', '')),
                    'transcript_sample': (data.get('transcript', '') or data.get('content', ''))[:300]
                }
                
                with open(pkt_path, 'w') as pf:
                    json.dump(packet, pf, indent=2)
                    
                print(f"  ✓ Saved ({len(packet['transcript_sample'])} chars sample) -> {pkt_filename}", flush=True)
                success += 1
        except Exception as e:
            print(f"  ✗ Skipped/No Captions: {e}", flush=True)
            skipped += 1
        
        time.sleep(0.2)

    print(f"\n==================================================")
    print(f"BATCH COMPLETE:")
    print(f"  Downloaded Transcripts: {success}")
    print(f"  No Captions / Skipped: {skipped}")
    print(f"  Files saved in: {out_dir}")
    print(f"==================================================", flush=True)

if __name__ == '__main__':
    run()
