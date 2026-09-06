import os, json

def main():
    viewer_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/hydrated_viewer_dataset.json'
    ling_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/video_linguistic_analytics_dataset.json'
    
    with open(viewer_path, 'r') as f: viewer_items = json.load(f)
    with open(ling_path, 'r') as f: ling_items = json.load(f)
    
    ling_map = {item['id']: item for item in ling_items}
    
    for item in viewer_items:
        v_id = item['id']
        if v_id in ling_map:
            l_info = ling_map[v_id]
            item['layer3_paragraphs'] = l_info.get('layer3_paragraphs', [])
            item['gross_wpm'] = l_info.get('gross_wpm', 0.0)
            item['net_wpm'] = l_info.get('net_wpm', 0.0)
            item['pause_duration_sec'] = l_info.get('pause_duration_sec', 0.0)
            item['linguistics'] = l_info.get('linguistics', {})

    with open(viewer_path, 'w') as jf:
        json.dump(viewer_items, jf, indent=2)

    print(f"Successfully merged Layer 3 & NLP Analytics into hydrated_viewer_dataset.json for {len(viewer_items)} videos!")

if __name__ == '__main__':
    main()
