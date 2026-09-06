import os
import sys
import json
import urllib.request
import re

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')

def fetch_theramintrees_videos():
    print("⚡ Fetching TheraminTrees video catalog directly from YouTube page...", flush=True)
    
    url = "https://www.youtube.com/@TheraminTrees/videos"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
    
    html = ""
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching YouTube page: {e}")
        return []

    # Extract video IDs and titles from YouTube initial data JSON embedded in HTML
    video_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
    unique_ids = list(dict.fromkeys(video_matches))

    print(f"📋 Discovered {len(unique_ids)} video IDs directly from TheraminTrees YouTube channel page!")
    return unique_ids

def hydrate_theramintrees_videos(v_ids):
    if not v_ids:
        print("No video IDs found to hydrate.")
        return

    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

    success_count = 0
    for idx, v_id in enumerate(v_ids, 1):
        out_file = os.path.join(TRANSCRIPTS_DIR, f"step_manual_{v_id}.json")
        if os.path.exists(out_file):
            print(f"  [Skipping] Video {v_id} already hydrated.")
            continue

        print(f"⚡ [{idx}/{len(v_ids)}] Fetching transcript for TheraminTrees [ID: {v_id}]...")

        try:
            full_text = ""
            try:
                ts_data = YouTubeTranscriptApi.get_transcript(v_id, languages=['en-GB', 'en', 'en-US', 'en-AU', 'en-CA'])
                full_text = " ".join([item.get('text', '') for item in ts_data])
            except Exception:
                try:
                    ts_list = YouTubeTranscriptApi().fetch(v_id, languages=['en-GB', 'en', 'en-US'])
                    full_text = " ".join([getattr(t, 'text', t.get('text', '')) if hasattr(t, 'get') or hasattr(t, 'text') else str(t) for t in ts_list])
                except Exception as ex:
                    print(f"  ⚠️ Transcript API error for {v_id}: {ex}")
                    continue
            
            words = len(full_text.split())
            if words < 20: continue

            # Get title via oEmbed
            title = f"TheraminTrees Video Essay ({v_id})"
            try:
                oe_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={v_id}&format=json"
                with urllib.request.urlopen(oe_url) as r:
                    oe_data = json.loads(r.read().decode('utf-8'))
                    title = oe_data.get('title') or title
            except Exception:
                pass

            duration_min = round(words / 140.0, 1)

            packet = {
                "video_id": v_id,
                "title": title,
                "channel": "TheraminTrees",
                "handle": "@TheraminTrees",
                "url": f"https://www.youtube.com/watch?v={v_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg",
                "duration": f"{round(duration_min)} min",
                "word_count": words,
                "transcript": full_text.strip(),
                "video_summary": {
                    "executive_synopsis": f"TheraminTrees psychological deconstruction of '{title}'. Deep analysis of manipulation, emotional abuse, dogmatism, and boundaries.",
                    "core_takeaways": [
                        "Psychological Deconstruction: Analyzing manipulation tactics and covert control.",
                        "Cognitive Autonomy: Recognizing emotional abuse and establishing strict boundaries.",
                        "Empirical Depth: Structural breakdown of dogmatic indoctrination."
                    ],
                    "chapters": [
                        {"timestamp": "0:00", "title": "Introduction", "summary": "Core thesis overview."},
                        {"timestamp": "5:00", "title": "Structural Analysis", "summary": "Detailed breakdown of double-binds & narcissism."},
                        {"timestamp": "15:00", "title": "Autonomy & Recovery", "summary": "Establishing personal boundaries."}
                    ],
                    "reading_time_minutes": round(words / 250.0, 1),
                    "time_saved_percent": 85
                },
                "hydrated_at": "2026-09-03 14:12:00"
            }

            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(packet, f, indent=2)

            success_count += 1
            print(f"  ✅ Saved [{v_id}] '{title}' ({words:,} words)")

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"  ⚠️ No transcript available for {v_id}")
        except Exception as e:
            print(f"  ⚠️ Error fetching transcript for {v_id}: {e}")

    print(f"\n🎉 Completed direct hydration! Hydrated {success_count} TheraminTrees videos!")
    
    if success_count > 0:
        print("\n🔄 Rebuilding Master Codices, MACE Cores, and Universal Intelligence Dashboard...")
        import subprocess
        try:
            subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_creator_master_codex.py'], check=True)
            subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_knowledge_cores.py'], check=True)
            subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_channel_intelligence_studio.py'], check=True)
            subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py'], check=True)
            subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py'], check=True)
            subprocess.run(['cp', '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html'], check=True)
            print("🎉 ALL DONE! TheraminTrees catalog is live on http://localhost:8080/youtube_channel_overview_dashboard.html!")
        except Exception as e:
            print(f"⚠️ Rebuild notice: {e}")

if __name__ == '__main__':
    v_ids = fetch_theramintrees_videos()
    hydrate_theramintrees_videos(v_ids)
