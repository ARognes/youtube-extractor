import os
import sys
import json
import argparse
import datetime

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')

def ingest_custom_source(title, text, core_id, author="External Source", source_url=""):
    words = len(text.split())
    doc_id = f"ext_{int(datetime.datetime.now().timestamp())}"

    packet = {
        "video_id": doc_id,
        "title": title,
        "channel": author,
        "handle": f"@{author.lower().replace(' ', '')}",
        "url": source_url or f"file://{doc_id}",
        "duration": f"{round(words/150.0, 1)} min",
        "word_count": words,
        "transcript": text.strip(),
        "video_summary": {
            "executive_synopsis": f"Custom ingested archival document: '{title}' by {author}.",
            "core_takeaways": [
                f"Core Takeaway from {title}: Ingested into {core_id}."
            ],
            "chapters": [
                {"timestamp": "0:00", "title": "Overview", "summary": f"Ingested text content from {author}."}
            ]
        },
        "hydrated_at": datetime.datetime.now().isoformat()
    }

    out_path = os.path.join(TRANSCRIPTS_DIR, f"step_manual_{doc_id}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(packet, f, indent=2)

    print(f"✅ Ingested custom source '{title}' ({words:,} words) into {out_path}!", flush=True)
    return packet

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', default="Modern Web Architecture Guide")
    parser.add_argument('--text', default="High-performance web API engineering and system design patterns for 2026.")
    parser.add_argument('--core', default="core_software_engineering")
    parser.add_argument('--author', default="Engineering Archival Paper")
    args = parser.parse_args()

    ingest_custom_source(args.title, args.text, args.core, args.author)
