# Prototype retrospective

## Executive summary

The prototype proved that a personal long-form video library can be acquired, normalized, searched, organized into inspectable taxonomies, and published as an interactive knowledge graph. It also grew faster than its contracts and operational boundaries.

The right next step is not to discard the work. It is to preserve the corpus, transcript schema, timestamp-search technique, taxonomy concepts, and visual exploration while rebuilding the pipeline around explicit configuration, reproducible stages, secure credentials, and tests.

This retrospective describes the state observed on September 20, 2026.

## Timeline

The tracked history consists of five commits over one week:

1. September 5: initial Rust CLI, psychology-oriented tag silos, and static visualizer.
2. September 5: one-command GitHub Pages deployment.
3. September 11: expansion to a software-engineering core and four additional channels.
4. September 11: Svelte 5 and static-path fixes.
5. September 11: `.nojekyll` deployment fix.

That pace explains both the impressive breadth and the architectural drift. The project validated many ideas before pausing to define a stable product boundary.

## What worked well

### A real corpus was created

The most important accomplishment is not the UI; it is the data acquisition. The local corpus contains 1,849 transcript archives representing roughly 6.9 million words. This provides enough volume to reveal real scaling and data-quality issues that a toy sample would miss.

### The normalized transcript format is efficient

Storing one transcript string plus `[character_offset, seconds]` pairs supports compact archival storage and timestamped search. It avoids duplicating metadata for every caption segment and remains human-readable in YAML.

### The project reached end-to-end usefulness

The prototype demonstrated:

- Authenticated transcript acquisition.
- Concurrent batch processing.
- Offline corpus statistics and search.
- Per-video and per-channel tag artifacts.
- Cross-channel ontology links.
- Static visualization and deployment.
- Publication and agent-facing serving experiments.

That breadth clarified which product directions are promising.

### The tag hierarchy is explainable

Lexicon matching is limited, but every tag can be traced to configured terms and transcript contexts. For an early taxonomy system, that inspectability is valuable. It gives the next iteration a baseline against which semantic approaches can be evaluated.

### The repository preserves research trails

The scripts in `scratch/` document many explored directions: speech dynamics, summaries, creator personas, fine-tuning records, knowledge graphs, and cross-creator synthesis. Even where they are not production-ready, they prevent rediscovery of prior experiments.

## What did not scale

### Paths became the integration mechanism

Independent scripts communicate by assuming exact filenames and absolute directories. As files moved into `data/`, the REST and MCP servers continued reading the repository root. This is the clearest example of missing shared configuration and artifact contracts.

### Source, configuration, and generated data became interleaved

Large generated tag outputs are tracked beside source code, while other equally important generated artifacts are ignored. Taxonomies are embedded in Python code, visualizer metadata is partly duplicated in Svelte, and the same graph manifest exists in three locations.

The result works locally but makes ownership unclear:

- Which files are edited by hand?
- Which files are authoritative?
- Which files should be regenerated?
- Which input corpus produced a checked-in output?

### Experiments were promoted implicitly

Some outputs look analytical but originate partly from fixed templates. Creator codices and report chapters include hand-authored principles, playbooks, and editorial prose selected by channel. Those can be valuable, but provenance is essential. A consumer should be able to distinguish transcript-derived facts, heuristic classifications, and authored interpretation.

### Environment assumptions were not captured

The project has Rust and Node manifests but no Python dependency manifest, no supported runtime matrix, and no Node engine declaration. Machine-specific Chrome and Node paths appear in scripts. This made an otherwise healthy visualizer impossible to verify under the current default Node runtime.

### Validation lagged feature growth

The Rust project compiles, but it has zero tests. A duplicate short option made the documented search command panic despite successful compilation. There are no schema fixtures, pipeline smoke tests, or checks that the three visualizer manifests remain synchronized.

### Security was treated as a convenience

Provider credentials were embedded in tracked Rust source even though `.env.example` suggests environment-based configuration. This is the most urgent defect because source history must be treated as public once pushed. Rotation is required; merely deleting the current lines is insufficient.

