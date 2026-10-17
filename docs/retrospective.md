# After-action report: from transcript extractor to knowledge-core compiler

## Purpose of this report

This report re-evaluates the project at the end of its first prototype cycle. It is intentionally broader than a code retrospective. The central questions are no longer only whether transcripts can be downloaded, searched, and tagged. They are:

- What is a knowledge core?
- What makes source material worthy of admission?
- What epistemic guarantees should a core provide?
- How should broad knowledge be compressed without stripping away the context that makes it reliable?
- Where do YouTube, supplementary research, archives, skills, and agent-facing packages begin and end?
- How will we know that a compiled core actually improves an agent’s understanding?

This report describes the state observed on September 20, 2026 and establishes a more precise product thesis for the next iteration.

## Executive conclusion

The prototype answered its first feasibility question successfully: long-form YouTube material can be acquired at useful scale and relatively low cost, converted into a consistent textual representation, organized into derived structures, and exposed to people and agents.

The larger opportunity is not a YouTube transcript extractor. It is a source-aware knowledge-core compiler.

A knowledge-core compiler accepts well-formed textual evidence, filters it against explicit standards, organizes it into a coherent model of a subject, preserves provenance and uncertainty, and packages the result so an agent can acquire broad subject focus without loading an entire research archive into context.

YouTube should remain the primary discovery and evidence stream in the near term because the project already has a large corpus and because long-form lectures, interviews, tutorials, and essays contain unusually rich explanatory material. Web research should initially play a bounded supporting role: verify claims, resolve ambiguity, supply missing primary sources, update unstable facts, and fill genuine gaps. It should not silently expand the scope or overwhelm the selected media corpus.

The principal failure of the first iteration was not poor extraction. It was insufficient separation between five different activities:

1. Acquiring content.
2. Judging whether content deserves inclusion.
3. Preserving and indexing evidence.
4. Synthesizing a coherent model.
5. Packaging that model for a particular consumer.

The next iteration should make those stages explicit and refuse to compile a knowledge core until the source set passes a defined quality gate.

## Revised product thesis

### Previous framing

The repository was framed as a YouTube knowledge extractor and archival publication system. That framing encouraged the implementation to treat transcript availability as the main admission criterion and to treat downstream formats—tags, codices, reports, graphs, and agent tools—as parallel products.

### Revised framing

The product is a knowledge-core generator with a YouTube-first acquisition strategy.

Its job is to convert an admissible evidence corpus into a compact, navigable, provenance-preserving representation of a subject. Extraction is an adapter. Search is an evidence-access feature. Visualization is one inspection surface. Reports and agent packages are compiled views. None of those alone defines the product.

### Working mission

> Compile high-quality textual evidence into bounded, versioned knowledge cores that give an agent a coherent and appropriately calibrated understanding of a subject under finite context constraints.

The words in this mission matter:

- **High-quality** means admission is earned through grading, not assumed from availability or popularity.
- **Textual evidence** allows YouTube transcripts, articles, papers, documentation, books, and curated notes to share a pipeline after source-specific normalization.
- **Bounded** means a core declares its scope, depth, exclusions, prerequisites, and temporal cutoff.
- **Versioned** means knowledge can be revised without erasing the reasoning and sources behind an earlier state.
- **Coherent** means the result is more than an unordered collection of excerpts.
- **Calibrated** means consensus, uncertainty, disagreement, and source limitations survive compilation.
- **Finite context** means compression and progressive disclosure are product requirements, not afterthoughts.

## What is a knowledge core?

A knowledge core is a compiled epistemic package for a defined subject. It should help an agent orient itself, reason with the subject’s important concepts, retrieve supporting evidence, identify uncertainty, and know where its understanding stops.

It resembles a university degree in structure, not in social function. A useful core has:

- A defined domain and level.
- Prerequisites.
- Foundational concepts.
- A progression from first principles to advanced topics.
- Multiple perspectives where the field contains disagreement.
- Canonical examples and counterexamples.
- A map of what a competent learner should understand.
- Evidence and references for deeper inspection.
- Some way to evaluate whether the material transferred into usable understanding.

