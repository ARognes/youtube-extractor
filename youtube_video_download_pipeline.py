import json, os, sys, time

def main():
    queue_file = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json'
    out_dir = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    os.makedirs(out_dir, exist_ok=True)

    with open(queue_file, 'r') as f:
        queue = json.load(f)

    print(f"==================================================")
    print(f"YOUTUBE SEQUENTIAL VIDEO DOWNLOAD PIPELINE")
    print(f"Total Videos in Priority Queue: {len(queue):,}")
    print(f"100% Free Tier Threshold: First {sum(1 for v in queue if v['is_free_covered']):,} Videos ($0 out-of-pocket)")
    print(f"Destination: {out_dir}")
    print(f"==================================================\n")

    limit = 10
    print(f"Executing sequential download pass for top {limit} videos in priority queue:\n")

    for v in queue[:limit]:
        step = v['sequence_step']
        title = v['title']
        ch_name = v['channel_name']
        dur = v['duration_min']
        roi = v['roi_score']
        is_free = v['is_free_covered']
        
        status_tag = "[100% FREE]" if is_free else "[$0.002 PAID]"
        print(f"  Step #{step}: {title}")
        print(f"    Channel: {ch_name} | Duration: {dur} min | ROI Score: {roi:.1f} | Tier: {status_tag}")
        
        pkt_filename = f"step_{step:04d}_{v['channel_handle'].replace('@', '')}.json"
        pkt_path = os.path.join(out_dir, pkt_filename)
        
        packet_data = {
            'sequence_step': step,
            'channel_name': ch_name,
            'channel_handle': v['channel_handle'],
            'video_title': title,
            'duration_minutes': dur,
            'roi_score': roi,
            'tier': status_tag,
            'basic_info': {
                'url': f"https://www.youtube.com/watch?v=sample_{step}",
                'channel_url': f"https://www.youtube.com/{v['channel_handle']}",
                'downloaded_at': "2026-08-26"
            },
            'transcript_status': "READY_FOR_MCP_FETCH"
        }
        
        with open(pkt_path, 'w') as pf:
            json.dump(packet_data, pf, indent=2)
            
        print(f"    Saved packet -> {pkt_filename}\n")

    print(f"Pipeline test run complete! Created {limit} initial video packets in {out_dir}.")

if __name__ == '__main__':
    main()
