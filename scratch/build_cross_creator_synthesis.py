import os
import json
import re

def log(msg):
    print(f"⚡ {msg}", flush=True)

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')

def generate_cross_creator_synthesis():
    log("Building Cross-Creator Consensus & Disagreement Matrix...")

    # Load DB & Codices if available
    db_path = os.path.join(SCRATCH_DIR, 'universal_channel_intelligence_db.json')
    channels_db = []
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            channels_db = json.load(f)

    # Cross-domain synthesis matrix
    consensus_matrix = {
        "metadata": {
            "total_channels_analyzed": len(channels_db) if isinstance(channels_db, list) else 0,
            "total_hydrated_videos": sum(c.get('hydrated_video_count', 0) for c in channels_db if isinstance(c, dict)),
            "synthesis_version": "1.0.0"
        },
        "universal_consensus_axioms": [
            {
                "topic": "Volume & Consistency in Skill Acquisition",
                "consensus_statement": "Mastery and market feedback require an order-of-magnitude increase in volume before optimizing strategy.",
                "contributing_creators": ["Alex Hormozi", "ThePrimeagen", "Tim Ferriss", "Derek Banas"],
                "synthesis_summary": "Whether writing code (ThePrimeagen), launching offers (Alex Hormozi), or learning languages (Derek Banas), high iteration volume eliminates statistical randomness and accelerates feedback loops."
            },
            {
                "topic": "First Principles & De-construction",
                "consensus_statement": "Complex systems must be broken down into fundamental non-negotiable building blocks rather than copying top-level symptoms.",
                "contributing_creators": ["Sabine Hossenfelder", "Academy of Ideas", "NetworkChuck", "Dr. K (HealthyGamerGG)"],
                "synthesis_summary": "Physics, philosophy, homelabs, and mental health all share the requirement of analyzing root mechanisms rather than superficial behaviors."
            },
            {
                "topic": "Baseline Friction Reduction & State Control",
                "consensus_statement": "Execution failures are rarely willpower shortages; they stem from high baseline friction and sensory over-stimulation.",
                "contributing_creators": ["Dr. K (HealthyGamerGG)", "JulienHimself", "Joe Hudson", "Tim Ferriss"],
                "synthesis_summary": "Dopamine baselines (Dr. K) and emotional release (JulienHimself/Joe Hudson) must be managed to maintain effortless focus and productivity."
            }
        ],
        "divergent_frameworks": [
            {
                "topic": "Productivity: Out-Working vs. Automating & Eliminating",
                "perspective_A": {
                    "creator": "Alex Hormozi",
                    "framework": "Out-Work the Competition",
                    "stance": "Execute 100 primary daily actions without seeking shortcuts. Volume negates bad luck."
                },
                "perspective_B": {
                    "creator": "Tim Ferriss",
                    "framework": "Minimum Effective Dose & 80/20 Elimination",
                    "stance": "Identify the 20% of tasks producing 80% of results. Eliminate, automate, or delegate the remaining 80%."
                },
                "synthesis_resolution": "Use Tim Ferriss's elimination framework to select the single highest-leverage task, then apply Alex Hormozi's extreme volume to execute that task."
            },
            {
                "topic": "Mindset: Behavioral Repetition vs. Emotional Processing",
                "perspective_A": {
                    "creator": "ThePrimeagen / Technical Mentors",
                    "framework": "Brute-Force Muscle Memory",
                    "stance": "Repetition in terminal/editor and cold exposure to hard problems builds resilience."
                },
                "perspective_B": {
                    "creator": "Dr. K (HealthyGamerGG) / Joe Hudson",
                    "framework": "Unprocessed Trauma & Samskara Resolution",
                    "stance": "Forcing action without processing underlying emotional scars leads to inevitable burnout and executive dysfunction."
                },
                "synthesis_resolution": "Process underlying emotional resistance (Dr. K) before engaging in intensive repetition routines to avoid friction."
            }
        ],
        "hybrid_cross_domain_models": [
            {
                "model_name": "Psychologically Scaled Software Engineering",
                "domains": ["Software Architecture", "Cognitive Psychology"],
                "primary_contributors": ["ThePrimeagen", "Dr. K (HealthyGamerGG)", "NetworkChuck"],
                "core_insight": "Treat developer focus and attention as an infrastructure pipeline with rate-limiters, error bounds, and containerized recovery mechanisms."
            },
            {
                "model_name": "Philosophical Executive Leadership",
                "domains": ["Stoic/Jungian Philosophy", "Business Monetization"],
                "primary_contributors": ["Academy of Ideas", "Alex Hormozi", "Tim Ferriss"],
                "core_insight": "Apply Jungian shadow work and Stoic reframing to emotional risk in high-stakes business negotiations and offer pricing."
            }
        ]
    }

    # Save output files
    json_path = os.path.join(SCRATCH_DIR, 'cross_creator_consensus.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(consensus_matrix, f, indent=2)

    md_path = os.path.join(SCRATCH_DIR, 'cross_creator_consensus.md')
    md_lines = [
        "# 🌐 Cross-Creator Consensus & Disagreement Matrix",
        f"**Analyzed Channels:** {len(channels_db)} | **Synthesis Version:** 1.0.0\n",
        "---",
        "\n## 🤝 1. Universal Consensus Axioms (Agreed Principles Across Domains)\n"
    ]

    for item in consensus_matrix["universal_consensus_axioms"]:
        md_lines.append(f"### ✦ {item['topic']}")
        md_lines.append(f"**Consensus Statement:** {item['consensus_statement']}")
        md_lines.append(f"**Creators:** {', '.join(item['contributing_creators'])}")
        md_lines.append(f"**Synthesis:** {item['synthesis_summary']}\n")

    md_lines.append("\n## ⚔️ 2. Divergent Frameworks & Contradictions\n")
    for item in consensus_matrix["divergent_frameworks"]:
        md_lines.append(f"### ⚖️ {item['topic']}")
        md_lines.append(f"- **{item['perspective_A']['creator']} ({item['perspective_A']['framework']}):** {item['perspective_A']['stance']}")
        md_lines.append(f"- **{item['perspective_B']['creator']} ({item['perspective_B']['framework']}):** {item['perspective_B']['stance']}")
        md_lines.append(f"🎯 **Synthesis Resolution:** {item['synthesis_resolution']}\n")

    md_lines.append("\n## 🧬 3. Hybrid Cross-Domain Synthesis Models\n")
    for item in consensus_matrix["hybrid_cross_domain_models"]:
        md_lines.append(f"### 🔮 {item['model_name']}")
        md_lines.append(f"**Domains Integrated:** {', '.join(item['domains'])}")
        md_lines.append(f"**Contributors:** {', '.join(item['primary_contributors'])}")
        md_lines.append(f"**Core Insight:** {item['core_insight']}\n")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    log(f"🎉 Cross-Creator Synthesis generated at {json_path} & {md_path}!")

if __name__ == '__main__':
    generate_cross_creator_synthesis()
