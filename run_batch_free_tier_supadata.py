import json, os, urllib.request, urllib.parse, time

def main():
    out_dir = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    os.makedirs(out_dir, exist_ok=True)

    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/real_home_videos.json', 'r') as f:
        videos = json.load(f)

    api_key = 'sd_32b8567c225df115f94f200dde8b8b61'

    print(f"==================================================")
    print(f"RE-HYDRATING TRANSCRIPTS TO 100% FULL-LENGTH")
    print(f"Fetching complete segment arrays for all videos")
    print(f"==================================================\n", flush=True)

    success_count = 0
    skipped_count = 0

    for idx, v in enumerate(videos, start=1):
        v_url = v['url']
        v_id = v['video_id']
        v_title = v['title']
        v_ch = v['channel']
        v_dur = v['duration']
        
        pkt_filename = f"step_{idx:04d}_{v_id}.json"
        pkt_path = os.path.join(out_dir, pkt_filename)
        
        # If file exists AND has > 20 segments, it's already full length!
        if os.path.exists(pkt_path):
            try:
                with open(pkt_path, 'r') as pf:
                    existing = json.load(pf)
                    segs = existing.get('raw_segments', [])
                    if isinstance(segs, list) and len(segs) > 20:
                        print(f"[{idx}/{len(videos)}] Already full length ({len(segs)} segments): '{v_title}'", flush=True)
                        success_count += 1
                        continue
            except Exception:
                pass

        print(f"[{idx}/{len(videos)}] Fetching full segments for: '{v_title}' ({v_ch}, {v_dur})...", flush=True)
        
        req_url = f"https://api.supadata.ai/v1/youtube/transcript?url={urllib.parse.quote(v_url)}"
        req = urllib.request.Request(req_url, headers={
            'x-api-key': api_key,
            'User-Agent': 'Antigravity/2.0'
        })
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                content = data.get('content', [])
                
                if isinstance(content, list):
                    full_text = ' '.join([item.get('text', '') for item in content])
                else:
                    full_text = str(content)
                
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
                    'language': data.get('lang', 'en'),
                    'transcript_segment_count': len(content) if isinstance(content, list) else 1,
                    'transcript': full_text,
                    'raw_segments': content # FULL UN-SLICED SEGMENTS
                }
                
                with open(pkt_path, 'w') as pf:
                    json.dump(packet, pf, indent=2)
                    
                print(f"  ✓ Saved FULL ({len(content)} segments / {len(full_text):,} chars) -> {pkt_filename}", flush=True)
                success_count += 1
        except Exception as e:
            print(f"  ✗ Skipped/Limit: {e}", flush=True)
            skipped_count += 1
        
        time.sleep(0.2)

    print(f"\n==================================================")
    print(f"FULL RE-HYDRATION RUN COMPLETE:")
    print(f"  Full Videos Ready: {success_count}")
    print(f"  Skipped / Limit: {skipped_count}")
    print(f"==================================================", flush=True)

if __name__ == '__main__':
    main()
