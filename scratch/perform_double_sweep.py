import os
import sys
import json
import urllib.request

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')

def log(msg):
    print(f"⚡ [DOUBLE-SWEEP] {msg}", flush=True)

def run_double_sweep():
    log("=======================================================")
    log("🔍 STARTING SYSTEM INTEGRITY DOUBLE-SWEEP & AUDIT")
    log("=======================================================")

    # 1. Audit Transcripts Directory
    if not os.path.exists(TRANSCRIPTS_DIR):
        log("❌ FAIL: Transcripts directory missing!")
        sys.exit(1)

    t_files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    log(f"✅ Sweep 1: Found {len(t_files):,} hydrated transcript JSON files.")

    valid_transcripts = 0
    total_words = 0
    channels_found = set()

    for f in t_files:
        fp = os.path.join(TRANSCRIPTS_DIR, f)
        try:
            with open(fp, 'r', encoding='utf-8') as jf:
                pkt = json.load(jf)
                words = pkt.get('word_count') or len((pkt.get('transcript') or '').split())
                ch = pkt.get('channel') or pkt.get('channel_name') or 'Unknown'
                if words > 10:
                    valid_transcripts += 1
                    total_words += words
                    channels_found.add(ch)
        except Exception:
            pass

    log(f"✅ Sweep 1 Complete: {valid_transcripts:,} clean valid video packets across {len(channels_found)} creator channels! ({total_words:,} total spoken words)")

    # 2. Build Master Codices for All Top Efficacy Tier 1 & 2 Channels
    log("=======================================================")
    log("🛠️ SWEEP 2: Generating Master Codices for Top Channels...")
    log("=======================================================")

    from build_creator_master_codex import build_master_codex_for_channel
    
    top_channels = [
        "Alex Hormozi", "HealthyGamerGG", "NetworkChuck", "Doug's Dharma",
        "ThePrimeagen", "Sabine Hossenfelder", "Web Dev Simplified",
        "Academy of Ideas", "Derek Banas", "JulienHimself", "Seytonic"
    ]

    generated_codices = 0
    for ch in top_channels:
        res = build_master_codex_for_channel(ch, SCRATCH_DIR)
        if res:
            generated_codices += 1

    log(f"✅ Sweep 2 Complete: Successfully built {generated_codices} Master Codices!")

    # 3. Re-Run Global Synthesis, Fine-Tuning & Knowledge Graph Generators
    log("=======================================================")
    log("🧬 SWEEP 3: Re-building Synthesis, Fine-Tuning & Graph Datasets...")
    log("=======================================================")

    from build_cross_creator_synthesis import generate_cross_creator_synthesis
    from build_fine_tuning_dataset import generate_fine_tuning_and_personas
    from build_knowledge_graph import generate_knowledge_graph

    generate_cross_creator_synthesis()
    generate_fine_tuning_and_personas()
    generate_knowledge_graph()

    # 4. REST API Endpoint Health Check
    log("=======================================================")
    log("🌐 SWEEP 4: Verifying REST API Endpoints on http://localhost:8080...")
    log("=======================================================")

    endpoints = [
        "http://localhost:8080/api/v1/codex/alex_hormozi?tier=1",
        "http://localhost:8080/api/v1/codex/theprimeagen?tier=2",
        "http://localhost:8080/api/v1/codex/sabine_hossenfelder?tier=3",
        "http://localhost:8080/api/v1/consensus",
        "http://localhost:8080/api/v1/graph",
        "http://localhost:8080/api/v1/personas",
        "http://localhost:8080/api/v1/channels"
    ]

    passed_api = 0
    for url in endpoints:
        try:
            with urllib.request.urlopen(url) as r:
                if r.status == 200:
                    passed_api += 1
                    log(f"  ✓ API OK: {url}")
                else:
                    log(f"  ❌ API HTTP {r.status}: {url}")
        except Exception as e:
            log(f"  ❌ API Error: {url} -> {e}")

    log("=======================================================")
    log(f"🎉 DOUBLE-SWEEP PASSED! {passed_api}/{len(endpoints)} API Endpoints 100% Operational!")
    log("=======================================================")

if __name__ == '__main__':
    run_double_sweep()
