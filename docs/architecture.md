# Architecture and data contracts

This document describes the repository as it exists at the September 20, 2026 retrospective checkpoint. It distinguishes operational paths from experiments and checked-in artifacts from local data.

## 1. System boundaries

The project has four conceptual layers:

```text
Acquisition        Normalization        Knowledge builds        Consumption
-----------        -------------        ----------------        -----------
YouTube IDs   ->   archive JSON    ->   tag silos          ->   Rust search
Channel feed       transcript YAML      creator codices         Svelte/D3 UI
Transcript APIs                         knowledge cores          REST prototype
                                        reports/graphs           MCP prototype
```

Only the acquisition and normalization stages are implemented as a compiled application. Knowledge builds are independent scripts, and the consumption layer reads their generated files directly.

## 2. Acquisition and normalization

### Entry points

`src/main.rs` defines five CLI operations:

- `channel`: resolves a channel, scans recent uploads, ranks candidates, and downloads a credit-limited selection.
- `download`: ingests one video ID or URL.
- `batch`: ingests a JSON queue with a Rayon thread pool.
- `search`: searches normalized YAML files and constructs timestamped YouTube links.
- `status`: counts transcripts, words, and channels.

There are also two separate binaries:

- `src/bin/search_transcripts.rs`: an earlier standalone parallel search implementation.
- `src/bin/ingest_defranco_curated.rs`: a creator-specific ingestion utility.

These overlapping entry points reflect prototype evolution. The next iteration should converge on one supported CLI.

### Provider behavior

`src/lib.rs` uses a blocking HTTP client and attempts providers in order:

1. TranscriptAPI.
2. Supadata as a fallback.

There is intentionally no local scraping fallback. This reduces IP blocking risk but means ingestion is network-dependent, authenticated, and potentially billable.

### Channel selection heuristic

`src/heuristic.rs` computes a Transcript Value Heuristic from:

- Duration, favoring substantial videos.
- Relative recency extracted from display text.
- Title keywords such as “explained,” “architecture,” “analysis,” and “tutorial.”
- An optional title substring filter.

The heuristic is useful for prioritization but is not a learned relevance score. Relative dates and human-readable duration fields come from the upstream provider, so they should be considered presentation data rather than durable metadata.

## 3. Canonical transcript contracts

### Raw archive JSON

New Rust ingestion writes `downloaded_transcripts/step_manual_<video_id>.json` with this shape:

```json
{
  "video_id": "string",
  "title": "string",
  "channel": "string",
  "handle": "string",
  "url": "https://www.youtube.com/watch?v=...",
  "duration": "MM:SS or HH:MM:SS",
  "word_count": 1234,
  "published": "string",
  "raw_segments": [
    { "text": "string", "start": 0.0, "duration": 2.1 }
  ],
  "topics": []
}
```

Older local archives contain additional provider and enrichment shapes. `scripts/reformat_transcripts_to_yaml.py` is deliberately tolerant of segment lists, SRT payloads, embedded transcript strings, and alternate metadata names.

### Normalized transcript YAML

`formatted_transcripts/step_manual_<video_id>.yaml` is the closest thing the project has to a canonical internal schema:

```yaml
video_id: abc123def45
title: Example title
channel: Example channel
handle: '@example'
url: https://www.youtube.com/watch?v=abc123def45
duration: '42:10'
published: 'optional provider value'
type: video
transcript: Full normalized transcript text...
timestamps: [[0, 0], [83, 4], [151, 9]]
```

Each timestamp pair is `[character_offset, playback_seconds]`. Search finds the last pair whose character offset is not greater than the match position. This compact representation is worth retaining.

Current schema weaknesses:

- No explicit schema version.
- Publication values may be absolute dates or relative phrases.
- Duration is formatted text rather than a numeric canonical value.
- The Rust and Python serializers are separate implementations.
- Character offsets assume consistent string handling across producers and consumers.

## 4. Three-tier tag silo

`scripts/build_channel_tag_silo.py` performs a single scan of normalized transcript files for six configured channels:

- HealthyGamerGG
- TheraminTrees
- ThePrimeagen
- Web Dev Simplified
- freeCodeCamp.org
- A Life Engineered

The compiler contains two main in-code taxonomies:

- Second-order channel lexicons: channel-specific domains and concept keyword lists.
- Third-order ontology: global concepts and mappings to second-order tags.

For each matched transcript it:

