# Next-iteration plan

> **Status:** Preliminary. The [after-action report](retrospective.md) substantially refines the product thesis around source admission, grading, provenance, progressive compilation, and agent-transfer evaluation. Resolve its open decisions and revise this plan before implementation begins.

## Mission

Build a secure, reproducible, local-first media knowledge pipeline that can ingest transcript sources, preserve evidence, generate versioned derived artifacts, search them quickly, and expose a stable dataset to human and agent interfaces.

The first release of the next iteration should prioritize trustworthy foundations over adding more synthesis formats.

## Product principles

1. Local corpus ownership: raw and normalized data remain usable without a hosted service.
2. Evidence preservation: original provider payloads and normalized text are never overwritten by interpretation.
3. Explicit provenance: every derived artifact records its generator, configuration, schema, and inputs.
4. Reproducibility: a fresh environment can install dependencies and run the documented pipeline.
5. Inspectability: heuristic and semantic decisions can be traced back to evidence.
6. Secure defaults: credentials never live in source, logs, fixtures, or generated artifacts.
7. One supported path: experiments may exist, but production commands and schemas are unambiguous.

## Proposed target architecture

```text
config/
  channels.yaml
  taxonomies/
src/ or crates/
  CLI and core Rust library
python/
  pyproject.toml
  media_knowledge/
    taxonomy, synthesis, and publication modules
schemas/
  transcript.schema.json
  tag-record.schema.json
  manifest.schema.json
data/                    # ignored by default
  raw/
  normalized/
  derived/
fixtures/                # small, synthetic, tracked corpus
web/
  visualizer
docs/
```

The exact language split is an implementation decision, but both languages should consume the same versioned schemas and configuration.

## Phase 0: Secure the checkpoint

Goal: make the current repository safe to continue using.

- Revoke and rotate both committed transcript-provider credentials.
- Remove credentials from source and load them from environment variables.
- Decide whether Git history must be rewritten based on repository exposure.
- Add secret scanning to local checks and CI.
- Document which commands spend provider credits and require confirmation.

Acceptance criteria:

- Repository-wide secret scan passes.
- Ingestion fails with a clear message when credentials are absent.
- Tests use fake providers and cannot make paid calls.

## Phase 1: Reproducible development environment

Goal: make setup deterministic on a new machine.

- Declare supported Rust, Python, and Node versions.
- Add `pyproject.toml` with locked Python dependencies.
- Track the visualizer lockfile and declare its Node engine.
- Add one bootstrap or task-runner interface for common commands.
- Replace workstation-specific absolute paths with a configurable project/data root.
- Add CI for Rust tests, Python tests/linting, and visualizer checks/builds.

Acceptance criteria:

- A clean checkout can install, test, and build from documented commands.
- No source file contains the original workstation path.
- CI performs no paid or external ingestion calls.

## Phase 2: Stabilize the data model

Goal: turn the normalized transcript format into an explicit contract.

- Define a versioned transcript schema.
- Store canonical numeric duration and publication timestamps where available.
- Retain provider display strings only as optional source metadata.
- Define whether offsets are Unicode scalar, byte, or grapheme positions.
- Create fixtures for segment-list, SRT, missing-duration, Unicode, and malformed inputs.
- Consolidate Rust and Python normalization behavior or test both against shared fixtures.
- Add an atomic-write strategy so interrupted ingestion cannot leave partial records.

Acceptance criteria:

- Every normalized fixture validates against the schema.
- Rust and Python produce equivalent normalized output for shared inputs.
- Search timestamp resolution is covered by boundary and Unicode tests.

## Phase 3: Consolidate the CLI

Goal: provide one reliable user-facing command.

Suggested command surface:

```text
media-knowledge ingest video <id-or-url>
media-knowledge ingest channel <handle>
media-knowledge ingest queue <file>
media-knowledge normalize [paths...]
media-knowledge search <query>
media-knowledge stats
media-knowledge validate
media-knowledge build tags
```

Work items:

- Fix conflicting flags and add CLI parsing tests.
- Remove or absorb duplicate binaries and creator-specific code.
- Return nonzero status when downloads fail.
- Record per-item failure reasons in batch summaries.
- Add dry-run planning for billable channel and queue ingestion.
- Make provider selection and retry behavior configurable.

