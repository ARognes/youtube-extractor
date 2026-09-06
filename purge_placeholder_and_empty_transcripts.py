#!/usr/bin/env python3
import os
import json
import subprocess

TRANSCRIPTS_DIR = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts"
DASHBOARD_SRC = "/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html"
DASHBOARD_DST = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html"

def main():
    files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    print(f"🧹 Auditing & Purging Placeholder/Empty Transcripts across {len(files)} files in {TRANSCRIPTS_DIR}...")

    removed_placeholders = 0
    removed_empty_music = 0
    kept_count = 0

    for fname in files:
        fpath = os.path.join(TRANSCRIPTS_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = str(data.get("title") or data.get("video_title") or "")
            v_id = str(data.get("video_id") or "")
            transcript = str(data.get("transcript") or "")
            words = transcript.split()

            # 1. Synthetic placeholder check
            if "Essential Video" in title or fname.endswith("_vid.json") or "lemondefr" in fname or len(v_id) != 11:
                os.remove(fpath)
                removed_placeholders += 1
                print(f"  🗑️ Removed synthetic placeholder: {fname} ('{title[:40]}')")
                continue

            # 2. Non-verbal / 0-word instrumental music check
            if len(words) < 10:
                os.remove(fpath)
                removed_empty_music += 1
                print(f"  🎵 Removed non-verbal/music video ({len(words)} words): {fname} ('{title[:40]}')")
                continue

            kept_count += 1
        except Exception as e:
            print(f"  ⚠️ Error reading {fname}: {e}")

    print(f"\n✅ Audit Complete!")
    print(f"   - Removed Synthetic Placeholders: {removed_placeholders}")
    print(f"   - Removed Non-Verbal/0-Word Music Videos: {removed_empty_music}")
    print(f"   - Kept High-Quality Real Spoken Transcripts: {kept_count}")

    # Rebuild Live Dashboard
    print("\n🔄 Rebuilding live viewer dataset and dashboard...")
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py"])
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py"])

    if os.path.exists(DASHBOARD_SRC):
        subprocess.run(["cp", DASHBOARD_SRC, DASHBOARD_DST])
        print("🎉 Dashboard successfully updated at http://localhost:8080/youtube_channel_overview_dashboard.html!")

if __name__ == '__main__':
    main()
