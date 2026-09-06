#!/usr/bin/env python3
"""
generate_dag_visualizer.py

Compiles an interactive HTML application (`reports/cognitive_concept_dag_visualizer.html`)
to visually browse the Epistemic Concept Dependency DAG and Situation-to-Protocol Matrix.
"""

import os
import json

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
DAG_PATH = os.path.join(SCRATCH_DIR, 'cognitive_concept_dag.json')
MATRIX_PATH = os.path.join(SCRATCH_DIR, 'cognitive_situation_protocol_matrix.json')
OUTPUT_HTML = os.path.join(SCRATCH_DIR, 'reports', 'cognitive_concept_dag_visualizer.html')

def build_mermaid_graph(nodes):
    lines = ["graph TD"]
    lines.append("  %% Style Classes")
    lines.append("  classDef level0 fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#ecfdf5;")
    lines.append("  classDef level1 fill:#78350f,stroke:#f59e0b,stroke-width:2px,color:#fffbeb;")
    lines.append("  classDef level2 fill:#881337,stroke:#f43f5e,stroke-width:2px,color:#fff1f2;")
    lines.append("  classDef level3 fill:#312e81,stroke:#6366f1,stroke-width:2px,color:#eef2ff;")

    # Nodes
    for n in nodes:
        clean_name = n['name'].replace('"', "'")
        lvl = n['level']
        lines.append(f'  {n["id"]}["<b>[{n["id"].split("_")[0]}]</b><br/>{clean_name}"]:::level{lvl}')

    lines.append("")
    lines.append("  %% Directed Edges")
    # Edges from prerequisites
    for n in nodes:
        target = n["id"]
        for prereq in n.get("prerequisites", []):
            lines.append(f"  {prereq} --> {target}")
        for res in n.get("resolved_by", []):
            lines.append(f"  {target} -.->|remedy| {res}")

    return "\n".join(lines)

