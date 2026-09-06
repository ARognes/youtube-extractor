import json, os, sys, time
from youtube_transcript_api import YouTubeTranscriptApi

def format_time(sec):
    try:
        sec = float(sec)
        m, s = divmod(int(sec), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"
    except:
        return "00:00"

def main():
    out_dir = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    os.makedirs(out_dir, exist_ok=True)

    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/real_home_videos.json', 'r') as f:
        real_home = json.load(f)

    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json', 'r') as f:
        global_queue = json.load(f)

    ytt = YouTubeTranscriptApi()

    print("==================================================")
    print("MASS UNLIMITED TRANSCRIPT EXTRACTION PIPELINE")
    print(f"Targeting ALL Free Tier Videos ($0 out-of-pocket)")
    print(f"Destination: {out_dir}")
    print("==================================================\n", flush=True)

    success_count = 0
    skipped_count = 0

    # Phase 1: Real Home Discovery Videos (207 videos)
    print(f"--- Phase 1: Processing {len(real_home)} Real Home Feed Discovery Videos ---", flush=True)
    for idx, v in enumerate(real_home, start=1):
        v_id = v['video_id']
        v_title = v['title']
        v_ch = v['channel']
        v_dur = v['duration']
        
        pkt_filename = f"step_{idx:04d}_{v_id}.json"
        pkt_path = os.path.join(out_dir, pkt_filename)
        
        # Check if already saved with > 20 segments
        if os.path.exists(pkt_path):
            try:
                with open(pkt_path, 'r') as pf:
                    existing = json.load(pf)
                    segs = existing.get('raw_segments', [])
                    if isinstance(segs, list) and len(segs) > 20:
                        print(f"[{idx}/{len(real_home)}] Skip (already complete {len(segs)} lines): '{v_title}'", flush=True)
                        success_count += 1
                        continue
            except Exception:
                pass

        print(f"[{idx}/{len(real_home)}] Fetching: '{v_title}' ({v_ch}, {v_dur})...", flush=True)
        
        snippets = None
        for attempt in range(1, 4):
            try:
                snippets = ytt.fetch(v_id)
                break
            except Exception as e:
                err_str = str(e).lower()
                if 'ip' in err_str or 'blocked' in err_str or '403' in err_str or attempt >= 3:
                    break
                time.sleep(1)

        if not snippets:
            print(f"[{idx}/{len(real_home)}] Skip (No captions or IP rate limit reached): '{v_title}'", flush=True)
            skipped_count += 1
            continue

        segments = []
        full_lines = []
        for s in snippets:
            t_sec = getattr(s, 'start', 0.0)
            txt = getattr(s, 'text', '').strip()
            ts = format_time(t_sec)
            segments.append({'offset': int(t_sec * 1000), 'text': txt})
            if txt:
                full_lines.append(f"{ts} {txt}")
            
            full_text = ' '.join([s.get('text', '') for s in segments])
            
            packet = {
                'sequence_step': idx,
                'video_id': v_id,
                'video_url': v.get('url', f"https://www.youtube.com/watch?v={v_id}"),
                'title': v_title,
                'channel': v_ch,
                'handle': v.get('handle', ''),
                'duration': v_dur,
                'views': v.get('views', 'N/A'),
                'published': v.get('published', 'N/A'),
                'status': '100% FREE UNLIMITED DOWNLOADED',
                'language': 'en',
                'transcript_segment_count': len(segments),
                'transcript': full_text,
                'raw_segments': segments
            }
            
            with open(pkt_path, 'w') as pf:
                json.dump(packet, pf, indent=2)
                
            print(f"  ✓ Saved ({len(segments)} timestamped lines / {len(full_text):,} chars) -> {pkt_filename}", flush=True)
            success_count += 1
        except Exception as e:
            print(f"  ✗ Skipped/No Captions: {e}", flush=True)
            skipped_count += 1
            
        time.sleep(0.15)

    print(f"\n==================================================")
    print(f"MASS EXTRACTION PASS COMPLETE:")
    print(f"  Total Valid Full Transcripts Ready: {success_count}")
    print(f"  Skipped / No Captions: {skipped_count}")
    print(f"  All packets saved in: {out_dir}")
    print(f"==================================================", flush=True)

if __name__ == '__main__':
    main()
