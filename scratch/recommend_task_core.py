import os
import sys
import json
import re

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'

CORE_KEYWORDS = {
    "core_software_engineering": ["code", "coding", "rust", "vim", "web", "api", "software", "algorithm", "python", "javascript", "typescript", "css"],
    "core_cognitive_psychology": ["anxiety", "burnout", "adhd", "dopamine", "mind", "psychology", "emotion", "limerence", "dr k", "samskara"],
    "core_business_monetization": ["offer", "pricing", "business", "monetization", "lead", "hormozi", "sales", "revenue", "scale", "ferriss"],
    "core_science_philosophy": ["physics", "quantum", "science", "jung", "stoic", "nietzsche", "philosophy", "climate", "sabine"],
    "core_cybersecurity_homelab": ["docker", "homelab", "n8n", "network", "cybersecurity", "security", "exploit", "usb", "terminal", "linux"],
    "core_pali_philosophy": ["pali", "sutta", "buddhist", "buddhism", "meditation", "dhharma", "doug"]
}

def recommend_core_for_prompt(prompt):
    p_clean = prompt.lower()
    scores = {}

    for cid, keywords in CORE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in p_clean)
        scores[cid] = score

    sorted_cores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    recommended = [c[0] for c in sorted_cores if c[1] > 0]

    if not recommended:
        recommended = ["core_software_engineering", "core_business_monetization"]

    return {
        "prompt": prompt,
        "recommended_cores": recommended,
        "suggested_compression_tier": 2 if len(recommended) > 1 else 1,
        "confidence_scores": scores
    }

if __name__ == '__main__':
    prompt_test = "How do I price my SaaS product and configure Docker containers?"
    res = recommend_core_for_prompt(prompt_test)
    print(json.dumps(res, indent=2))