def main():
    print("Generating Cognitive Architecture DAG Visualizer HTML...")
    with open(DAG_PATH, 'r', encoding='utf-8') as f:
        dag_data = json.load(f)

    with open(MATRIX_PATH, 'r', encoding='utf-8') as f:
        matrix_data = json.load(f)

    nodes = dag_data.get('nodes', [])
    crises = matrix_data.get('crises', [])
    mermaid_code = build_mermaid_graph(nodes)

    nodes_json_str = json.dumps(nodes).replace("</", "<\\/")
    crises_json_str = json.dumps(crises).replace("</", "<\\/")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Cognitive Psychology Knowledge Core: Epistemic DAG & Crisis Matrix</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: rgba(18, 26, 43, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --accent-0: #10b981;
      --accent-1: #f59e0b;
      --accent-2: #f43f5e;
      --accent-3: #6366f1;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      line-height: 1.5;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }}
    header {{
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 10;
    }}
    .header-title h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .header-title p {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}
    .nav-tabs {{
      display: flex;
      gap: 8px;
    }}
    .nav-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 0.82rem;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.2s;
    }}
    .nav-btn:hover, .nav-btn.active {{
      background: #2563eb;
      color: #fff;
      border-color: #3b82f6;
    }}
    .main-container {{
      display: flex;
      flex: 1;
      overflow: hidden;
      position: relative;
    }}
    .view-panel {{
      display: none;
      width: 100%;
      height: 100%;
    }}
    .view-panel.active {{
      display: flex;
    }}
    /* DAG Canvas */
    .dag-canvas-container {{
      flex: 1;
      overflow: auto;
      padding: 24px;
      display: flex;
      justify-content: center;
      background: radial-gradient(circle at 50% 50%, rgba(30, 41, 59, 0.5) 0%, rgba(9, 13, 22, 1) 100%);
    }}
    .mermaid {{
      width: 100%;
      max-width: 1300px;
    }}
    /* Inspector Sidebar */
    .inspector-sidebar {{
      width: 440px;
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border-left: 1px solid var(--card-border);
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      padding: 24px;
      transition: width 0.3s;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .badge-0 {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-0); border: 1px solid var(--accent-0); }}
    .badge-1 {{ background: rgba(245, 158, 11, 0.2); color: var(--accent-1); border: 1px solid var(--accent-1); }}
    .badge-2 {{ background: rgba(244, 63, 94, 0.2); color: var(--accent-2); border: 1px solid var(--accent-2); }}
    .badge-3 {{ background: rgba(99, 102, 241, 0.2); color: var(--accent-3); border: 1px solid var(--accent-3); }}
    .section-title {{
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 16px 0 6px 0;
    }}
    .callout-box {{
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-left: 3px solid #38bdf8;
      padding: 12px;
      border-radius: 6px;
      font-size: 0.82rem;
      margin: 12px 0;
    }}
    .callout-box p {{
      margin-bottom: 6px;
    }}
    .callout-box p:last-child {{ margin-bottom: 0; }}
    .citation-card {{
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--card-border);
      padding: 10px 12px;
      border-radius: 6px;
      margin-bottom: 8px;
      font-size: 0.8rem;
    }}
    .citation-card a {{
      color: #38bdf8;
      text-decoration: none;
      font-weight: 600;
    }}
    .citation-card a:hover {{ text-decoration: underline; }}
    /* Matrix View */
    .matrix-container {{
      flex: 1;
      overflow-y: auto;
      padding: 32px;
      max-width: 1200px;
      margin: 0 auto;
      width: 100%;
    }}
    .crisis-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .crisis-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
    }}
    .crisis-header h3 {{
      font-size: 1.15rem;
      color: #fff;
    }}
    .protocol-step {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--card-border);
      border-radius: 6px;
      padding: 12px;
      margin-top: 8px;
      font-size: 0.85rem;
    }}
    .protocol-step-title {{
      font-weight: 600;
      color: #38bdf8;
      margin-bottom: 4px;
    }}
    .anti-pattern {{
      color: #fda4af;
      font-size: 0.82rem;
      margin-top: 4px;
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-title">
      <h1>🧠 Cognitive Psychology Knowledge Architecture</h1>
      <p>142 Masterclasses | Epistemic Directed Acyclic Graph & Situation-to-Protocol Matrix</p>
    </div>
    <div class="nav-tabs">
      <button class="nav-btn active" onclick="switchView('dag')">🌳 Epistemic DAG</button>
      <button class="nav-btn" onclick="switchView('matrix')">🎯 Situation-to-Protocol Matrix</button>
      <button class="nav-btn" onclick="switchView('catalog')">📚 Master Video Catalog</button>
    </div>
  </header>

  <div class="main-container">

    <!-- VIEW 1: DAG EXPLORER -->
    <div id="view-dag" class="view-panel active">
      <div class="dag-canvas-container">
        <div class="mermaid">
{mermaid_code}
        </div>
      </div>
      <div class="inspector-sidebar" id="inspector-sidebar">
        <div id="inspector-placeholder" style="margin-top: 40px; text-align: center; color: var(--text-muted);">
          <p style="font-size: 2rem; margin-bottom: 12px;">👆</p>
          <p>Click on any concept node in the DAG to inspect its prerequisites, clinical mechanisms, dialectic gap annotations, and timestamped masterclasses.</p>
        </div>
        <div id="inspector-content" style="display: none;">
          <div id="node-badge-container"></div>
          <h2 id="node-title" style="font-size: 1.25rem; font-weight: 700; margin: 8px 0;"></h2>
          <p id="node-authority" style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 12px;"></p>
          
          <div class="section-title">Epistemic Definition</div>
          <p id="node-definition" style="font-size: 0.85rem; color: #cbd5e1;"></p>

          <div class="section-title">Dialectic Gap & Context Header</div>
          <div class="callout-box">
            <p><strong>⚠️ External Theoretical Roots:</strong> <span id="node-epistemology"></span></p>
            <p><strong>⚠️ Serial Prerequisites:</strong> <span id="node-serial"></span></p>
            <p><strong>⚠️ Restored Diagrammatic Context:</strong> <span id="node-multimodal"></span></p>
          </div>

          <div class="section-title">Relationships & Trajectories</div>
          <p style="font-size: 0.8rem; margin-bottom: 4px;"><strong>Prerequisite Roots:</strong> <span id="node-prereqs"></span></p>
          <p style="font-size: 0.8rem; margin-bottom: 4px;"><strong>Leads to Symptoms:</strong> <span id="node-symptoms"></span></p>
          <p style="font-size: 0.8rem; margin-bottom: 12px;"><strong>Prescribed Protocols:</strong> <span id="node-protocols"></span></p>

          <div class="section-title">Primary Masterclass Citations</div>
          <div id="node-citations"></div>
        </div>
      </div>
    </div>

    <!-- VIEW 2: CRISIS MATRIX -->
    <div id="view-matrix" class="view-panel">
      <div class="matrix-container" id="matrix-container">
        <!-- Rendered via JS -->
      </div>
    </div>

    <!-- VIEW 3: CATALOG VIEW -->
    <div id="view-catalog" class="view-panel">
      <div class="matrix-container">
        <h2 style="margin-bottom: 16px;">Core Video Knowledge Catalog (142 Masterclasses)</h2>
        <p style="color: var(--text-muted); margin-bottom: 24px;">Complete multi-creator inventory powering the Cognitive Psychology Knowledge Core.</p>
        <div id="catalog-list"></div>
      </div>
    </div>

  </div>

  <script>
    const DAG_NODES = {nodes_json_str};
    const CRISES = {crises_json_str};

    mermaid.initialize({{
      startOnLoad: true,
      theme: 'dark',
      securityLevel: 'loose',
      flowchart: {{
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis'
      }}
    }});

    function switchView(viewName) {{
      document.querySelectorAll('.view-panel').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

      document.getElementById('view-' + viewName).classList.add('active');
      event.target.classList.add('active');

      if (viewName === 'matrix') renderMatrix();
      if (viewName === 'catalog') renderCatalog();
    }}

    function inspectNode(nodeId) {{
      const n = DAG_NODES.find(item => item.id === nodeId);
      if (!n) return;

      document.getElementById('inspector-placeholder').style.display = 'none';
      document.getElementById('inspector-content').style.display = 'block';

      const badgeContainer = document.getElementById('node-badge-container');
      badgeContainer.innerHTML = `<span class="badge badge-${{n.level}}">Level ${{n.level}}: ${{n.category}}</span>`;

      document.getElementById('node-title').textContent = n.name;
      document.getElementById('node-authority').textContent = "Contributing Authority: " + n.epistemic_authority.join(', ');
      document.getElementById('node-definition').textContent = n.definition;

      const gaps = n.gap_annotations || {{}};
      document.getElementById('node-epistemology').textContent = gaps.assumed_epistemology || "None specified";
      document.getElementById('node-serial').textContent = gaps.serial_dependencies || "Self-contained";
      document.getElementById('node-multimodal').textContent = gaps.multimodal_cues || "Audio verbatim";

      document.getElementById('node-prereqs').textContent = n.prerequisites.length ? n.prerequisites.join(', ') : "None (Root Primitive)";
      document.getElementById('node-symptoms').textContent = n.manifests_as.length ? n.manifests_as.join(', ') : "Direct Resolution Node";
      document.getElementById('node-protocols').textContent = n.resolved_by.length ? n.resolved_by.join(', ') : "Protocol Level Node";

      const citDiv = document.getElementById('node-citations');
      citDiv.innerHTML = '';
      (n.curated_citations || []).forEach(c => {{
        const card = document.createElement('div');
        card.className = 'citation-card';
        card.innerHTML = `
          <div><a href="https://www.youtube.com/watch?v=${{c.video_id}}" target="_blank">${{c.title}}</a></div>
          <div style="color: var(--text-muted); margin-top: 4px;">Channel: <strong>${{c.channel}}</strong> | Timestamps: <code>${{c.timestamp}}</code></div>
        `;
        citDiv.appendChild(card);
      }});
    }}

    function renderMatrix() {{
      const container = document.getElementById('matrix-container');
      if (container.children.length > 0) return;

      CRISES.forEach(c => {{
        const card = document.createElement('div');
        card.className = 'crisis-card';
        card.innerHTML = `
          <div class="crisis-header">
            <div>
              <span class="badge badge-2">${{c.crisis_id}}</span>
              <h3 style="margin-top: 6px;">${{c.title}}</h3>
            </div>
            <span style="font-size: 0.75rem; color: var(--text-muted);">Primitive: <code>${{c.prerequisite_primitive}}</code></span>
          </div>
          <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 12px;"><strong>Diagnosis:</strong> ${{c.clinical_diagnosis}}</p>
          <div class="callout-box" style="border-left-color: #f43f5e; margin-bottom: 16px;">
            <p><strong>⚠️ Applicability Boundary:</strong> ${{c.gap_warning}}</p>
          </div>
          <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">Triangulated Multi-Creator Protocol</div>
          ${{c.triangulated_protocol.map(s => `
            <div class="protocol-step">
              <div class="protocol-step-title">Step ${{s.step}}: ${{s.phase}} <span style="font-size: 0.75rem; color: var(--text-muted);">(${{s.authority}})</span></div>
              <p>${{s.action}}</p>
            </div>
          `).join('')}}
          <div style="margin-top: 16px;">
            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #fda4af;">Anti-Patterns to Avoid</div>
            ${{c.anti_patterns_to_avoid.map(ap => `<p class="anti-pattern">❌ ${{ap}}</p>`).join('')}}
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function renderCatalog() {{
      const list = document.getElementById('catalog-list');
      if (list.children.length > 0) return;
      list.innerHTML = '<p style="color: var(--text-muted);">See Master Markdown Compendium for complete tabular masterclass registry across all 142 videos.</p>';
    }}

    // Hook mermaid click handlers once rendered
    window.addEventListener('DOMContentLoaded', () => {{
      setTimeout(() => {{
        document.querySelectorAll('.node').forEach(nodeEl => {{
          nodeEl.style.cursor = 'pointer';
          nodeEl.addEventListener('click', () => {{
            const id = nodeEl.id.split('-')[1] || nodeEl.id;
            inspectNode(id);
          }});
        }});
      }}, 1200);
    }});
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated Interactive Visualizer at {OUTPUT_HTML} ({len(html_content):,} bytes)")

if __name__ == '__main__':
    main()