It resembles the personality cores in *Portal* only in the sense that attaching one should create a stable focus and subject lens. It should not override the agent’s general reasoning, impersonate an authority, or convert the biases of a source set into personality. The core supplies an epistemic frame, not an identity.

### A knowledge core is not

- A raw transcript collection.
- A full-text search index.
- A pile of summaries.
- A topic tag graph.
- A static report.
- A prompt that tells an agent how to behave.
- A task-specific skill or workflow.
- A claim of exhaustive or expert-certified knowledge.

Those may be inputs, internal structures, inspection surfaces, or companion artifacts. The core is the compiled model that connects them.

### Relationship to adjacent artifacts

| Artifact | Primary purpose | Relationship to a core |
| --- | --- | --- |
| Source archive | Preserve original evidence | The evidentiary substrate |
| Search index | Locate relevant evidence | A retrieval mechanism |
| Taxonomy/ontology | Name and relate concepts | Part of the organizing model |
| Knowledge graph | Express entities and relationships | One possible structural projection |
| Report or textbook | Support linear human reading | A compiled presentation |
| Skill | Guide an agent through a procedure | May depend on one or more cores |
| Knowledge core | Establish broad subject understanding | The reusable epistemic package |

A skill answers, “How should I perform this task?” A knowledge core answers, “What must I understand to reason competently in this area?”

## What did the first iteration actually prove?

### Proven

- Authenticated transcript acquisition is operational and affordable enough to support a substantial personal corpus.
- The local collection can exceed 1,800 videos and 6.9 million words without requiring a database for basic use.
- A normalized transcript plus character-offset timestamps supports compact storage and useful timestamped search.
- Deterministic channel-specific lexicons can produce inspectable first-, second-, and third-order structures.
- A static graph can expose relationships across hundreds of selected videos.
- The same evidence can feed reports, taxonomies, codices, graphs, and agent-facing experiments.

### Suggested but not proven

- That the current tagged subset represents the best available source material.
- That the generated taxonomies accurately represent each channel or subject.
- That the current “knowledge cores” measurably improve agent reasoning.
- That longer videos are generally better learning sources.
- That source popularity, production quality, or information density predicts epistemic quality.
- That keyword prevalence is a good proxy for conceptual importance.
- That combining many sources automatically creates balanced knowledge.
- That compression has preserved the conditions, exceptions, and disagreements needed for correct use.

### Not attempted systematically

- Formal source grading.
- Claim-level corroboration.
- Coverage analysis against a domain curriculum.
- Redundancy reduction based on marginal information value.
- Evaluation of synthesized claims against source evidence.
- Agent performance tests with and without a core.
- Versioned updates as a field changes.
- Copyright, quotation, and retention policy by source type.

This distinction is important. The prototype established pipeline feasibility, not epistemic fitness.

## The central boundary: archive versus core

The archive and the core should be treated as separate products with different optimization targets.

### The archive optimizes for

- Fidelity.
- Completeness.
- Traceability.
- Durable identifiers.
- Source preservation.
- Retrieval.
- Reprocessing as methods improve.

### The core optimizes for

- Coherence.
- Coverage of the declared scope.
- Appropriate compression.
- Low unnecessary redundancy.
- Conceptual navigation.
- Calibrated confidence.
- Efficient agent assimilation.

The archive should retain information that the core omits. The core should never become the only surviving copy of the evidence from which it was compiled.

This yields a crucial design rule:

> Compilation must be lossy for brevity, but the loss must be reversible through provenance links back to the archive.

## Source acquisition should be open; admission should be strict

The system can accept many textual sources without treating them as equally authoritative or equally useful.

### Near-term source hierarchy

1. **Primary YouTube corpus:** long-form lectures, essays, interviews, demonstrations, and tutorials selected for the target core.
2. **Primary external sources:** official documentation, standards, original research, first-party records, or canonical texts discovered while verifying the media corpus.
3. **Supplementary web research:** reputable secondary sources used to resolve loose ends, clarify terminology, update facts, or cover missing concepts.
4. **Discovery-only material:** search results, aggregators, commentary, and weak sources that may identify leads but should not directly establish compiled claims.