### Some runtime failures are too quiet

Batch ingestion counts failures without reporting their causes. Python scripts frequently catch broad exceptions and continue. That keeps long jobs moving but makes partial or stale output difficult to diagnose.

## Verification findings

The retrospective used read-only or local build checks where possible:

| Check | Result |
| --- | --- |
| Git worktree before documentation | Clean and aligned with `origin/main` |
| `cargo test --all-targets` | Compiled; 0 tests executed |
| `youtube-extractor status` | Successful; 1,849 transcripts and 6,936,413 words |
| Main CLI `search` | Panic from duplicate `-c` flags |
| `python3 scripts/query_tag_silo.py --stats` | Missing `yaml` module |
| `npm run check` | Failed under Node 16 due to newer toolchain API requirements |
| Manifest copies | The three current copies are byte-identical |

No paid transcript calls were made.

## Decisions worth preserving

- Keep raw provider responses separate from normalized transcripts.
- Keep offline search available without a database.
- Keep timestamped jump URLs as a first-class feature.
- Keep taxonomies inspectable and exportable.
- Keep the visualizer deployable as a static site.
- Keep the personal corpus out of normal Git history.
- Keep experimental work separate from supported commands.

## Decisions to revisit

- Blocking HTTP plus Rayon is workable but not necessarily the simplest long-term ingestion model.
- YAML is excellent for inspection but may not be the best search/index substrate at larger scale.
- In-code taxonomies make iteration easy but obscure configuration ownership.
- Checking hundreds of generated per-video tag files into Git creates noisy diffs.
- A server that directly opens arbitrary artifact files is expedient but lacks schema validation and lifecycle management.
- A deployment script that switches branches and pushes from the working checkout is risky.

## Core lessons

### Establish contracts before adding representations

The repository now has raw transcripts, normalized transcripts, hydrated datasets, essays, codices, cores, taxonomies, graph triples, manifests, reports, and training records. Each can be justified, but every representation should declare:

- Its schema and version.
- Its authoritative inputs.
- Whether it is source or generated output.
- The command that reproduces it.
- Its provenance and quality level.

### Separate evidence from interpretation

Transcript text and timestamps are evidence. Keyword matches and summaries are derived observations. Curated playbooks and synthesis chapters are editorial interpretation. The next system should carry those distinctions in metadata rather than relying on directory names or reader intuition.

### Make the smallest useful pipeline reliable first

The strongest coherent slice is:

```text
ingest -> normalize -> validate -> search
```

The next coherent slice is:

```text
validated transcripts -> configured taxonomy -> inspectable tag output -> visualizer
```

Knowledge cores, reports, embeddings, MCP, and advanced consumers should build on those stable foundations rather than define competing data contracts.

## Recommended disposition

### Preserve as reference

- The local transcript corpus.
- The normalized YAML schema and timestamp mapping idea.
- Existing tag-silo outputs as a regression/demo dataset.
- Taxonomy definitions and channel mappings.
- The visualizer interaction model.
- Experimental scripts as an archive of explored ideas.

### Refactor or replace

- Credential handling.
- Absolute path constants.
- Duplicate CLI binaries and creator-specific ingestion code.
- Artifact discovery in REST/MCP servers.
- In-code generated prose presented without provenance.
- Manual manifest copying.
- Branch-switching deployment scripts.

### Do not carry forward by default

- Assumptions that a particular workstation path, Chrome installation, or Node installation exists.
- Silent exception handling for production stages.
- Root-level artifact naming conventions that conflict with `data/` organization.
- Claims that direct transcript download requires no credentials.

## Closing assessment

This was a successful exploratory build. It answered the key feasibility question: a large personal YouTube corpus can become a searchable and navigable knowledge substrate with modest infrastructure. The prototype’s debt is mainly integration debt, not evidence that the idea failed.

The next iteration should be narrower at first, with explicit contracts and provenance. Once ingestion, validation, search, and one taxonomy build are reproducible, the more ambitious synthesis work can return on a much stronger base.
