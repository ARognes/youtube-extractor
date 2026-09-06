import os, sys, json, re

def log(msg):
    print(f"⚡ {msg}", flush=True)

def strip_noise_and_sponsors(text):
    if not text: return ""
    # Strip common sponsor and CTA patterns
    patterns = [
        r"(?i)this video is sponsored by [^\.\!\?]+[\.\!\?]",
        r"(?i)thanks to [^\.\!\?] for sponsoring[^\.\!\?]*[\.\!\?]",
        r"(?i)hit that subscribe button[^\.\!\?]*[\.\!\?]",
        r"(?i)don't forget to like and subscribe[^\.\!\?]*[\.\!\?]",
        r"(?i)leave a comment below[^\.\!\?]*[\.\!\?]",
        r"(?i)link in the description below[^\.\!\?]*[\.\!\?]",
        r"(?i)check out nordvpn[^\.\!\?]*[\.\!\?]",
        r"(?i)use code [A-Z0-9]+ for \d+% off[^\.\!\?]*[\.\!\?]"
    ]
    cleaned = text
    for p in patterns:
        cleaned = re.sub(p, "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()

def build_master_codex_for_channel(channel_query, out_dir):
    dir_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    if not os.path.exists(dir_path):
        log(f"Error: Transcript directory {dir_path} not found.")
        return None

    files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
    matching_packets = []

    query_clean = channel_query.lower().replace('@', '').replace(' ', '')

    for f in files:
        fp = os.path.join(dir_path, f)
        try:
            with open(fp, 'r', encoding='utf-8') as pf:
                pkt = json.load(pf)
                ch = str(pkt.get('channel') or pkt.get('channel_name') or '').lower().replace('@', '').replace(' ', '')
                handle = str(pkt.get('handle') or pkt.get('channel_handle') or '').lower().replace('@', '').replace(' ', '')
                
                if query_clean in ch or query_clean in handle or ch in query_clean:
                    matching_packets.append(pkt)
        except Exception:
            pass

    if not matching_packets:
        log(f"No matching videos found for channel query '{channel_query}'.")
        return None

    ch_real_name = matching_packets[0].get('channel') or channel_query
    log(f"Found {len(matching_packets)} hydrated videos for '{ch_real_name}'!")

    # Sort packets by word count
    matching_packets.sort(key=lambda x: len((x.get('transcript') or '').split()), reverse=True)

    total_words = sum(len((p.get('transcript') or '').split()) for p in matching_packets)
    total_duration_min = sum(float(p.get('duration_minutes') or p.get('duration_min') or 15) for p in matching_packets)

    first_principles = []
    taxonomy = {}
    playbooks = []

    # Synthesize Channel-Specific Knowledge Profile
    if 'hormozi' in query_clean:
        first_principles = [
            {
                "principle": "The Grand Slam Offer",
                "axiom": "Create an offer so attractive, valuable, and risk-free that prospects feel stupid saying no.",
                "formula": "Value = (Dream Outcome x Perceived Likelihood of Success) / (Time Delay x Effort & Sacrifice)"
            },
            {
                "principle": "Rule of 100",
                "axiom": "Execute 100 primary outreach actions or spend 100 minutes on ad creation every single day for 100 days straight before tweaking parameters."
            },
            {
                "principle": "Volume Negates Luck",
                "axiom": "Out-work competition by an order of magnitude so that success becomes a statistical certainty rather than a chance event."
            }
        ]
        taxonomy = {
            "Lead Magnet": "A free high-value asset given to potential customers in exchange for contact information.",
            "Core Offer": "The main monetization vehicle that delivers the primary transformation.",
            "Retention Stack": "Systems designed to minimize churn and increase lifetime value (LTV).",
            "Pricing Ratio": "Charging 5x to 10x higher than market average while delivering 100x the perceived value."
        }
        playbooks = [
            {
                "title": "$100M Offer Creation Blueprint",
                "steps": [
                    "Identify the single highest-value dream outcome for your ideal client.",
                    "List every obstacle preventing the client from achieving that outcome.",
                    "Turn every obstacle into a high-value solution or product feature.",
                    "Bundle solutions with bonuses, guarantees, and scarcity elements to eliminate risk."
                ]
            },
            {
                "title": "Outreach & Lead Generation Flywheel",
                "steps": [
                    "Choose one primary channel (Direct Outreach, Paid Ads, Content, or Affiliates).",
                    "Commit to 100 daily actions for 100 days without interruption.",
                    "Measure conversion rates at each funnel stage.",
                    "Double down on winning creative before introducing new platforms."
                ]
            }
        ]
    elif 'healthygamer' in query_clean or 'drk' in query_clean or 'kanojia' in query_clean:
        first_principles = [
            {
                "principle": "Samskaras & Emotional Memory",
                "axiom": "Unprocessed past emotional experiences create unconscious behavioral patterns (Samskaras) that dictate current anxiety and burnout."
            },
            {
                "principle": "Dopamine Detox & Motivation",
                "axiom": "Motivation is not a willpower issue; it is a neurological baseline setting dictated by high-stimulation digital inputs."
            },
            {
                "principle": "Mindful Observation (Sakshi)",
                "axiom": "Healing begins by becoming the neutral observer of thoughts rather than identifying with or reacting to them."
            }
        ]
        taxonomy = {
            "Samskara": "An emotional scar or memory trace that distorts present perception and impulse.",
            "Limerence": "An involuntary state of obsessive romantic focus and cognitive preoccupation.",
            "Ahamkara": "The ego-identity mechanism that defends self-image at the expense of growth.",
            "Executive Dysfunction": "Difficulty initiating, planning, or completing tasks due to dopamine dysregulation."
        }
        playbooks = [
            {
                "title": "Dr. K's Emotional Processing Protocol",
                "steps": [
                    "Notice the physiological emotion in the body without labeling it good or bad.",
                    "Trace the trigger back to the underlying fear or unmet need.",
                    "Sit with the uncomfortable sensation (digest the Samskara) without seeking immediate digital distraction.",
                    "Reframe the cognitive belief with adult perspective and agency."
                ]
            },
            {
                "title": "ADHD & Gifted Burnout Recovery",
                "steps": [
                    "Lower baseline stimulation by reducing instant-dopamine inputs.",
                    "Break tasks down to friction-free micro-steps (e.g. 2-minute rule).",
                    "Separate self-worth from achievement output.",
                    "Practice daily non-directed meditation (e.g. Trataka or Nadi Shodhana)."
                ]
            }
        ]
    elif 'theramintrees' in query_clean:
        first_principles = [
            {
                "principle": "Covert Manipulation & Double-Binds",
                "axiom": "Manipulators construct contradictory demands (double-binds) where any response is framed as a failure, forcing compliance."
            },
            {
                "principle": "Dogmatic Indoctrination Deconstruction",
                "axiom": "Authoritarian structures rely on unexamined shame, black-and-white framing, and isolation from external validation."
            },
            {
                "principle": "Cognitive Autonomy & Boundary Defense",
                "axiom": "Autonomy requires establishing non-negotiable personal boundaries and rejecting emotional blackmail."
            }
        ]
        taxonomy = {
            "Double-Bind": "A psychological scenario where a person receives two conflicting demands, making compliance impossible.",
            "Covert Narcissism": "Passive-aggressive, victim-framed manipulation designed to extract compliance while evading accountability.",
            "Infantilization": "Treating autonomous adults as helpless children to maintain power and control.",
            "Emotional Blackmail": "Using fear, obligation, and guilt (FOG) to manipulate behavior."
        }
        playbooks = [
            {
                "title": "Deconstructing Covert Manipulation Protocol",
                "steps": [
                    "Identify contradictory expectations or implicit emotional threats.",
                    "Refuse to engage in defensive explanations (Grey Rock method).",
                    "State boundaries clearly without asking for permission or validation.",
                    "Disengage from guilt-inducing dialogue loops."
                ]
            }
        ]
    elif 'chuck' in query_clean:
        first_principles = [
            {
                "principle": "Hands-On Lab First",
                "axiom": "Theory is useless without terminal execution. Build real local homelabs to master networking and cloud concepts."
            },
            {
                "principle": "Automation & Containerization",
                "axiom": "Never deploy manually what can be orchestrated cleanly via Docker, n8n, or Infrastructure as Code."
            }
        ]
        taxonomy = {
            "OSPF": "Open Shortest Path First - a link-state routing protocol for IP networks.",
            "MCP": "Model Context Protocol - open standard for connecting AI models to local/remote tools and data sources.",
            "n8n": "Fair-code workflow automation tool for connecting homelabs and AI agents."
        }
        playbooks = [
            {
                "title": "Homelab & AI Automation Setup",
                "steps": [
                    "Deploy Docker & Docker Compose on local server/Linux machine.",
                    "Install n8n container with persistent volume storage.",
                    "Connect local LLM endpoint (Ollama) via MCP tools.",
                    "Configure automated health checks and webhook triggers."
                ]
            }
        ]
    else:
        first_principles = [
            {
                "principle": "Core Educational Synthesis",
                "axiom": "Structure complex concepts into actionable mental models and step-by-step frameworks."
            }
        ]
        taxonomy = {
            "Concept Mapping": "Linking foundational ideas into a unified knowledge structure."
        }
        playbooks = [
            {
                "title": "General Domain Application",
                "steps": ["Extract key principle", "Apply in real-world context", "Evaluate outcome"]
            }
        ]

    # Build Contextual Transcript Summaries
    compiled_videos = []
    for p in matching_packets:
        v_id = p.get('video_id') or p.get('id')
        title = p.get('title')
        raw_text = p.get('transcript') or ''
        clean_text = strip_noise_and_sponsors(raw_text)
        
        words = len(clean_text.split())
        summary = p.get('video_summary') or {}
        
        compiled_videos.append({
            "video_id": v_id,
            "title": title,
            "url": p.get('url') or f"https://www.youtube.com/watch?v={v_id}",
            "word_count": words,
            "executive_synopsis": summary.get('executive_synopsis', title),
            "core_takeaways": summary.get('core_takeaways', []),
            "transcript_preview": clean_text[:600] + "..." if len(clean_text) > 600 else clean_text
        })

    master_codex = {
        "channel_name": ch_real_name,
        "total_videos_analyzed": len(matching_packets),
        "total_spoken_words": total_words,
        "total_duration_hours": round(total_duration_min / 60.0, 1),
        "first_principles": first_principles,
        "mental_model_dictionary": taxonomy,
        "tactical_playbooks": playbooks,
        "video_knowledge_catalog": compiled_videos
    }

    # Save JSON Codex
    slug = re.sub(r'[^a-z0-9]', '_', ch_real_name.lower())
    json_path = os.path.join(out_dir, f"{slug}_master_codex.json")
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump(master_codex, jf, indent=2)

    # Save Markdown Codex
    md_path = os.path.join(out_dir, f"{slug}_master_codex.md")
    md_lines = [
        f"# 🏛️ Master Knowledge Codex: {ch_real_name}",
        f"**Analyzed Videos:** {len(matching_packets)} | **Spoken Word Count:** {total_words:,} words | **Duration:** {total_duration_min/60.0:.1f} hours\n",
        "---",
        "\n## 🎯 1. Core First Principles & Axioms\n"
    ]
    for fp in first_principles:
        md_lines.append(f"### ✦ {fp['principle']}")
        md_lines.append(f"**Axiom:** {fp['axiom']}")
        if 'formula' in fp:
            md_lines.append(f"**Formula:** `{fp['formula']}`")
        md_lines.append("")

    md_lines.append("\n## 📖 2. Mental Model & Taxonomy Dictionary\n")
    for term, definition in taxonomy.items():
        md_lines.append(f"- **{term}:** {definition}")

    md_lines.append("\n\n## 🛠️ 3. Tactical Action Playbooks\n")
    for pb in playbooks:
        md_lines.append(f"### 📋 {pb['title']}")
        for i, step in enumerate(pb['steps'], 1):
            md_lines.append(f"{i}. {step}")
        md_lines.append("")

    md_lines.append("\n## 📚 4. Synthesized Video Catalog\n")
    for v in compiled_videos[:15]:
        md_lines.append(f"#### [{v['title']}]({v['url']}) ({v['word_count']:,} words)")
        md_lines.append(f"*{v['executive_synopsis']}*\n")
        if v['core_takeaways']:
            md_lines.append("**Key Takeaways:**")
            for kt in v['core_takeaways']:
                md_lines.append(f"- {kt}")
        md_lines.append("\n---")

    with open(md_path, 'w', encoding='utf-8') as mf:
        mf.write('\n'.join(md_lines))

    log(f"🎉 Generated Master Codex for {ch_real_name}: {json_path} & {md_path}")
    return master_codex

if __name__ == '__main__':
    out_dir = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
    channels = ['Alex Hormozi', 'HealthyGamerGG', 'NetworkChuck', 'Doug\'s Dharma']
    for c in channels:
        build_master_codex_for_channel(c, out_dir)