Acceptance criteria:

- Help and every subcommand parse in tests.
- Offline commands never require credentials.
- Billable commands show an exact plan before execution unless explicitly approved.

## Phase 4: Rebuild one derived pipeline

Goal: establish a reproducible template for all later knowledge artifacts.

Start with the existing three-tier tag silo because it has both data and a working consumer.

- Move channel and ontology definitions from Python constants into versioned configuration.
- Separate tag detection from output serialization.
- Add schema validation for per-video records, channel indexes, and the graph manifest.
- Record input corpus fingerprint, configuration version, and generator version.
- Generate the visualizer manifest once into a build directory.
- Evaluate precision and recall on a small hand-reviewed sample.
- Label heuristic matches as heuristic evidence.

Acceptance criteria:

- One command rebuilds the demo tag silo from tracked fixtures.
- Repeated builds are deterministic aside from explicitly excluded timestamps.
- The visualizer consumes one canonical generated manifest.
- Quality metrics are reported against the reviewed sample.

## Phase 5: Restore consumption surfaces

Goal: reconnect interfaces only after artifact contracts are stable.

### Visualizer

- Preserve graph, ontology, matrix, filtering, and static deployment.
- Derive channel metadata from the manifest instead of duplicating it in Svelte.
- Add empty, loading, and invalid-manifest states.
- Replace checkout-mutating deployment with CI or a dedicated worktree.

### Search

- Keep filesystem search for portability.
- Benchmark whether an optional SQLite FTS index materially improves startup or query latency.
- Support multiple matches per transcript with configurable context.

### REST/MCP

- Build both on a shared artifact repository abstraction.
- Validate artifacts at startup.
- Return provenance with results.
- Decide whether both interfaces are necessary; do not maintain two divergent readers by default.

Acceptance criteria:

- Every interface reads the same configured artifact root.
- Contract tests verify consistent core and graph results.
- Missing or incompatible artifacts produce actionable errors.

## Phase 6: Reintroduce advanced synthesis deliberately

Promote experiments one at a time based on a concrete use case:

- Creator codices.
- Knowledge cores.
- Cross-creator consensus.
- Speech dynamics.
- Reports and PDFs.
- Agent retrieval and fine-tuning exports.

Each promoted stage must declare:

- Evidence inputs.
- Algorithm/model and version.
- Authored templates or editorial assumptions.
- Output schema.
- Evaluation method.
- Cost and privacy implications.

## Initial backlog

### Must do first

- Rotate exposed credentials.
- Add environment-based configuration.
- Fix the CLI search flag collision.
- Add minimal Rust unit and CLI parsing tests.
- Add Python and Node dependency/runtime declarations.
- Replace absolute paths in supported scripts.

### Then do

- Version the transcript schema.
- Create a small synthetic fixture corpus.
- Move taxonomy configuration out of Python code.
- Unify artifact-root handling.
- Add CI and generated-artifact validation.
- Remove manifest duplication.

### Later

- Search index benchmarking.
- Semantic tagger experiments.
- REST/MCP product decision.
- Report pipeline portability.
- External corpus storage/versioning strategy.

## Open decisions

These should be resolved before substantial implementation:

1. Is the primary product a personal CLI, a reusable library, or a hosted/local application?
2. Is the corpus expected to remain single-user and local?
3. Which generated artifacts deserve version control versus rebuild-on-demand storage?
4. Should Rust own all normalization, or should normalization become a language-neutral contract with multiple implementations?
5. Is deterministic lexical tagging a supported feature, a baseline, or only a prototype?
6. Does the next iteration need both REST and MCP immediately?
7. What evidence/provenance standard is required for generated psychological or technical guidance?

## Definition of the first next-iteration milestone

The first milestone is complete when a fresh checkout can:

1. Install pinned dependencies.
2. Validate a small tracked fixture corpus.
3. Search it and produce correct timestamp links.
4. Rebuild a deterministic tag manifest.
5. Build the visualizer against that manifest.
6. Pass all checks without network access or secrets.

That milestone creates a trustworthy base for importing the full local corpus and reintroducing advanced synthesis.