1. Finds lexicon terms in the transcript.
2. Produces timestamped first-order activations.
3. Assigns second-order and third-order tags.
4. Extracts frequent phrases.
5. Writes a per-video YAML record.
6. Updates channel counts and an inverted tag index.

Generated artifacts are:

```text
tag_silo/
  third_order_unbound_tags.yaml
  tag_hierarchy_manifest.json
  <channel>/
    channel_taxonomy.yaml
    inverted_tag_index.json
    videos/<video_id>.yaml
```

The graph manifest includes all third- and second-order nodes but samples only the twelve longest video records per channel as first-order nodes. Consequently, “videos analyzed” and “video nodes displayed” intentionally differ.

## 5. Other knowledge-build paths

The repository includes several partially overlapping synthesis generations.

### Creator codices

`scripts/build_creator_master_codex.py` groups transcript archives by creator and emits a channel-level codex. Some conceptual summaries and playbooks are hand-authored templates selected by channel name; they are not purely inferred from the corpus.

### Knowledge cores

`scripts/build_knowledge_cores.py` groups channels into six broad domains, including software engineering, psychology, business, science, cybersecurity, and Pāli philosophy. It aggregates enriched transcript summaries into core archives and a registry.

### Reports

`scripts/generate_core_compendium.py` combines cores and creator codices into Markdown and HTML, then invokes a machine-specific Chrome binary to create a PDF. Significant prose in the current compendium generator is fixed editorial content.

### Experimental research

`scratch/` includes scripts for:

- Transcript cleanup and title resolution.
- Speech dynamics and pause analysis.
- Paragraph and essay reconstruction.
- Video summarization and fine-tuning datasets.
- Knowledge graphs and cross-creator synthesis.
- Task-to-core recommendation.
- Visualization generation and channel intelligence dashboards.

These scripts preserve useful research ideas, but many reference obsolete filenames, absolute paths, or external working directories. Treat them as a design archive until individually promoted and tested.

## 6. Consumption surfaces

### Rust search

Search loads every normalized YAML document in parallel, applies optional channel/type filters, finds a match, resolves the nearest timestamp, and prints a YouTube jump URL. It currently returns at most one match per transcript.

### Svelte/D3 visualizer

`visualizer/src/routes/+page.svelte` imports the graph manifest at build time. It provides:

- A filterable force-directed graph.
- A global ontology directory.
- A channel comparison matrix.
- Core, channel, tier, and text filters.

The application is statically rendered for GitHub Pages. `scripts/deploy_gh_pages.sh` builds the site, switches branches, replaces the published files, commits, and pushes. Because that script mutates the checkout and remote state, it should eventually be replaced with CI deployment or a worktree-based process.

### REST prototype

`scripts/knowledge_api_server.py` exposes file-backed endpoints for codices, cores, fusion, recommendation, audits, search, consensus, graph triples, personas, and channel catalogs.

### MCP prototype

`scripts/mcp_knowledge_server.js` implements three JSON-RPC tools:

- `list_knowledge_cores`
- `load_knowledge_core`
- `query_knowledge_graph`

Both servers use absolute repository paths and expect generated files at the repository root. Most corresponding artifacts now live in `data/core_archives`, `data/channel_codices`, or `data/collected_data`, so these services are currently disconnected from the present layout.

## 7. Source and artifact ownership

The current repository mixes four categories:

| Category | Examples | Desired next-iteration policy |
| --- | --- | --- |
| Product source | Rust CLI, reusable Python package, visualizer | Tracked and tested |
| Configuration | Provider settings, taxonomies, channel definitions | Tracked, declarative, reviewed |
| Reproducible output | Manifest, compact demo corpus | Generated in CI or checked with provenance |
| Personal/local corpus | Raw transcripts, enriched archives, large datasets | Ignored, versioned externally if needed |

The next iteration should make those boundaries visible in both directory structure and commands.

## 8. Known operational gaps

- Two credentials are committed in Rust source and must be rotated.
- The documented `.env` file is not loaded by the Rust application.
- The primary search command has conflicting short flags.
- There is no automated test coverage.
- Python dependencies and supported Python version are unspecified.
- The visualizer does not declare a Node engine and has no tracked lockfile.
- Several scripts are tied to one absolute filesystem path.
- Generated artifacts lack provenance, schema versions, and input hashes.
- REST/MCP readers disagree with the present `data/` layout.
- Errors during individual batch downloads are counted but discarded.

These gaps define the starting backlog rather than diminishing the prototype’s successful proof of concept.
