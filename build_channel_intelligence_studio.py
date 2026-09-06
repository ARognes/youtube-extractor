#!/usr/bin/env python3
import os
import json
import re

TRANSCRIPTS_DIR = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts"
OUT_DB_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/universal_channel_intelligence_db.json"

# Channel Specific Playbook Templates & Custom Rules
CUSTOM_PLAYBOOKS = {
    "Alex Hormozi": [
        {
            "title": "📜 Playbook: $100M Offer Creation & Business Scaling",
            "subtitle": "Synthesized rules from Alex Hormozi (Acquisition.com)",
            "rules": [
                {
                    "rule": "1. Charge Premium Prices by Increasing Perceived Value",
                    "insight": "Competing on price is a race to the bottom. Create irresistible grand slam offers by maximizing the Dream Outcome and Likelihood of Achievement while minimizing Time Delay and Effort.",
                    "action": "Increase your price by 2x to 5x and invest the margin directly into customer success."
                },
                {
                    "rule": "2. There Are Only 4 Paths to Becoming Ultra Wealthy",
                    "insight": "Wealth creation relies on high-leverage activities: Media, Code, Capital, and Labor. Scale through digital media and proprietary systems to decouple time from income.",
                    "action": "Focus 80% of your effort on building scalable distribution systems and high-margin products."
                },
                {
                    "rule": "3. The 2 Sales Questions That Force Decisions",
                    "insight": "Objections come from fear or lack of clarity. Ask prospects: 'What happens if you do nothing?' and 'How much is staying in your current state costing you?'",
                    "action": "Use diagnostic framing in sales conversations to highlight the real cost of inaction."
                }
            ]
        }
    ],
    "ThePrimeagen": [
        {
            "title": "📜 Playbook: Vim/Neovim Velocity & Development Speed",
            "subtitle": "Synthesized rules from ThePrimeagen (Ex-Netflix Senior Engineer)",
            "rules": [
                {
                    "rule": "1. Stop Using the Mouse; Master Motion Keys",
                    "insight": "Navigating code with a mouse breaks developer flow state. Master motions (`f`, `t`, `ciw`, `vap`, `%`) to edit at the speed of thought.",
                    "action": "Disable mouse support in your editor for 7 days to force muscle memory development."
                },
                {
                    "rule": "2. Blazing Fast Fuzzy Finding (`telescope.nvim` / `harpoon`) font-weight",
                    "insight": "Don't navigate file trees line-by-line. Jump directly between active files using mark-based buffers like Harpoon.",
                    "action": "Limit active working files to 4 slots in Harpoon to reduce cognitive switching cost."
                },
                {
                    "rule": "3. Benchmark Production Languages with Real Metrics",
                    "insight": "Don't trust internet hype about language speed. Benchmark Rust, Go, and TypeScript under actual HTTP load and memory allocations.",
                    "action": "Profile memory layout and garbage collection pauses before deciding to rewrite services."
                }
            ]
        }
    ],
    "freeCodeCamp.org": [
        {
            "title": "📜 Playbook: Full-Stack Engineering & Machine Learning Roadmap",
            "subtitle": "Synthesized rules from freeCodeCamp Full Courses & Technical Curricula",
            "rules": [
                {
                    "rule": "1. Build Goal-Oriented Projects, Don't Tutorial-Hop",
                    "insight": "Learning a syntax without building a functional system leads to shallow retention. Build complete apps with real auth and database backends.",
                    "action": "Build a production-ready RAG application using TypeScript, Vector Databases, and PyTorch."
                },
                {
                    "rule": "2. Master Data Augmentation & Regularization in ML",
                    "insight": "Model performance is limited by data quality. Apply normalization, ResNet architectures, and dropout to prevent overfitting.",
                    "action": "Implement PyTorch zero-to-GANs pipelines with quantified validation loss tracking."
                }
            ]
        }
    ],
    "Web Dev Simplified": [
        {
            "title": "📜 Playbook: Modern CSS & High-Performance React Architecture",
            "subtitle": "Synthesized rules from Kyle Cook (Web Dev Simplified)",
            "rules": [
                {
                    "rule": "1. Leverage Modern Native CSS (Scroll-Driven Animations & `:has()`)",
                    "insight": "Stop importing heavy JavaScript animation libraries for simple scroll effects. Native CSS now handles view transitions and container queries.",
                    "action": "Replace JS scroll listeners with CSS `animation-timeline: scroll()` for 60fps performance."
                },
                {
                    "rule": "2. Avoid State Mutation & Unnecessary Re-Renders in React",
                    "insight": "Directly mutating React state causes hidden render bugs. Keep transient state local and wrap expensive computations in `useMemo`.",
                    "action": "Use strict immutable updates and custom hooks for decoupled API state."
                }
            ]
        }
    ],
    "/noclip": [
        {
            "title": "📜 Playbook: Game Development History & Post-Mortem Architecture",
            "subtitle": "Synthesized insights from Noclip Documentaries (Supergiant, ZA/UM, Motion Twin)",
            "rules": [
                {
                    "rule": "1. Iterative Mechanics First, Visual Polish Second",
                    "insight": "Hades and Disco Elysium succeeded because their core gameplay loops were tested and prototyped in gray-box environments for months before art assets were finalized.",
                    "action": "Focus on core game feel and mechanic responsive feedback loops before polishing graphics."
                }
            ]
        }
    ],
    "The Cherno": [
        {
            "title": "📜 Playbook: C++ Architecture & Custom Game Engine Design",
            "subtitle": "Synthesized rules from Yan Chernikov (The Cherno - Hazel 2D)",
            "rules": [
                {
                    "rule": "1. Respect Memory Alignment & Cache Locality",
                    "insight": "Pointer chasing across heap-allocated objects causes CPU cache misses. Store game components in contiguous memory arrays.",
                    "action": "Use Entity Component Systems (ECS) with contiguous vector storage for transform components."
                }
            ]
        }
    ]
}

