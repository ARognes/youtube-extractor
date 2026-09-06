import json, os, sys, subprocess

def ingest_mcp_output(v_id, title, channel_name, step_num, mcp_file_path):
    dir_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    
    with open(mcp_file_path, 'r') as f:
        raw_content = json.load(f)

    # Content structure from transcriptapi MCP tool
    content = raw_content.get('content', raw_content)
    if isinstance(content, str):
        try: content = json.loads(content)
        except Exception: pass

    transcript_list = []
    real_title = title
    real_channel = channel_name

    if isinstance(content, dict):
        if 'transcript' in content and isinstance(content['transcript'], list):
            transcript_list = content['transcript']
        elif 'results' in content:
            transcript_list = content.get('results', [])
        
        meta = content.get('metadata', {})
        if meta.get('title'): real_title = meta['title']
        if meta.get('author_name'): real_channel = meta['author_name']

    elif isinstance(content, list):
        transcript_list = content

    full_text = ""
    if transcript_list:
        full_text = ' '.join(s.get('text', '') for s in transcript_list if isinstance(s, dict) and s.get('text'))

    if not full_text:
        print("No transcript text found in MCP output.")
        return False

    pkt = {
        'step_number': step_num,
        'video_id': v_id,
        'title': real_title,
        'channel': real_channel,
        'handle': '',
        'duration': 15,
        'duration_seconds': 900,
        'url': f"https://www.youtube.com/watch?v={v_id}",
        'transcript': full_text,
        'raw_segments': transcript_list
    }

    fn = f"step_{step_num:04d}_{v_id}.json"
    target_path = os.path.join(dir_path, fn)
    with open(target_path, 'w') as pf:
        json.dump(pkt, pf, indent=2)

    print(f"✓ Successfully saved '{real_title}' ({len(full_text.split()):,} words) to {fn}")

    # Rebuild datasets and dashboard HTML
    subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py'])
    subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py'])
    subprocess.run(['cp', '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/'])

    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/hydrated_viewer_dataset.json', 'r') as f:
        hydrated = json.load(f)

    print(f"🎉 Live Dashboard Updated! Total Real Hydrated Videos: {len(hydrated)}")
    return True

if __name__ == '__main__':
    v_id = sys.argv[1]
    title = sys.argv[2]
    ch_name = sys.argv[3]
    step_num = int(sys.argv[4])
    mcp_file_path = sys.argv[5]
    ingest_mcp_output(v_id, title, ch_name, step_num, mcp_file_path)
