import os, json, subprocess

dir_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'

# Rebuild viewer datasets and dashboard HTML
subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py'])
subprocess.run(['python3', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py'])
subprocess.run(['cp', '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/'])

with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/hydrated_viewer_dataset.json', 'r') as f:
    hydrated = json.load(f)

print(f"🎉 Updated Live Server! Total Real Hydrated Videos in Dashboard: {len(hydrated)}")