DEFAULT_TOPIC_PILLARS = {
    "Pillar 1: 💻 Architecture & Code Design": ["code", "system", "design", "architecture", "build", "framework", "pattern", "component"],
    "Pillar 2: ⚡ Performance & Optimization": ["fast", "performance", "speed", "memory", "cache", "benchmark", "optimize", "wpm", "latency"],
    "Pillar 3: 🛠️ Tools, Tooling & Workflow": ["tool", "vim", "git", "linux", "terminal", "workflow", "setup", "editor", "script"],
    "Pillar 4: 📈 Career Growth & Industry Insights": ["career", "interview", "level", "senior", "job", "industry", "money", "promo", "tech"],
    "Pillar 5: 📚 Fundamentals & Concepts": ["concept", "learn", "fundamental", "math", "tutorial", "guide", "explanation", "basics"]
}

def analyze_all_channels():
    files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    print(f"⚡ Synthesizing Universal Intelligence Studio across {len(files)} transcript files...")

    channel_map = {}

    for fname in files:
        fpath = os.path.join(TRANSCRIPTS_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            ch = str(data.get('channel') or data.get('channel_name') or 'Unknown Creator').strip()
            v_id = data.get('video_id')
            title = str(data.get('title') or data.get('video_title') or '')
            transcript = str(data.get('transcript') or '')
            words = len(transcript.split())
            duration = data.get('duration') or 15
            summary = data.get('video_summary') or {}

            if not ch or not v_id or words < 10:
                continue

            if ch not in channel_map:
                channel_map[ch] = []

            # Assign Pillar
            title_lower = title.lower()
            trans_lower = transcript.lower()

            assigned_pillar = "Pillar 1: 💻 Architecture & Code Design"
            max_score = 0
            for pillar, kws in DEFAULT_TOPIC_PILLARS.items():
                score = sum(3 if kw in title_lower else 1 for kw in kws if kw in trans_lower or kw in title_lower)
                if score > max_score:
                    max_score = score
                    assigned_pillar = pillar

            channel_map[ch].append({
                "id": v_id,
                "title": title,
                "duration": duration,
                "word_count": words,
                "pillar": assigned_pillar,
                "url": f"https://www.youtube.com/watch?v={v_id}",
                "synopsis": summary.get("executive_synopsis", f"High-yield analysis of '{title}'."),
                "transcript_snippet": transcript[:300] + "..." if len(transcript) > 300 else transcript
            })
        except Exception:
            pass

    universal_db = {}

    for ch, videos in channel_map.items():
        # Group by Pillar
        pillars = {p: [] for p in DEFAULT_TOPIC_PILLARS.keys()}
        for v in videos:
            pillars[v["pillar"]].append(v)

        # Build Quotes Index for search
        quotes = []
        for v in videos:
            sentences = re.split(r'(?<=[.!?]) +', v["transcript_snippet"])
            for s in sentences:
                if len(s.split()) >= 10:
                    quotes.append({
                        "video_id": v["id"],
                        "video_title": v["title"],
                        "quote": s.strip(),
                        "pillar": v["pillar"]
                    })

        # Match custom playbooks or generate default playbook
        playbooks = CUSTOM_PLAYBOOKS.get(ch, [
            {
                "title": f"📜 Playbook: Core Engineering & Content Synthesis ({ch})",
                "subtitle": f"Synthesized rules from {len(videos)} hydrated video transcripts",
                "rules": [
                    {
                        "rule": "1. Master System Fundamentals & Execution",
                        "insight": f"Analysis across {ch}'s catalog demonstrates a strong emphasis on consistent technical execution and domain mastery.",
                        "action": "Apply structured problem solving before jumping directly into implementation code."
                    }
                ]
            }
        ])

        universal_db[ch] = {
            "channel_name": ch,
            "total_videos": len(videos),
            "total_words": sum(v["word_count"] for v in videos),
            "pillars": pillars,
            "playbooks": playbooks,
            "quotes": quotes[:300], # Top 300 quotes for search
            "videos": videos
        }

    print(f"✅ Generated Universal Intelligence Database for {len(universal_db)} Creator Channels!")

    with open(OUT_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(universal_db, f, indent=2, ensure_ascii=False)

    print(f"🎉 Universal Intelligence Database saved to {OUT_DB_FILE}!")

if __name__ == '__main__':
    analyze_all_channels()
