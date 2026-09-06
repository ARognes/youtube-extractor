import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')
REPORTS_DIR = os.path.join(SCRATCH_DIR, 'reports')

CHROME_PATH = "/Applications/Browsers/Google Chrome.app/Contents/MacOS/Google Chrome"

def log(msg):
    print(f"📘 [COMPENDIUM] {msg}", flush=True)

def generate_compendium_for_core(core_id="core_cognitive_psychology"):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    log(f"Compiling publication compendium for '{core_id}'...")

    # Load core data
    core_file = os.path.join(SCRATCH_DIR, f"{core_id}_master_archive.json")
    if not os.path.exists(core_file):
        log(f"❌ Core file {core_file} not found!")
        return None

    with open(core_file, 'r', encoding='utf-8') as f:
        core_data = json.load(f)

    # Load contributor codices
    creators = core_data.get('channels_included', [])
    codices = {}
    for ch in creators:
        slug = ch.lower().replace(' ', '_').replace('@', '').replace("'", '_')
        c_path = os.path.join(SCRATCH_DIR, f"{slug}_master_codex.json")
        if os.path.exists(c_path):
            with open(c_path, 'r', encoding='utf-8') as cf:
                codices[ch] = json.load(cf)

    # Load video packets for core
    t_files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    core_videos = []
    queries = [ch.lower().replace('@', '').replace(' ', '') for ch in creators]
    queries.append('theramin')

    for fn in t_files:
        fp = os.path.join(TRANSCRIPTS_DIR, fn)
        try:
            with open(fp, 'r', encoding='utf-8') as pf:
                pkt = json.load(pf)
                ch = (pkt.get('channel') or pkt.get('channel_name') or '').lower().replace('@', '').replace(' ', '')
                if any(q in ch for q in queries):
                    core_videos.append(pkt)
        except Exception:
            pass

    core_videos.sort(key=lambda x: len((x.get('transcript') or '').split()), reverse=True)
    total_words = sum(len((p.get('transcript') or '').split()) for p in core_videos)
    log(f"Loaded {len(core_videos)} catalog videos across {len(creators)} creators ({total_words:,} total spoken words).")

    # 1. Compile Markdown Document
    md_content = build_markdown_document(core_id, core_data, codices, core_videos, total_words)
    md_path = os.path.join(REPORTS_DIR, f"{core_id}_compendium.md")
    with open(md_path, 'w', encoding='utf-8') as mf:
        mf.write(md_content)
    log(f"✅ Generated Companion Markdown Manual: {md_path}")

    # 2. Compile Publication-Grade Styled HTML
    html_content = build_styled_html_document(core_id, core_data, codices, core_videos, total_words)
    html_path = os.path.join(REPORTS_DIR, f"{core_id}_compendium.html")
    with open(html_path, 'w', encoding='utf-8') as hf:
        hf.write(html_content)
    log(f"✅ Generated Publication HTML Print Layout: {html_path}")

    # 3. Convert HTML to Publication-Grade PDF via Headless Chrome
    pdf_path = os.path.join(REPORTS_DIR, f"{core_id}_compendium.pdf")
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    log("Rendering publication PDF via Chrome headless...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(pdf_path):
        pdf_size = os.path.getsize(pdf_path) / (1024 * 1024)
        log(f"🎉 SUCCESS! Rendered publication PDF ({pdf_size:.2f} MB): {pdf_path}")
    else:
        log(f"⚠️ PDF rendering notice: {res.stderr}")

    return md_path, pdf_path

def build_markdown_document(core_id, core_data, codices, videos, total_words):
    lines = []
    lines.append(f"# 🏛️ MACE Archival Compendium: {core_data['title']}")
    lines.append(f"**Domain Archive ID:** `{core_id}`  ")
    lines.append(f"**Publication Date:** {datetime.now().strftime('%B %Y')} | **Archived Masterclasses:** {len(videos)} | **Spoken Words:** {total_words:,}  ")
    lines.append(f"**Contributing Creators:** {', '.join(core_data.get('channels_included', []))}  \n")
    lines.append("---")
    lines.append("\n## 📖 Executive Summary & Scope")
    lines.append(f"*{core_data['description']}*\n")
    lines.append("This archival compendium concentrates the grass-roots psychological wisdom, clinical psychiatric insights, and philosophical frameworks of the world's leading independent mental health researchers into a single machine-actionable, human-readable reference text.\n")

    # PART I: Executive Distillation & Axioms
    lines.append("## 🎯 PART I: EXECUTIVE DISTILLATION & FIRST PRINCIPLES\n")
    lines.append("### Foundational Axioms\n")
    
    # Gather principles from codices
    for ch, codex in codices.items():
        lines.append(f"#### ✦ Contributing Authority: {ch}")
        for fp in codex.get('first_principles', []):
            lines.append(f"- **{fp['principle']}:** {fp['axiom']}")
            if 'formula' in fp:
                lines.append(f"  *Formula:* `{fp['formula']}`")
        lines.append("")

    lines.append("### Comprehensive Mental Model & Terminology Dictionary\n")
    all_taxonomy = {}
    for ch, codex in codices.items():
        for k, v in codex.get('mental_model_dictionary', {}).items():
            all_taxonomy[k] = (v, ch)

    for term, (definition, author) in sorted(all_taxonomy.items()):
        lines.append(f"- **{term}** *(Origin: {author})*: {definition}")

    lines.append("\n### Actionable Step-by-Step Tactical Playbooks\n")
    for ch, codex in codices.items():
        for pb in codex.get('tactical_playbooks', []):
            lines.append(f"#### 📋 {pb['title']} (Framework: {ch})")
            for i, st in enumerate(pb.get('steps', []), 1):
                lines.append(f"{i}. {st}")
            lines.append("")

    # PART II: Thematic Synthesis Chapters
    lines.append("\n---\n## 🧠 PART II: THEMATIC DEEP-DIVE SYNTHESIS CHAPTERS\n")
    lines.append("### Chapter 1: The Architecture of Covert Manipulation & Double-Binds")
    lines.append("*Synthesized from TheraminTrees & Dr. Alok Kanojia*\n")
    lines.append("Covert manipulation functions not through overt aggression, but through the structural fabrication of **double-bind scenarios**—interpersonal frameworks where any conceivable choice by the victim is weaponized against them. Indoctrination and narcissistic control rely on isolating the individual from external reality testing, using manufactured guilt (FOG: Fear, Obligation, Guilt) to enforce compliance.\n")
    lines.append("> *\"Manipulators construct contradictory demands where any response is framed as a failure, forcing compliance while evading accountability.\"* — **TheraminTrees**\n")

    lines.append("### Chapter 2: Samskaras, Emotional Memory & The Digestion of Trauma")
    lines.append("*Synthesized from Dr. Alok Kanojia (HealthyGamerGG) & JulienHimself*\n")
    lines.append("Modern digital hyper-stimulation allows individuals to endlessly suppress painful emotional memories (**Samskaras**). When an emotional experience is avoided through gaming, social media, or compulsive work, it remains physiologically trapped in the subconscious. Healing does not require traumatic regression or endless analysis; it requires becoming the neutral observer (**Sakshi**) and allowing the uncomfortable somatic sensation to complete its biological cycle.\n")
    lines.append("> *\"Unprocessed past emotional experiences create unconscious behavioral patterns that dictate current anxiety and burnout. Sit with the sensation without immediate distraction.\"* — **Dr. K**\n")

    lines.append("### Chapter 3: Cognitive Autonomy, Boundary Defense & Dopamine Baseline Reset")
    lines.append("*Synthesized from TheraminTrees, HealthyGamerGG & JulienHimself*\n")
    lines.append("Cognitive autonomy is the deliberate capacity to decouple personal identity from external approval and high-dopamine triggers. Setting boundaries is not an aggressive act, but an informational statement of limits. When dealing with covert manipulation or severe digital addiction, the **Grey Rock technique** and baseline dopamine detoxing allow executive function to recover its sovereign capacity.\n")

    # PART III: Contributing Creator Profiles
    lines.append("\n---\n## 🏛️ PART III: CONTRIBUTING CREATOR DOSSIER PROFILES\n")
    for ch, codex in codices.items():
        lines.append(f"### Profile: {ch}")
        lines.append(f"- **Total Catalog Masterclasses Analyzed:** {codex.get('total_videos_analyzed', len(videos))}")
        lines.append(f"- **Spoken Word Volume:** {codex.get('total_spoken_words', 0):,} words")
        lines.append(f"- **Core Focus:** Comprehensive psychological deconstruction and practical mental health protocols.")
        lines.append("")

    # PART IV: Annotated Video Catalog & Citation Index
    lines.append("\n---\n## 📚 PART IV: ANNOTATED VIDEO CATALOG & CITATION INDEX\n")
    lines.append(f"Index of all {len(videos)} masterclasses analyzed and cited in this compendium:\n")

    for idx, v in enumerate(videos, 1):
        v_id = v.get('video_id') or v.get('id')
        title = v.get('title')
        ch = v.get('channel')
        words = len((v.get('transcript') or '').split())
        url = v.get('url') or f"https://www.youtube.com/watch?v={v_id}"
        summary = v.get('video_summary') or {}
        synopsis = summary.get('executive_synopsis', title)

        lines.append(f"### {idx}. [{title}]({url})")
        lines.append(f"**Creator:** {ch} | **Spoken Words:** {words:,} words | **Duration:** {v.get('duration', 'N/A')}")
        lines.append(f"*{synopsis}*\n")
        takeaways = summary.get('core_takeaways', [])
        if takeaways:
            lines.append("**Key Takeaways:**")
            for t in takeaways:
                lines.append(f"- {t}")
        lines.append("")

    return "\n".join(lines)

def build_styled_html_document(core_id, core_data, codices, videos, total_words):
    # CSS for beautiful publication printing
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Inter:wght@300;400;500;600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&display=swap');

    @page {
        size: letter;
        margin: 20mm 18mm 22mm 18mm;
        @bottom-right {
            content: "Page " counter(page);
            font-family: 'Inter', sans-serif;
            font-size: 8.5pt;
            color: #64748b;
        }
        @top-right {
            content: "MACE Archival Compendium: Cognitive Psychology";
            font-family: 'Inter', sans-serif;
            font-size: 8pt;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    }

    body {
        font-family: 'Merriweather', serif;
        font-size: 10pt;
        line-height: 1.65;
        color: #1e293b;
        background: #ffffff;
        margin: 0;
        padding: 0;
    }

    .cover-page {
        page-break-after: always;
        height: 90vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border-bottom: 2px solid #0f172a;
        padding: 40px 20px;
    }

    .cover-badge {
        display: inline-block;
        background: #0f172a;
        color: #38bdf8;
        font-family: 'Inter', sans-serif;
        font-size: 9pt;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        padding: 6px 14px;
        border-radius: 4px;
        margin-bottom: 24px;
    }

    .cover-title {
        font-family: 'Cinzel', serif;
        font-size: 32pt;
        line-height: 1.15;
        color: #0f172a;
        margin: 0 0 16px 0;
    }

    .cover-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 14pt;
        font-weight: 400;
        color: #475569;
        margin: 0 0 36px 0;
        line-height: 1.4;
    }

    .cover-meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        font-family: 'Inter', sans-serif;
        border-top: 1px solid #cbd5e1;
        padding-top: 24px;
        margin-top: auto;
    }

    .meta-box {
        font-size: 9pt;
    }
    .meta-label {
        color: #64748b;
        font-size: 8pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .meta-val {
        font-weight: 700;
        color: #0f172a;
        margin-top: 2px;
    }

    .page-break {
        page-break-after: always;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }

    h1 {
        font-size: 20pt;
        border-bottom: 2px solid #0f172a;
        padding-bottom: 8px;
        margin-top: 32px;
        margin-bottom: 16px;
        page-break-after: avoid;
    }

    h2 {
        font-size: 14pt;
        color: #0369a1;
        margin-top: 24px;
        margin-bottom: 12px;
        page-break-after: avoid;
    }

    h3 {
        font-size: 11pt;
        color: #0f172a;
        margin-top: 18px;
        margin-bottom: 8px;
        page-break-after: avoid;
    }

    p {
        margin: 0 0 12px 0;
    }

    blockquote {
        border-left: 3px solid #0284c7;
        margin: 16px 0;
        padding: 8px 16px;
        background: #f0f9ff;
        font-style: italic;
        color: #0369a1;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }

    .callout-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 16px 0;
        page-break-inside: avoid;
    }

    .dictionary-term {
        margin-bottom: 10px;
        font-size: 9.5pt;
    }
    .dictionary-term strong {
        color: #0f172a;
        font-family: 'Inter', sans-serif;
    }

    .author-badge {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        font-family: 'Inter', sans-serif;
        font-size: 7.5pt;
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 3px;
        margin-left: 6px;
    }

    .catalog-item {
        border-bottom: 1px solid #e2e8f0;
        padding: 12px 0;
        page-break-inside: avoid;
    }
    .catalog-title {
        font-family: 'Inter', sans-serif;
        font-size: 10pt;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .catalog-meta {
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: #64748b;
        margin-bottom: 6px;
    }
    .catalog-synopsis {
        font-size: 9pt;
        color: #334155;
        margin: 0;
        font-style: italic;
    }
    """

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>MACE Archival Compendium: Cognitive Psychology</title>
        <style>{css}</style>
    </head>
    <body>
        <!-- COVER PAGE -->
        <div class="cover-page">
            <div class="cover-badge">MACE Archival Core Edition</div>
            <h1 class="cover-title">Cognitive Psychology &amp; Emotional Processing</h1>
            <p class="cover-subtitle">Deconstructing Covert Manipulation, Unresolved Emotional Trauma, and Cognitive Autonomy</p>
            
            <div class="cover-meta-grid">
                <div class="meta-box">
                    <div class="meta-label">Domain Identifier</div>
                    <div class="meta-val">{core_id}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Archived Masterclasses</div>
                    <div class="meta-val">{len(videos)} Videos Analyzed</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Total Spoken Volume</div>
                    <div class="meta-val">{total_words:,} Words</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Contributing Authorities</div>
                    <div class="meta-val">TheraminTrees, Dr. K, JulienHimself, Joe Hudson</div>
                </div>
            </div>
        </div>

        <!-- PART I -->
        <h1>PART I: Executive Distillation &amp; First Principles</h1>
        <p>This section outlines the foundational axioms and non-negotiable laws governing interpersonal manipulation, subconscious trauma storage, and executive recovery.</p>

        <h2>1. Foundational Axioms</h2>
    """

    for ch, codex in codices.items():
        html += f"<h3>Contributing Authority: {ch}</h3><ul>"
        for fp in codex.get('first_principles', []):
            html += f"<li><strong>{fp['principle']}:</strong> {fp['axiom']}</li>"
        html += "</ul>"

    html += "<h2>2. Mental Model &amp; Terminology Dictionary</h2>"
    all_taxonomy = {}
    for ch, codex in codices.items():
        for k, v in codex.get('mental_model_dictionary', {}).items():
            all_taxonomy[k] = (v, ch)

    for term, (definition, author) in sorted(all_taxonomy.items()):
        html += f"""
        <div class="dictionary-term">
            <strong>{term}</strong> <span class="author-badge">{author}</span>: {definition}
        </div>
        """

    html += """
        <h2>3. Tactical Action Playbooks</h2>
    """
    for ch, codex in codices.items():
        for pb in codex.get('tactical_playbooks', []):
            html += f"""
            <div class="callout-box">
                <h4 style="margin:0 0 8px 0; color:#0369a1;">📋 {pb['title']} <span class="author-badge">{ch}</span></h4>
                <ol style="margin:0; padding-left:20px; font-size:9.5pt;">
            """
            for st in pb.get('steps', []):
                html += f"<li style='margin-bottom:4px;'>{st}</li>"
            html += "</ol></div>"

    html += """
        <div class="page-break"></div>
        <!-- PART II -->
        <h1>PART II: Thematic Deep-Dive Synthesis Chapters</h1>
        
        <h2>Chapter 1: The Architecture of Covert Manipulation &amp; Double-Binds</h2>
        <p><em>Synthesized from TheraminTrees &amp; Dr. Alok Kanojia</em></p>
        <p>Covert manipulation functions not through overt aggression, but through the structural fabrication of <strong>double-bind scenarios</strong>—interpersonal frameworks where any conceivable choice by the victim is weaponized against them. Indoctrination and narcissistic control rely on isolating the individual from external reality testing, using manufactured guilt (FOG: Fear, Obligation, Guilt) to enforce compliance.</p>
        <blockquote>
            "Manipulators construct contradictory demands where any response is framed as a failure, forcing compliance while evading accountability." — <strong>TheraminTrees</strong>
        </blockquote>
        <p>When an authoritarian structure or narcissistic individual constructs a double-bind, reasoning and logical dialogue become counterproductive. The victim cannot 'solve' a contradictory demand. The only therapeutic resolution is disengaging from the frame entirely through emotional neutrality and firm boundary enforcement.</p>

        <h2>Chapter 2: Samskaras, Emotional Memory &amp; The Digestion of Trauma</h2>
        <p><em>Synthesized from Dr. Alok Kanojia (HealthyGamerGG) &amp; JulienHimself</em></p>
        <p>Modern digital hyper-stimulation allows individuals to endlessly suppress painful emotional memories (<strong>Samskaras</strong>). When an emotional experience is avoided through gaming, social media, or compulsive work, it remains physiologically trapped in the subconscious. Healing does not require traumatic regression or endless analysis; it requires becoming the neutral observer (<strong>Sakshi</strong>) and allowing the uncomfortable somatic sensation to complete its biological cycle.</p>
        <blockquote>
            "Unprocessed past emotional experiences create unconscious behavioral patterns that dictate current anxiety and burnout. Sit with the sensation without immediate distraction." — <strong>Dr. K</strong>
        </blockquote>

        <h2>Chapter 3: Cognitive Autonomy, Boundary Defense &amp; Dopamine Baseline Reset</h2>
        <p><em>Synthesized from TheraminTrees, HealthyGamerGG &amp; JulienHimself</em></p>
        <p>Cognitive autonomy is the deliberate capacity to decouple personal identity from external approval and high-dopamine triggers. Setting boundaries is not an aggressive act, but an informational statement of limits. When dealing with covert manipulation or severe digital addiction, the <strong>Grey Rock technique</strong> and baseline dopamine detoxing allow executive function to recover its sovereign capacity.</p>

        <div class="page-break"></div>
        <!-- PART III -->
        <h1>PART III: Contributing Creator Dossier Profiles</h1>
    """

    for ch, codex in codices.items():
        html += f"""
        <div class="callout-box">
            <h3 style="margin:0 0 6px 0;">🏛️ Authority Dossier: {ch}</h3>
            <div style="font-family:'Inter', sans-serif; font-size:8.5pt; color:#64748b; margin-bottom:8px;">
                Total Masterclasses: {codex.get('total_videos_analyzed', len(videos))} | Analyzed Words: {codex.get('total_spoken_words', 0):,} words
            </div>
            <p style="font-size:9.5pt; margin:0;">Specializes in clinical psychiatric breakdown, deconstructing covert manipulation, boundary setting, and cognitive autonomy.</p>
        </div>
        """

    html += f"""
        <div class="page-break"></div>
        <!-- PART IV -->
        <h1>PART IV: Annotated Video Catalog &amp; Citation Index</h1>
        <p>Complete archival registry of all {len(videos)} masterclasses indexed in this compendium:</p>
    """

    for idx, v in enumerate(videos, 1):
        v_id = v.get('video_id') or v.get('id')
        title = v.get('title')
        ch = v.get('channel')
        words = len((v.get('transcript') or '').split())
        url = v.get('url') or f"https://www.youtube.com/watch?v={v_id}"
        summary = v.get('video_summary') or {}
        synopsis = summary.get('executive_synopsis', title)

        html += f"""
        <div class="catalog-item">
            <div class="catalog-title">{idx}. <a href="{url}" style="color:#0369a1; text-decoration:none;">{title}</a></div>
            <div class="catalog-meta">Creator: {ch} &bull; {words:,} words &bull; Duration: {v.get('duration', 'N/A')}</div>
            <p class="catalog-synopsis">"{synopsis}"</p>
        </div>
        """

    html += """
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--core', default='core_cognitive_psychology')
    args = parser.parse_args()

    generate_compendium_for_core(args.core)
