# 🎬 YouTube Knowledge Extractor & Archival Publication System

An autonomous, multi-creator knowledge extraction, synthesis, and publication pipeline that converts long-form spoken video essays and technical lectures into high-density reference books, Markdown manuals, and Model Context Protocol (MCP) data substrates.

---

## 📂 Project Structure

```
~/Documents/Projects/media-extractor/youtube-extractor/
├── downloaded_transcripts/               # 1,740 raw, verified transcript JSON files (182 creator channels)
├── reports/                              # Compiled publication PDFs, companion Markdown manuals & HTML layouts
│   ├── core_cognitive_psychology_compendium.pdf
│   ├── core_cognitive_psychology_compendium.md
│   └── core_cognitive_psychology_compendium.html
├── knowledge_cores_registry.json         # 6 MACE Domain Core registry manifest
├── core_*_master_archive.json            # Domain-specific Master Archives
├── *_master_codex.json & .md             # Single-file Creator Master Codices
├── knowledge_graph_triples.json & .csv   # 5,641 extracted Semantic Graph Triples
├── creator_instruct.jsonl                # 1,118 Fine-tuning Instruction training pairs
├── creator_personas.json                 # 183 System prompt creator personas
├── generate_core_compendium.py           # Publication PDF/Markdown compilation engine
├── build_knowledge_cores.py              # Modular Archival Core Engine (MACE) compiler
├── build_creator_master_codex.py         # Creator Master Codex synthesizer
├── build_knowledge_graph.py              # Semantic graph extractor
├── build_fine_tuning_dataset.py          # Instruction-tuning & persona dataset exporter
├── build_cross_creator_synthesis.py      # Cross-creator consensus & divergence matrix
└── mcp_knowledge_server.js               # Model Context Protocol RPC Server
```

---

## 🚀 Quickstart & Usage

### 1. Generate Domain Compendium Books (PDF + Markdown)
Compile publication-grade PDF reference books and companion Markdown manuals for any domain core:

```bash
# Cognitive Psychology (TheraminTrees, HealthyGamerGG, JulienHimself)
python3 generate_core_compendium.py --core core_cognitive_psychology

# Business & Offer Scaling (Alex Hormozi, Tim Ferriss)
python3 generate_core_compendium.py --core core_business_monetization

# Software Engineering (ThePrimeagen, Web Dev Simplified, freeCodeCamp)
python3 generate_core_compendium.py --core core_software_engineering

# Cybersecurity & Homelabs (NetworkChuck, Seytonic)
python3 generate_core_compendium.py --core core_cybersecurity_homelab

# Early Buddhist Philosophy (Doug's Dharma)
python3 generate_core_compendium.py --core core_pali_philosophy

# Science & Classical Physics (Sabine Hossenfelder, Academy of Ideas)
python3 generate_core_compendium.py --core core_science_philosophy
```

### 2. Synthesize Individual Creator Codices
Synthesize a single comprehensive codex for any specific creator channel:
```bash
python3 -c "
from build_creator_master_codex import build_master_codex_for_channel
build_master_codex_for_channel('TheraminTrees', '.')
"
```

### 3. Connect to MCP Clients (Claude Desktop, Cursor, Antigravity)
Launch the Model Context Protocol stdio server to expose all 6 Archival Cores and 5,600+ knowledge graph triples as native AI tools:
```bash
node mcp_knowledge_server.js
```