“Primary” here describes the role in this project, not always the conventional historical distinction between primary and secondary literature. Every record should separately identify its actual source type.

### Why keep YouTube primary for now?

- The existing corpus is the project’s strongest asset.
- Spoken explanations often contain intuition, examples, and pedagogical sequencing absent from terse reference material.
- Long-form creators can expose tacit mental models and practical judgment.
- Timestamped media remains available as context beyond the transcript.
- Restricting the initial source hierarchy prevents web research from turning every core into an unbounded crawl.

### Why YouTube cannot be sufficient by itself

- Transcripts lose diagrams, demonstrations, tone, and on-screen qualifications.
- Creator incentives may reward confidence, novelty, controversy, or simplification.
- Citations may be absent or difficult to verify.
- Auto-generated transcripts can corrupt technical vocabulary.
- Older videos may be silently outdated.
- Repetition across creators can mimic consensus when sources share the same upstream idea.
- Excellent pedagogy and reliable evidence are related but distinct qualities.

Supplementary research is therefore not ornamental. It is the corrective mechanism that closes evidentiary gaps while remaining subordinate to a declared core scope.

## The source-admission problem

The most important missing subsystem is not another summarizer. It is a grading and admission process.

“Optimal material” is not an intrinsic label. A source is optimal relative to:

- The core’s declared scope.
- The learner/agent’s assumed starting knowledge.
- Gaps already present in the admitted corpus.
- The source’s marginal contribution after redundancy.
- The type of claim being supported.
- The core’s temporal and risk requirements.

A brilliant introductory lecture may be low-value in an advanced core. A dry standards document may be poor pedagogy but indispensable evidence. A speculative interview may be useful for mapping a controversy but unsuitable for establishing settled facts.

### Two-stage grading model

The system should separate cheap triage from expensive deep review.

#### Stage 1: acquisition triage

The purpose is to reject obviously unsuitable material before paying the full cost of transcription, analysis, or research.

Signals may include:

- Title and description relevance.
- Creator/channel prior quality.
- Duration and content type.
- Availability of transcript or captions.
- Language and audio/transcript quality.
- Obvious duplication or reposting.
- Sponsorship or promotional density.
- Publication date where freshness matters.
- Presence of references, chapters, demonstrations, or supporting material.

Stage 1 should produce `reject`, `hold`, or `transcribe/analyze`; it should not assign epistemic authority.

#### Stage 2: content grading

After normalization, grade the actual material rather than its metadata. A provisional 100-point rubric follows.

| Dimension | Weight | Question |
| --- | ---: | --- |
| Reliability and authority | 20 | Is the source positioned to know, and does it handle evidence responsibly? |
| Evidence traceability | 15 | Can important claims be traced to demonstrations, data, primary sources, or explicit reasoning? |
| Conceptual coherence | 15 | Does the material build a consistent model rather than present disconnected assertions? |
| Information density | 10 | How much relevant, non-promotional substance is present? |
| Pedagogical value | 10 | Does it explain mechanisms, examples, distinctions, and failure cases clearly? |
| Scope fit | 10 | Does it fill a declared part of this specific core? |
| Marginal contribution | 10 | What does it add beyond already admitted sources? |
| Calibration and nuance | 5 | Does it distinguish fact, inference, opinion, uncertainty, and exceptions? |
| Extractability | 3 | Can the text be recovered accurately without essential missing visuals? |
| Temporal fitness | 2 | Is it current enough for the claims it supports, or explicitly historical? |

Weights should be configurable by domain. Reliability and traceability should weigh more heavily in medicine, law, finance, safety, and empirical science. Pedagogy and demonstration may weigh more heavily in practical crafts, while canonical relevance may dominate historical or philosophical cores.

### Hard gates

A weighted score should not compensate for certain failures. A source should be rejected or quarantined when:

- The transcript is too corrupted to establish what was said.
- The source is substantially outside the core boundary.
- Important claims cannot be distinguished from promotion, fabrication, or unattributed copying.
- Essential meaning depends on unavailable visuals and cannot be reconstructed.
- The source creates unacceptable legal, privacy, or safety risk.
- It is redundant and contributes no meaningful new evidence, explanation, counterexample, or perspective.

