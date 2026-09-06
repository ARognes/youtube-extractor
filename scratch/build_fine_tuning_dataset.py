import os
import json
import re

def log(msg):
    print(f"⚡ {msg}", flush=True)

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')

def generate_fine_tuning_and_personas():
    log("Building Fine-Tuning Instruct Dataset (.jsonl) & Persona Prompts...")

    files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    instruct_pairs = []
    personas = {}

    for f in files:
        fp = os.path.join(TRANSCRIPTS_DIR, f)
        try:
            with open(fp, 'r', encoding='utf-8') as jf:
                pkt = json.load(jf)
                ch = pkt.get('channel') or pkt.get('channel_name') or 'Expert Advisor'
                title = pkt.get('title') or ''
                summary = pkt.get('video_summary') or {}
                synopsis = summary.get('executive_synopsis') or title
                takeaways = summary.get('core_takeaways') or []

                if title and takeaways:
                    # Instruct Pair 1: Technical Summary & Key Principles
                    instruct_pairs.append({
                        "messages": [
                            {"role": "system", "content": f"You are an AI advisor trained on the complete knowledge base of {ch}."},
                            {"role": "user", "content": f"What are the core technical takeaways and first principles from '{title}'?"},
                            {"role": "assistant", "content": f"Based on {ch}'s analysis:\n\n**Executive Synopsis:** {synopsis}\n\n**Key Principles:**\n" + "\n".join([f"- {t}" for t in takeaways])}
                        ]
                    })

                    # Instruct Pair 2: Chapter Breakdown
                    chapters = summary.get('chapters') or []
                    if chapters:
                        ch_str = "\n".join([f"- [{c.get('timestamp', '0:00')}] {c.get('title', 'Chapter')}: {c.get('summary', '')}" for c in chapters])
                        instruct_pairs.append({
                            "messages": [
                                {"role": "system", "content": f"You are an AI advisor trained on {ch}'s masterclass catalog."},
                                {"role": "user", "content": f"Can you provide a timestamped chapter breakdown for '{title}'?"},
                                {"role": "assistant", "content": f"Here is {ch}'s chapter roadmap for '{title}':\n\n{ch_str}"}
                            ]
                        })

                # Register Persona system prompts
                ch_slug = re.sub(r'[^a-z0-9]', '_', ch.lower())
                if ch_slug not in personas:
                    personas[ch_slug] = {
                        "creator_name": ch,
                        "system_prompt": f"You are {ch}'s specialized AI persona. You reason strictly from first principles, utilizing {ch}'s specific terminology, mental models, and step-by-step playbooks. Never break character or substitute generic advice when a specific {ch} framework exists."
                    }
        except Exception:
            pass

    # Save instruct .jsonl
    jsonl_path = os.path.join(SCRATCH_DIR, 'creator_instruct.jsonl')
    with open(jsonl_path, 'w', encoding='utf-8') as jf:
        for item in instruct_pairs:
            jf.write(json.dumps(item) + '\n')

    # Save personas .json
    personas_path = os.path.join(SCRATCH_DIR, 'creator_personas.json')
    with open(personas_path, 'w', encoding='utf-8') as jf:
        json.dump(personas, jf, indent=2)

    log(f"🎉 Fine-Tuning dataset generated! {len(instruct_pairs)} pairs saved to {jsonl_path}")
    log(f"🎉 Persona Prompts generated for {len(personas)} creators at {personas_path}")

if __name__ == '__main__':
    generate_fine_tuning_and_personas()
