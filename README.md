# 🎬 YouTube Knowledge Extractor & Archival Publication System

A high-performance Rust and Python knowledge extraction, synthesis, and publication pipeline that converts long-form spoken video essays and technical lectures into high-density reference books, Markdown manuals, 3-tier tag silos, Model Context Protocol (MCP) data substrates, and interactive web visualizers.

---

## ⚡ High-Performance Rust CLI Downloader (`youtube-extractor`)

A compiled, multi-threaded Rust CLI equipped with **dynamic worker allocation** (`--workers N`) and **real-time ETA & throughput predictions**:

```bash
# Build the optimized release binary
cargo build --release

# 1. Download and format a single YouTube video transcript
./target/release/youtube-extractor download "https://www.youtube.com/watch?v=LyTpZ327ixY" --channel "Philip DeFranco"

# 2. Batch download transcripts from a queue file with dynamic workers & live ETA
./target/release/youtube-extractor batch queue.json --workers 8 --skip-existing

# 3. Sub-second parallel search across all 1,760+ YAML transcripts with jump URLs
./target/release/youtube-extractor search "cognitive dissonance" --limit 5

# 4. View library statistics (transcripts, words, channel rankings)
./target/release/youtube-extractor status
```

---

## 🏷️ 3-Tier Tagging Hierarchy Architecture

The repository enforces a clean separation of raw data from a bottom-up tagging layer:
- **1st-Order Tags (Video-Bound):** Timestamped concept anchors within individual video transcripts.
- **2nd-Order Tags (Channel-Bound):** Channel-level thematic pillars and signature vocabulary isolated to each creator's domain (e.g., `tag_silo/healthygamergg/channel_taxonomy.yaml` and `tag_silo/theramintrees/channel_taxonomy.yaml`).
- **3rd-Order Tags (Global Unbound):** Universal cross-cutting psychological and philosophical ontologies with no single-channel bounds (`tag_silo/third_order_unbound_tags.yaml`).

```bash
# Query the tag silos from the terminal
python3 scripts/query_tag_silo.py --stats
python3 scripts/query_tag_silo.py --channel healthygamergg --tag samskara
python3 scripts/query_tag_silo.py --channel theramintrees --tag double_bind
```

---

## 🌐 Interactive SvelteKit + D3.js Visualizer (`visualizer/`)

An interactive Single-Page Application (SPA) designed for static deployment on **GitHub Pages**:
- **D3 Force-Directed Network Graph:** Visualizes 1st, 2nd, and 3rd order relations with dynamic physics, zoom/pan, and search.
- **Pillar Comparison Matrix:** Side-by-side comparative analysis of creator channels.
- **Global Ontology Directory:** Interactive index of unbound concepts.

```bash
cd visualizer
npm install
npm run dev     # Launch local preview at http://localhost:5173
npm run build   # Generate pure static site in visualizer/build/
```

---

## 📂 Project Structure

```
youtube-extractor/
├── src/                                  # High-Performance Rust Engine
│   ├── main.rs                           # Primary CLI (download, batch, search, status)
│   ├── lib.rs                            # Transcript formatters, parsers & serialization
│   └── bin/search_transcripts.rs         # Standalone parallel search binary
├── scripts/                              # Core Python & Node pipeline tools
│   ├── build_channel_tag_silo.py         # 3-Tier Tag Silo Compiler
│   ├── query_tag_silo.py                 # Tag Silo Terminal Inspector
│   ├── reformat_transcripts_to_yaml.py   # YAML formatter
│   └── mcp_knowledge_server.js           # MCP RPC Server
├── scratch/                              # Experimental agent scripts & workspaces
├── data/                                 # Collected datasets, archives & codices (gitignored)
├── formatted_transcripts/                # Local clean YAML transcripts (gitignored)
├── downloaded_transcripts/               # Local raw archive JSONs (gitignored)
├── tag_silo/                             # 3-Tier Tag Silo Layer
│   ├── third_order_unbound_tags.yaml     # 3rd-Order global unbound ontologies
│   ├── tag_hierarchy_manifest.json       # Graph manifest for D3.js SPA
│   ├── healthygamergg/                   # HealthyGamerGG 2nd-order pillars & 1st-order records
│   └── theramintrees/                    # TheraminTrees 2nd-order pillars & 1st-order records
├── visualizer/                           # SvelteKit + D3.js Static Visualizer SPA
├── reports/                              # Compiled publication PDFs & Markdown compendiums
├── taxonomy/                             # Cross-channel creator profiles & speech dynamics
├── .env.example                          # Environment configuration template
└── Cargo.toml                            # Rust package and workspace configuration
```

---

## 🔐 Environment Setup

Copy `.env.example` to `.env` to configure external API tokens if using optional third-party integrations:
```bash
cp .env.example .env
```
*(No tokens are required for direct transcript downloads or offline search).*