### Provisional grades

- **A — Canonical:** strong enough to shape the core’s primary model.
- **B — Supporting:** useful evidence, explanation, examples, or alternative framing.
- **C — Exploratory:** valuable for discovery, controversy mapping, or hypothesis generation; not sufficient alone for compiled claims.
- **D — Archive only:** retained for traceability or historical interest, excluded from synthesis.
- **Reject:** not retained beyond minimal audit metadata where appropriate.

The numeric score should support consistency, but the grade must also include written reasons, confidence, grader identity/method, and any domain-specific override.

## Deeper questions the next iteration must answer

### What is the unit of quality?

A video is often too coarse. One video may contain an excellent explanation, an unsupported tangent, an outdated recommendation, and a promotional segment. Grading should exist at multiple levels:

- Source/channel prior.
- Document/video grade.
- Section or segment grade.
- Claim grade.

The system should avoid both extremes: treating a trusted creator as infallible and atomizing every sentence until explanatory context disappears.

### Who or what performs grading?

Possible graders include deterministic rules, language models, human reviewers, external reputation signals, and cross-source corroboration. None is sufficient alone.

A credible system will likely use:

- Rules for technical and format checks.
- Models for structured preliminary assessment.
- Cross-source analysis for agreement and dependency.
- Human review for rubric calibration, high-impact decisions, and disputed material.

The output must state which mechanism assigned each judgment. Model confidence must not be presented as source reliability.

### How do we prevent popularity from becoming authority?

Views, subscribers, production quality, and search rank are useful discovery signals but weak truth signals. They should never directly establish reliability. Creator-level priors may reduce review cost, but admission should remain content-specific.

### How do we measure marginal contribution?

Repeated claims can indicate importance, shared dependence, or an echo chamber. Redundancy analysis should ask whether a source contributes:

- Independent evidence.
- A clearer mechanism.
- A useful example or counterexample.
- A competing interpretation.
- Better pedagogy.
- Coverage of a missing prerequisite.

Near-duplicate explanation without new evidence should not receive the same weight as independent corroboration.

### What constitutes sufficient coverage?

The corpus should be compared against an explicit domain map, not against itself. Otherwise, the system will conclude that frequently discussed topics are the whole field.

Coverage requires:

- Scope statement.
- Prerequisite graph.
- Core concepts and competencies.
- Known schools or competing models.
- Canonical examples and failure modes.
- Declared exclusions.
- Gap register.

Web research should primarily respond to that gap register.

### When is a core complete?

A core is never universally complete. A version can be ready when:

- Its declared scope has no critical unaddressed gaps.
- Foundational claims meet evidence thresholds.
- Important disagreements are represented.
- Redundancy is controlled.
- Compression and retrieval evaluations pass.
- Known limitations and temporal cutoff are explicit.

Readiness should be a release decision against a contract, not a feeling produced by corpus size.

### How general should a core be?

Overly broad cores become shallow and incoherent; overly narrow cores become glorified notes. A useful boundary likely corresponds to a teachable domain with identifiable prerequisites and competencies—for example, “distributed systems fundamentals” rather than “software” or one specific deployment procedure.

Cores should be composable. A broader degree-like package can depend on smaller cores rather than flattening everything into one document.

### Is a core descriptive or prescriptive?

Primarily descriptive and explanatory. It may contain procedures when procedures are part of domain knowledge, but task execution belongs in skills or playbooks. This separation allows the same core to support many future tasks without embedding one preferred workflow.

### How should disagreement be compiled?

The compiler should not force false consensus. It should distinguish:

- Widely accepted foundations.
- Strong but bounded evidence.
- Competing schools or interpretations.
- Minority positions.
- Open questions.
- Source-specific claims.

Disagreement should be organized around claims, assumptions, evidence, and consequences—not reduced to “some people say.”

### How much compression is safe?

Compression is safe only when the core preserves the conditions needed to apply a claim correctly. Removing examples, qualifications, causal mechanisms, or counterexamples can make a shorter artifact less useful and more dangerous.

The optimization target should not be minimum tokens. It should be maximum usable understanding per token subject to fidelity and calibration constraints.

