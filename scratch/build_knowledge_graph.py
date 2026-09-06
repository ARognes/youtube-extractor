import os
import json
import csv
import re

def log(msg):
    print(f"⚡ {msg}", flush=True)

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')

def generate_knowledge_graph():
    log("Extracting Knowledge Graph Triples (Subject ➔ Predicate ➔ Object)...")

    files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    triples = []

    for f in files:
        fp = os.path.join(TRANSCRIPTS_DIR, f)
        try:
            with open(fp, 'r', encoding='utf-8') as jf:
                pkt = json.load(jf)
                ch = pkt.get('channel') or pkt.get('channel_name') or 'Unknown'
                title = pkt.get('title') or ''
                summary = pkt.get('video_summary') or {}
                takeaways = summary.get('core_takeaways') or []
                chapters = summary.get('chapters') or []

                # Triple Rule 1: Channel HAS_VIDEO Video
                triples.append({
                    "subject": ch,
                    "predicate": "HAS_VIDEO",
                    "object": title,
                    "source_type": "channel_video_relation"
                })

                # Triple Rule 2: Takeaways extraction
                for t in takeaways:
                    if ':' in t:
                        parts = t.split(':', 1)
                        subj = parts[0].strip()
                        obj = parts[1].strip()
                        triples.append({
                            "subject": subj,
                            "predicate": "DEFINES_PRINCIPLE",
                            "object": obj[:120],
                            "source_type": "takeaway_principle"
                        })
                    else:
                        triples.append({
                            "subject": title,
                            "predicate": "TEACHES_CONCEPT",
                            "object": t[:120],
                            "source_type": "takeaway_concept"
                        })

                # Triple Rule 3: Chapter breakdown topics
                for chap in chapters:
                    chap_title = chap.get('title') or ''
                    if chap_title:
                        triples.append({
                            "subject": title,
                            "predicate": "CONTAINS_CHAPTER",
                            "object": chap_title,
                            "source_type": "chapter_relation"
                        })
        except Exception:
            pass

    # Save JSON Triples
    json_path = os.path.join(SCRATCH_DIR, 'knowledge_graph_triples.json')
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump(triples, jf, indent=2)

    # Save CSV Triples (For Neo4j / NetworkX import)
    csv_path = os.path.join(SCRATCH_DIR, 'knowledge_graph_triples.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=["subject", "predicate", "object", "source_type"])
        writer.writeheader()
        writer.writerows(triples)

    log(f"🎉 Extracted {len(triples)} Knowledge Graph Triples! Saved to {json_path} & {csv_path}")

if __name__ == '__main__':
    generate_knowledge_graph()
