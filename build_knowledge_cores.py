import os
import sys
import json
import re

def log(msg):
    print(f"⚡ [MACE CORE ENGINE] {msg}", flush=True)

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')

# Domain Core Mapping Taxonomy
CORE_TAXONOMY = {
    "core_software_engineering": {
        "title": "Software Engineering & System Architecture Core",
        "description": "High-density technical masterclasses on coding, Rust, VIM, web development, algorithms, and system design.",
        "channel_queries": ["theprimeagen", "freecodecamp", "web dev simplified", "derek banas", "hacking"]
    },
    "core_cognitive_psychology": {
        "title": "Cognitive Psychology & Emotional Processing Core",
        "description": "Evidence-based mental health, Samskara resolution, ADHD burnout recovery, and emotional release frameworks.",
        "channel_queries": ["healthygamergg", "dr. k", "julienhimself", "art of accomplishment", "joe hudson", "theramintrees"]
    },
    "core_business_monetization": {
        "title": "Business Systems & Offer Scaling Core",
        "description": "High-leverage business scaling, offer creation, pricing models, minimum effective dose, and lead generation flywheels.",
        "channel_queries": ["alex hormozi", "tim ferriss"]
    },
    "core_science_philosophy": {
        "title": "Science, Physics & Classical Philosophy Core",
        "description": "Quantum physics, climate science, Carl Jung, Stoicism, Nietzsche, and empirical scientific methodology.",
        "channel_queries": ["sabine hossenfelder", "academy of ideas", "veritasium", "action lab"]
    },
    "core_cybersecurity_homelab": {
        "title": "Cybersecurity, Homelabs & Hardware Hacking Core",
        "description": "Hands-on pen-testing, Docker Swarm homelabs, automation, n8n, and hardware security exploits.",
        "channel_queries": ["networkchuck", "seytonic"]
    },
    "core_pali_philosophy": {
        "title": "Pāli Canon & Early Buddhist Philosophy Core",
        "description": "Direct Sutta textual analysis, epistemic humility, mindfulness mechanisms, and early Buddhist philosophy.",
        "channel_queries": ["doug's dharma", "dougsdharma"]
    }
}

def build_all_archival_cores():
    log("Initializing Modular Archival Core Engine (MACE) compilation...")

    if not os.path.exists(TRANSCRIPTS_DIR):
        log("❌ Error: Transcripts directory missing.")
        return

    t_files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    transcripts_packets = []

    for f in t_files:
        fp = os.path.join(TRANSCRIPTS_DIR, f)
        try:
            with open(fp, 'r', encoding='utf-8') as jf:
                pkt = json.load(jf)
                transcripts_packets.append(pkt)
        except Exception:
            pass

    log(f"Loaded {len(transcripts_packets):,} transcript packets across all channels.")

    cores_manifest = []

    for core_id, core_meta in CORE_TAXONOMY.items():
        log(f"Compiling Archival Core: '{core_meta['title']}'...")

        queries = core_meta["channel_queries"]
        matched_packets = []

        for pkt in transcripts_packets:
            ch = (pkt.get('channel') or pkt.get('channel_name') or '').lower()
            handle = (pkt.get('handle') or pkt.get('channel_handle') or '').lower()
            
            if any(q in ch or q in handle for q in queries):
                matched_packets.append(pkt)

        # Sort matched packets by word count
        matched_packets.sort(key=lambda x: len((x.get('transcript') or '').split()), reverse=True)

        tot_words = sum(len((p.get('transcript') or '').split()) for p in matched_packets)
        tot_vids = len(matched_packets)
        channels_in_core = sorted(list(set(p.get('channel') or p.get('channel_name') for p in matched_packets if p.get('channel'))))

        # Aggregate First Principles & Playbooks
        principles = []
        playbooks = []
        taxonomy_dict = {}

        for p in matched_packets:
            summary = p.get('video_summary') or {}
            takeaways = summary.get('core_takeaways') or []
            for t in takeaways:
                if ':' in t:
                    parts = t.split(':', 1)
                    taxonomy_dict[parts[0].strip()] = parts[1].strip()[:150]
                else:
                    principles.append(t)

        core_data = {
            "core_id": core_id,
            "title": core_meta["title"],
            "description": core_meta["description"],
            "channels_included": channels_in_core,
            "total_videos_archived": tot_vids,
            "total_spoken_words": tot_words,
            "first_principles": principles[:15],
            "taxonomy_dictionary": taxonomy_dict,
            "catalog_summary": [
                {
                    "video_id": p.get('video_id') or p.get('id'),
                    "title": p.get('title'),
                    "channel": p.get('channel'),
                    "word_count": len((p.get('transcript') or '').split()),
                    "synopsis": (p.get('video_summary') or {}).get('executive_synopsis', '')
                } for p in matched_packets[:25]
            ]
        }

        # Save Core JSON
        core_json_path = os.path.join(SCRATCH_DIR, f"{core_id}_master_archive.json")
        with open(core_json_path, 'w', encoding='utf-8') as jf:
            json.dump(core_data, jf, indent=2)

        # Save Core MD
        core_md_path = os.path.join(SCRATCH_DIR, f"{core_id}_master_archive.md")
        md_lines = [
            f"# 🏛️ MACE Knowledge Core: {core_meta['title']}",
            f"**Core ID:** `{core_id}` | **Archived Videos:** {tot_vids} | **Spoken Words:** {tot_words:,}\n",
            f"*{core_meta['description']}*\n",
            f"**Contributing Creators:** {', '.join(channels_in_core)}\n",
            "---",
            "\n## 🎯 1. Core First Principles\n"
        ]
        for pr in principles[:12]:
            md_lines.append(f"- {pr}")

        md_lines.append("\n## 📖 2. Taxonomy & Concept Dictionary\n")
        for k, v in list(taxonomy_dict.items())[:15]:
            md_lines.append(f"- **{k}:** {v}")

        md_lines.append("\n\n## 📚 3. Archival Video Catalog Snapshot\n")
        for item in core_data["catalog_summary"]:
            md_lines.append(f"#### {item['title']} ({item['channel']}) - {item['word_count']:,} words")
            md_lines.append(f"*{item['synopsis']}*\n")

        with open(core_md_path, 'w', encoding='utf-8') as mf:
            mf.write('\n'.join(md_lines))

        cores_manifest.append({
            "core_id": core_id,
            "title": core_meta["title"],
            "channels_count": len(channels_in_core),
            "videos_count": tot_vids,
            "words_count": tot_words,
            "json_path": core_json_path,
            "md_path": core_md_path
        })

        log(f"  ✓ Archival Core Compiled: {core_id} ({tot_vids} videos, {tot_words:,} words)")

    # Save Cores Registry
    registry_path = os.path.join(SCRATCH_DIR, 'knowledge_cores_registry.json')
    with open(registry_path, 'w', encoding='utf-8') as jf:
        json.dump(cores_manifest, jf, indent=2)

    log(f"🎉 MACE Core Engine Compilation Complete! Registry saved to {registry_path}")

if __name__ == '__main__':
    build_all_archival_cores()
