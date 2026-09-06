#!/usr/bin/env python3
import os
import json
import re
import subprocess

TRANSCRIPTS_DIR = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts"
QUEUE_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json"
PENDING_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/pending_real_video_downloads.json"
DASHBOARD_SRC = "/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html"
DASHBOARD_DST = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html"

def sanitize_title(title_str):
    if not title_str:
        return "Untitled Video"
    
    # 1. Truncate any raw JSON leakage
    if '","navigationEndpoint"' in title_str:
        title_str = title_str.split('","navigationEndpoint"')[0]
    if '","clickTrackingParams"' in title_str:
        title_str = title_str.split('","clickTrackingParams"')[0]
    if '","webCommandMetadata"' in title_str:
        title_str = title_str.split('","webCommandMetadata"')[0]
    if '","commandMetadata"' in title_str:
        title_str = title_str.split('","commandMetadata"')[0]
    if '","' in title_str:
        title_str = title_str.split('","')[0]
        
    # 2. Fix escaped quotes and unicode
    title_str = title_str.replace('\\"', '"').replace('\\n', ' ').strip()
    title_str = re.sub(r'\s+', ' ', title_str)
    
    return title_str

def main():
    print("🧹 Starting Title Cleaning & Strict Deduplication Master Pass...")

    # 1. Process files in downloaded_transcripts/
    files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    print(f"📁 Inspecting {len(files)} transcript files in {TRANSCRIPTS_DIR}...")

    vid_to_files = {}
    cleaned_titles_count = 0

    for fname in files:
        fpath = os.path.join(TRANSCRIPTS_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data.get("title") or data.get("video_title") or ""
            clean = sanitize_title(title)

            if clean != title:
                cleaned_titles_count += 1
                print(f"  ✨ Sanitized Title [{fname}]: '{title[:50]}...' -> '{clean}'")
                data["title"] = clean
                if "video_title" in data:
                    data["video_title"] = clean
                with open(fpath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            v_id = data.get("video_id")
            if v_id:
                vid_to_files.setdefault(v_id, []).append(fname)
        except Exception as e:
            print(f"  ⚠️ Error reading {fname}: {e}")

    # 2. Deduplicate files (keep lowest step number)
    removed_dups_count = 0
    for v_id, file_list in vid_to_files.items():
        if len(file_list) > 1:
            # Sort by step number in filename
            file_list.sort(key=lambda x: int(re.search(r'step_(\d+)', x).group(1)) if re.search(r'step_(\d+)', x) else 999999)
            keep_file = file_list[0]
            remove_files = file_list[1:]

            for r_file in remove_files:
                r_path = os.path.join(TRANSCRIPTS_DIR, r_file)
                if os.path.exists(r_path):
                    os.remove(r_path)
                    removed_dups_count += 1
                    print(f"  🗑️ Removed duplicate file: {r_file} (Kept: {keep_file})")

    print(f"\n✅ Cleaned {cleaned_titles_count} dirty titles and removed {removed_dups_count} duplicate files!")

    # 3. Clean Titles & Deduplicate in sequential_video_queue.json
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)

        seen_vids = set()
        clean_queue = []

        for item in queue:
            t = item.get("title", "")
            c_t = sanitize_title(t)
            item["title"] = c_t

            v_id = item.get("video_id")
            if v_id and len(str(v_id)) == 11:
                if v_id in seen_vids:
                    continue
                seen_vids.add(v_id)

            clean_queue.append(item)

        # Re-index sequence steps
        for idx, item in enumerate(clean_queue, 1):
            item["sequence_step"] = idx

        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(clean_queue, f, indent=2, ensure_ascii=False)

        print(f"✅ Cleaned titles & deduplicated sequential_video_queue.json ({len(queue):,} -> {len(clean_queue):,} unique steps).")

    # 4. Clean Titles & Deduplicate in pending_real_video_downloads.json
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            pending = json.load(f)

        seen_p_vids = set()
        clean_pending = []

        for item in pending:
            t = item.get("title", "")
            item["title"] = sanitize_title(t)

            v_id = item.get("video_id")
            if v_id and len(str(v_id)) == 11:
                if v_id in seen_p_vids:
                    continue
                seen_p_vids.add(v_id)

            clean_pending.append(item)

        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(clean_pending, f, indent=2, ensure_ascii=False)

        print(f"✅ Cleaned titles & deduplicated pending_real_video_downloads.json ({len(pending):,} -> {len(clean_pending):,} unique real pending videos).")

    # 5. Rebuild Live Viewer & Dashboard
    print("\n🔄 Rebuilding live viewer dataset and dashboard...")
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py"])
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py"])

    if os.path.exists(DASHBOARD_SRC):
        subprocess.run(["cp", DASHBOARD_SRC, DASHBOARD_DST])
        print("🎉 Dashboard successfully updated at http://localhost:8080/youtube_channel_overview_dashboard.html!")

if __name__ == '__main__':
    main()