## Proposed compilation model

The next system should compile progressively rather than produce one monolithic summary.

### Stage 1: define the core contract

Before research begins, declare:

- Core identifier and version.
- Scope and exclusions.
- Intended depth and assumed prerequisites.
- Target competencies.
- Temporal cutoff and update policy.
- Risk level and evidence standards.
- Context/token budgets for compiled views.

### Stage 2: discover candidates

Use channels, playlists, citations, search, recommendations, and existing archives to create a candidate pool. Discovery metadata should remain separate from admission judgments.

### Stage 3: triage and acquire

Run cheap filters, estimate cost, deduplicate obvious copies, and acquire only candidates that justify deeper analysis.

### Stage 4: normalize and segment

Convert all sources into a shared document model while preserving source-specific metadata. Segment by semantic unit without losing document order or timestamp/page anchors.

### Stage 5: grade and admit

Apply document-, segment-, and claim-level grading. Record rationales and quarantine weak or uncertain material rather than silently discarding all traces.

### Stage 6: map claims and concepts

Extract concepts, claims, definitions, examples, relationships, prerequisites, disagreements, and evidence links. Detect duplication and likely shared sourcing.

### Stage 7: identify gaps

Compare the admitted evidence map with the core contract. Generate bounded research questions. Supplementary web research should answer those questions, not browse indefinitely.

### Stage 8: synthesize modules

Compile coherent modules organized by conceptual dependency. Preserve claim provenance, uncertainty, counterexamples, and dissent.

### Stage 9: compress into progressive views

Produce multiple levels from one underlying compiled model:

- **Level 0 — Identity card:** scope, version, purpose, prerequisites, limitations, and update date.
- **Level 1 — Orientation:** the minimum conceptual map needed to recognize the field and ask good questions.
- **Level 2 — Working core:** principles, mechanisms, vocabulary, canonical examples, and major disputes sufficient for ordinary reasoning.
- **Level 3 — Modules:** deeper topic packets loaded when a task requires them.
- **Level 4 — Evidence archive:** source passages, claims, citations, and full provenance.

This resolves the tension between brevity and context. Most tasks begin with Levels 0–2; deeper context remains addressable instead of being erased.

### Stage 10: evaluate and release

Run structural, epistemic, compression, retrieval, and agent-transfer evaluations. Release a versioned core only when it meets its declared thresholds.

## Proposed core package

A portable knowledge core should contain at least:

```text
core/
  manifest.yaml
  orientation.md
  curriculum.yaml
  concepts.jsonl
  claims.jsonl
  modules/
  disputes.jsonl
  gaps.yaml
  sources.jsonl
  retrieval/
  evaluations/
  changelog.md
```

### Manifest

The manifest defines identity, scope, intended level, prerequisites, version, temporal cutoff, build provenance, source counts, grading policy, and known limitations.

### Orientation

A concise narrative that explains the field’s shape, central questions, foundational mental models, and how modules relate. It should orient rather than exhaust.

### Curriculum

A dependency-aware sequence of concepts and competencies. It makes the university-degree analogy operational and exposes missing prerequisites.

### Concept records

Definitions, aliases, relationships, examples, misconceptions, and module membership.

### Claim ledger

Atomic enough to evaluate but contextual enough to interpret. Each claim should carry evidence links, status, confidence/calibration, scope conditions, counterevidence, and synthesis provenance.

### Modules

Human- and agent-readable explanatory units. Each module should combine concepts and claims into a coherent model rather than merely concatenate summaries.

### Dispute register

Important disagreements, their assumptions, supporting evidence, implications, and unresolved questions.

### Gap register

Missing evidence, unresolved terminology, uncovered curriculum nodes, stale areas, and questions queued for supplementary research.

### Source catalog

Stable source identities, source types, grades, rights/retention metadata, dependency relationships, and precise anchors into the archive.

### Retrieval layer

Task-loadable chunks or indexes derived from the compiled model. Retrieval artifacts should not become the authoritative copy of the core.

### Evaluations and changelog

Records of coverage, fidelity, retrieval, compression, and agent tests, plus the reasons a new core version differs from the previous one.

