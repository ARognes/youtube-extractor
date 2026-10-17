# YouTube Knowledge Extractor

YouTube Knowledge Extractor is a local-first pipeline for turning long-form YouTube transcripts into searchable archives, channel taxonomies, cross-channel knowledge structures, reports, and an interactive graph.

The repository contains three related systems:

1. A Rust CLI for transcript ingestion, normalization, search, and corpus statistics.
2. Python and Node scripts for tagging, synthesis, publication, and knowledge-serving experiments.
3. A SvelteKit and D3 visualizer for the checked-in three-tier tag silo.

The project began as a working prototype and accumulated several generations of output and experimental tooling. Before extending it, read [the architecture guide](docs/architecture.md), [the after-action report](docs/retrospective.md), and [the preliminary next-iteration plan](docs/next-iteration.md).

## Current snapshot

As of September 20, 2026, the local workspace contains:

- 1,849 raw transcript archives and 1,849 normalized transcript files.
- Approximately 6.9 million spoken words from 184 channel labels.
- A checked-in tag silo covering 485 videos from six selected channels.
- A visualizer manifest with 209 nodes, 294 links, and 11 global concepts.

The raw corpus and most derived archives are intentionally ignored by Git. The curated tag-silo records and visualizer manifest are tracked.

## Core workflow

```text
YouTube video or channel
    -> authenticated transcript provider
    -> downloaded_transcripts/*.json
    -> formatted_transcripts/*.yaml
    -> tag/synthesis scripts
    -> tag_silo/, data/, taxonomy/, reports/
    -> visualizer or local knowledge service
```

The normalized transcript YAML is the most important internal contract. It stores video metadata, the complete transcript, and pairs of character offsets and playback seconds. Search can therefore return a text match with a timestamped YouTube URL without storing one record per caption.

## Repository map

| Path | Role | Git policy |
| --- | --- | --- |
| `src/` | Rust ingestion, normalization, search, and status CLI | Tracked source |
| `scripts/` | Repeatable Python/Node build and serving scripts | Tracked source |
| `scratch/` | One-off research, migration, and synthesis experiments | Tracked prototypes |
| `downloaded_transcripts/` | Raw transcript/provider archives | Local, ignored |
| `formatted_transcripts/` | Normalized searchable YAML corpus | Local, ignored |
| `tag_silo/` | Curated first-, second-, and third-order tag outputs | Tracked artifacts |
| `taxonomy/` | Cross-channel metadata and taxonomy indexes | Tracked artifacts |
| `data/` | Codices, core archives, and research datasets | Local, ignored |
| `reports/` | Generated Markdown, HTML, and PDF publications | Tracked selectively |
| `visualizer/` | SvelteKit/D3 static application | Tracked source and manifest |

## Rust CLI

Build the CLI with:

```bash
cargo build --release
```

The intended commands are:

```bash
./target/release/youtube-extractor status

./target/release/youtube-extractor download VIDEO_OR_URL \
  --channel "Channel Name" \
  --title "Video title"

./target/release/youtube-extractor channel @ChannelHandle \
  --credits 25 \
  --min-duration 5m

./target/release/youtube-extractor batch queue.json \
  --workers 8 \
  --skip-existing

./target/release/youtube-extractor search "cognitive dissonance" --limit 5
```

Important current limitation: the primary `search` subcommand panics because two search filters are assigned the same `-c` short option. The standalone `search_transcripts` binary is also present, but the conflict should be fixed before treating the CLI as stable.

## Tag-silo pipeline

The three-tier model is:

- First order: timestamped concept occurrences attached to a video.
- Second order: channel-specific concepts and thematic pillars.
- Third order: cross-channel concepts that connect multiple domains.

The compiler currently analyzes six channels across psychology and software engineering:

```bash
python3 scripts/build_channel_tag_silo.py
python3 scripts/query_tag_silo.py --stats
python3 scripts/query_tag_silo.py --channel healthygamergg --tag samskara
```

This is a deterministic lexicon and phrase-frequency system, not a semantic embedding or language-model classifier. Its outputs are useful as inspectable prototype data, but tag quality should not be interpreted as independently validated ground truth.

Python dependencies are not yet captured in a lockfile or package manifest. At minimum, the tag tools require PyYAML.

## Visualizer

The visualizer is a static SvelteKit application with a D3 force graph, ontology browser, and channel comparison matrix.

```bash
cd visualizer
npm install
npm run check
npm run dev
npm run build
```

Use a modern Node release compatible with the versions in `visualizer/package.json`. The Node 16 runtime in the original development environment is too old for the installed Svelte/Vite toolchain.

The tag compiler writes the same graph manifest to:

- `tag_silo/tag_hierarchy_manifest.json`
- `visualizer/src/lib/tag_hierarchy_manifest.json`
- `visualizer/static/tag_hierarchy_manifest.json`

These copies should remain byte-identical until the next iteration replaces duplication with a single explicit build input.

## Credentials and network access

Transcript ingestion uses authenticated third-party APIs and consumes provider credits. It should never be presented as credential-free.

The current Rust library contains tracked, hard-coded credentials. Treat them as compromised: revoke or rotate them before further use. The next iteration should read `TRANSCRIPT_API_KEY` and `SUPADATA_API_KEY` from the environment, fail clearly when they are absent, and prevent secrets from entering source control.

Do not test download or channel-ingestion commands until that cleanup is complete.

## Verification status

At the retrospective checkpoint:

- `cargo test --all-targets` compiles successfully.
- The Rust project contains no automated tests.
- `youtube-extractor status` successfully reads the local corpus.
- The main `search` subcommand fails during argument validation.
- Python tag commands fail in a bare environment without PyYAML.
- The visualizer check/build fails on Node 16 and needs a newer runtime.
- The REST and MCP prototypes reference obsolete root-level artifact paths.

These are documented starting conditions for the next iteration, not hidden setup assumptions.

## Project documentation

- [Architecture and data contracts](docs/architecture.md)
- [After-action report and revised product thesis](docs/retrospective.md)
- [Preliminary next-iteration plan](docs/next-iteration.md)