## Evaluation: how do we know a core works?

The current project evaluates whether files were produced. The next iteration must evaluate whether useful understanding was produced.

### Structural evaluation

- Schema validity.
- No broken source anchors.
- Required scope and provenance fields present.
- Deterministic builds where expected.
- No orphan claims or unexplained concepts.

### Source-quality evaluation

- Distribution of A/B/C/D sources.
- Proportion of foundational claims supported by canonical or independently corroborating sources.
- Transcript quality and missing-visual rates.
- Source diversity and dependency analysis.
- Staleness by claim category.

### Coverage evaluation

- Curriculum nodes supported by admitted material.
- Critical prerequisites represented.
- Known schools and counterpositions included.
- Gap severity and explicit exclusions.

### Fidelity evaluation

- Can a reviewer trace synthesized claims to source passages?
- Do source passages actually support the compiled wording?
- Are qualifications and scope conditions retained?
- Are direct quotations distinguished from paraphrase and synthesis?

### Compression evaluation

- What information is lost from archive to module and module to working core?
- Does the shorter view preserve mechanisms, boundaries, and counterexamples?
- Can omitted detail be retrieved reliably from provenance links?
- Is repetition serving reinforcement, or wasting context?

### Retrieval evaluation

- Can the system retrieve the correct module and evidence for representative questions?
- Does retrieval preserve surrounding context?
- Does it surface disagreement rather than only the dominant formulation?
- Are false-positive concept matches controlled?

### Agent-transfer evaluation

Compare the same agent with no core, the working core, and working core plus retrieval on tasks such as:

- Explain a foundational mechanism.
- Diagnose a misconception.
- Compare competing models.
- Apply concepts to a novel case.
- Identify when evidence is insufficient.
- Cite the basis of an answer.
- Refuse a conclusion outside the core’s scope.

The goal is not only higher answer accuracy. A good core should improve calibration, consistency, source traceability, and recognition of limits.

## Risks that deserve heavier weight

### Polished misinformation

Compilation can make weak claims look coherent and authoritative. Better writing is not better evidence. The system should never allow synthesis quality to conceal source quality.

### Selection bias

A YouTube-first corpus will reflect platform incentives, English-language availability, creator networks, and the collector’s subscriptions. The core contract and gap analysis must counteract the idea that the available corpus defines the field.

### False consensus

Ten videos repeating one upstream claim do not equal ten independent confirmations. Source dependency and citation lineage matter.

### Context collapse

Short summaries often erase when a claim applies, what assumptions it uses, and how it can fail. Progressive disclosure and claim conditions are necessary defenses.

### Model-generated authority

If language models grade and synthesize sources, their outputs can inherit hidden errors or preferences. Model work should be recorded as a transformation with versioned prompts/models and review status, not treated as evidence.

### Temporal decay

Technical APIs, medical guidance, laws, prices, standards, and public facts change at different rates. Update policy should exist at claim level or claim category, not only at whole-core level.

### Domain risk

A psychology core, for example, can influence sensitive personal decisions. High-risk domains require stronger evidence thresholds, clearer limitations, and more conservative compilation than software tutorials or historical overviews.

### Copyright and retention

The system should distinguish preservation for private analysis from redistribution. Source type, quotation length, license, and publication status may constrain what a portable core can contain.

### Adversarial or irrelevant instructions

Internet text can contain prompt injection, hidden instructions, or manipulative framing. Ingested content must always be treated as evidence to analyze, never as instructions to the compiler or consuming agent.

### Core-induced tunnel vision

A focused package can improve reasoning within a subject while narrowing the agent’s perspective. The core should disclose its scope and source composition, preserve external uncertainty, and avoid presenting one taxonomy as the only possible worldview.

## Technical after-action findings

The implementation findings from the earlier retrospective remain relevant but are now subordinate to the product-level issues.

| Finding | Consequence |
| --- | --- |
| Credentials are committed in Rust source | Immediate rotation and secure configuration are required |
| Main `search` has conflicting `-c` flags | A documented core CLI path is broken despite successful compilation |
| Rust has zero tests | Data and parsing contracts can drift undetected |
| Python has no dependency manifest | Knowledge builds are not reproducible |
| Visualizer dependencies exceed the default Node runtime | The checked-in interface cannot be verified in the baseline environment |
| Scripts contain absolute workstation paths | Pipeline stages are coupled to one machine |
| REST/MCP expect obsolete root-level artifacts | Consumers and builders disagree on artifact ownership |
| The graph manifest is copied three times | There is no single authoritative build output |
| Generated prose and extracted evidence are not clearly distinguished | Consumers can overestimate epistemic provenance |
| Batch failures discard detailed causes | Corpus gaps can be silent |

These are not isolated cleanup items. They reflect the absence of shared contracts between acquisition, archive, compilation, and consumption.

## Decisions to preserve

- Preserve raw source material separately from normalized and synthesized forms.
- Preserve timestamp/page/section anchors through every transformation.
- Preserve local-first, offline access to owned corpus data.
- Preserve human-inspectable formats and deterministic baselines.
- Preserve the three-order taxonomy as an experiment and regression dataset.
- Preserve the graph UI’s ability to reveal structure.
- Preserve `scratch/` as a research record until its ideas are reviewed.

## Decisions to change

- Do not equate acquisition with admission.
- Do not use duration or creator identity as a sufficient quality proxy.
- Do not let the corpus define its own curriculum.
- Do not present templated editorial material as transcript-derived synthesis.
- Do not make one giant output serve archive, human reading, retrieval, and agent loading.
- Do not add new source types before defining a shared source/document contract.
- Do not expand research without a gap register and stopping rule.
- Do not call an artifact a knowledge core until it passes transfer-oriented evaluation.

## Recommended next experiment

Before rebuilding the platform, produce one small core manually enough to learn what the compiler must represent.

Choose a bounded subject with:

- Existing high-quality YouTube coverage.
- Available primary or authoritative web sources.
- Clear prerequisites and competencies.
- Some meaningful disagreement or nuance.
- Low enough risk to iterate safely.

Then:

1. Write the core contract and curriculum before selecting sources.
2. Grade a candidate pool of roughly 20–40 videos.
3. Admit a deliberately small set based on quality and marginal contribution.
4. Use web research only against an explicit gap list.
5. Build the proposed core package with claim-level provenance.
6. Create Level 0–4 views.
7. Evaluate an agent with and without the core.
8. Record where human judgment was still necessary.

This vertical slice will answer more architectural questions than immediately generalizing every existing script.

## Open decisions requiring deliberate answers

1. What subject should serve as the pilot core?
2. Who is the first consumer: this project’s agent, any compatible agent, or a human learner as well?
3. What context budgets should Levels 1 and 2 target?
4. Which grading dimensions are universal, and which must be domain profiles?
5. What evidence threshold is required for a claim to enter the working core?
6. How should independent corroboration be detected when sources share upstream material?
7. How much human review is acceptable per source and per released core?
8. Should full transcripts remain private while compiled cores are portable?
9. What licensing and quotation policy applies to distributable cores?
10. How should a consuming agent request deeper modules or evidence?
11. When does a knowledge core become several composable cores?
12. What is the update trigger: time, source changes, failed evaluations, or user request?
13. Should a core encode procedures, or merely reference separate task skills?
14. How will the system represent irreducible ambiguity without bloating the working core?
15. What is the minimum evaluation evidence required before labeling a release trustworthy?

## Final assessment

The first iteration was a successful acquisition-and-representation prototype. It produced a valuable corpus and demonstrated many possible outputs. Its weakness was not lack of ambition; it was allowing output variety to outrun a definition of knowledge quality.

The next iteration should organize itself around one invariant:

> A knowledge core is only as useful as its source admission, epistemic provenance, conceptual coherence, and ability to preserve necessary context under compression.

YouTube remains a powerful starting point, but it is a source stream rather than the product boundary. Supplementary research should be guided by declared gaps. Archives should preserve evidence. Cores should compile understanding. Skills should apply that understanding to tasks. Agent-facing views should load only the depth a task requires while keeping the path back to evidence intact.

That separation gives the project a clearer identity and a much stronger basis for the next build.
