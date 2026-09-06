#!/usr/bin/env python3
"""
build_entity_index.py

Extracts and indexes concrete software tools, programming languages,
libraries, philosophers, authors, and frameworks across all 1,740 formatted
transcripts, outputting `taxonomy/entity_index.yaml`.
"""

import os
import re
import bisect
import yaml
from collections import defaultdict

try:
    from yaml import CSafeDumper as Dumper, CSafeLoader as Loader
except ImportError:
    from yaml import SafeDumper as Dumper, SafeLoader as Loader

FORMATTED_DIR = "formatted_transcripts"
OUTPUT_FILE = "taxonomy/entity_index.yaml"

# Curated catalog of recognized entities with display names and categories
ENTITIES_CATALOG = {
    # Programming Languages
    "rust": ("Rust", "programming_languages"),
    "python": ("Python", "programming_languages"),
    "javascript": ("JavaScript", "programming_languages"),
    "typescript": ("TypeScript", "programming_languages"),
    "golang|\\bgo\\s+language|\\bgo\\s+code": ("Go", "programming_languages"),
    "c\\+\\+": ("C++", "programming_languages"),
    "zig": ("Zig", "programming_languages"),
    "bash": ("Bash", "programming_languages"),
    "sql": ("SQL", "programming_languages"),
    
    # Frameworks & Libraries
    "react": ("React", "frameworks_libraries"),
    "next\\.?js": ("Next.js", "frameworks_libraries"),
    "vue\\.?js|\\bvue\\b": ("Vue.js", "frameworks_libraries"),
    "svelte": ("Svelte", "frameworks_libraries"),
    "tailwind(?:css)?": ("Tailwind CSS", "frameworks_libraries"),
    "node\\.?js": ("Node.js", "frameworks_libraries"),
    "pytorch": ("PyTorch", "frameworks_libraries"),
    "tensorflow": ("TensorFlow", "frameworks_libraries"),

    # Dev Tools & Operating Systems
    "docker": ("Docker", "tools_infrastructure"),
    "kubernetes|k8s": ("Kubernetes", "tools_infrastructure"),
    "neovim|\\bnvim\\b": ("Neovim", "tools_infrastructure"),
    "\\bvim\\b": ("Vim", "tools_infrastructure"),
    "vs\\s*code|visual\\s*studio\\s*code": ("VS Code", "tools_infrastructure"),
    "linux": ("Linux", "tools_infrastructure"),
    "ubuntu": ("Ubuntu", "tools_infrastructure"),
    "arch\\s*linux": ("Arch Linux", "tools_infrastructure"),
    "git\\b": ("Git", "tools_infrastructure"),
    "github": ("GitHub", "tools_infrastructure"),
    "cloudflare": ("Cloudflare", "tools_infrastructure"),
    "aws|amazon\\s*web\\s*services": ("AWS", "tools_infrastructure"),

    # Databases & Storage
    "postgresql|postgres": ("PostgreSQL", "databases_storage"),
    "redis": ("Redis", "databases_storage"),
    "mongodb": ("MongoDB", "databases_storage"),
    "sqlite": ("SQLite", "databases_storage"),

    # Networking & Cybersecurity
    "wireshark": ("Wireshark", "networking_cybersecurity"),
    "raspberry\\s*pi": ("Raspberry Pi", "networking_cybersecurity"),
    "vpn": ("VPN", "networking_cybersecurity"),
    "wireguard": ("WireGuard", "networking_cybersecurity"),
    "firewall": ("Firewall", "networking_cybersecurity"),
    "dns": ("DNS", "networking_cybersecurity"),
    "bgp": ("BGP", "networking_cybersecurity"),
    "vlan": ("VLAN", "networking_cybersecurity"),
    "subdomain": ("Subdomain", "networking_cybersecurity"),

    # Philosophers, Thinkers & Authors
    "nietzsche": ("Friedrich Nietzsche", "thinkers_authors"),
    "carl\\s*jung|\\bjung\\b": ("Carl Jung", "thinkers_authors"),
    "marcus\\s*aurelius": ("Marcus Aurelius", "thinkers_authors"),
    "epictetus": ("Epictetus", "thinkers_authors"),
    "seneca": ("Seneca", "thinkers_authors"),
    "siddhartha|gautama\\s*buddha|the\\s*buddha": ("The Buddha", "thinkers_authors"),
    "alan\\s*watts": ("Alan Watts", "thinkers_authors"),
    "andrew\\s*huberman|huberman": ("Andrew Huberman", "thinkers_authors"),
    "alex\\s*hormozi|hormozi": ("Alex Hormozi", "thinkers_authors"),
    "tim\\s*ferriss": ("Tim Ferriss", "thinkers_authors"),

    # Business & Productivity Frameworks
    "rule\\s*of\\s*100": ("Rule of 100", "business_productivity"),
    "100m\\s*offers|\\$100m\\s*offers": ("$100M Offers", "business_productivity"),
    "atomic\\s*habits": ("Atomic Habits", "business_productivity"),
    "four\\s*hour\\s*workweek|4\\s*hour\\s*workweek": ("4-Hour Workweek", "business_productivity"),
    "deep\\s*work": ("Deep Work", "business_productivity"),
    "samskara": ("Samskara", "psychology_frameworks"),
    "dopamine\\s*detox": ("Dopamine Detox", "psychology_frameworks")
}


def find_timestamp(timestamps, char_index, text=""):
    if timestamps:
        keys = [item[0] for item in timestamps]
        idx = bisect.bisect_right(keys, char_index) - 1
        if idx >= 0:
            return timestamps[idx][1]
    if text:
        prefix = text[:char_index]
        inline_matches = list(re.finditer(r'\[(\d+(?:\.\d+)?)s?\]', prefix))
        if inline_matches:
            return int(round(float(inline_matches[-1].group(1))))
        ts_matches = list(re.finditer(r'\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b', prefix))
        if ts_matches:
            m = ts_matches[-1]
            if m.group(3):
                return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            return int(m.group(1)) * 60 + int(m.group(2))
    return 0


def build_jump_url(base_url, seconds, video_id):
    if not base_url and video_id:
        base_url = f"https://www.youtube.com/watch?v={video_id}"
    if not base_url:
        return ""
    clean_url = re.sub(r'[?&]t=\d+s?', '', base_url)
    sep = "&" if "?" in clean_url else "?"
    return f"{clean_url}{sep}t={seconds}s"


def extract_context(text, start, end, radius=70):
    s = max(0, start - radius)
    e = min(len(text), end + radius)
    snippet = ("..." if s > 0 else "") + text[s:e].replace('\n', ' ') + ("..." if e < len(text) else "")
    return snippet.strip()


def main():
    print("🏗️  Scanning transcripts to build Entity & Tool Index...")
    files = sorted([f for f in os.listdir(FORMATTED_DIR) if f.endswith('.yaml')])

    # Precompile regexes
    compiled_entities = []
    for pattern, (display_name, category) in ENTITIES_CATALOG.items():
        rx = re.compile(rf'\b(?:{pattern})\b', re.IGNORECASE)
        compiled_entities.append((display_name, category, rx))

    entity_results = defaultdict(lambda: {
        'display_name': '',
        'category': '',
        'total_mentions': 0,
        'channel_counts': defaultdict(int),
        'sample_cues': []
    })

    for idx, f in enumerate(files, 1):
        fpath = os.path.join(FORMATTED_DIR, f)
        with open(fpath, 'r', encoding='utf-8') as fp:
            doc = yaml.load(fp, Loader=Loader)

        transcript = doc.get('transcript', '')
        if not transcript:
            continue

        timestamps = doc.get('timestamps', [])
        channel = doc.get('channel', 'Unknown')
        video_id = doc.get('video_id', '')
        title = doc.get('title', '')
        url = doc.get('url', '')

        for display_name, category, rx in compiled_entities:
            matches = list(rx.finditer(transcript))
            if not matches:
                continue

            entry = entity_results[display_name]
            entry['display_name'] = display_name
            entry['category'] = category
            entry['total_mentions'] += len(matches)
            entry['channel_counts'][channel] += len(matches)

            # Record up to 3 sample cues per entity across files
            if len(entry['sample_cues']) < 5:
                first_match = matches[0]
                m_start = first_match.start()
                m_end = first_match.end()
                sec = find_timestamp(timestamps, m_start, transcript)
                jump_url = build_jump_url(url, sec, video_id)
                context = extract_context(transcript, m_start, m_end)

                entry['sample_cues'].append({
                    'video_id': video_id,
                    'title': title,
                    'channel': channel,
                    'timestamp_sec': sec,
                    'context': context,
                    'jump_url': jump_url
                })

        if idx % 300 == 0 or idx == len(files):
            print(f"   Processed {idx}/{len(files)} files...")

    # Format output dictionary
    output_dict = {}
    for display_name, data in sorted(entity_results.items(), key=lambda x: x[1]['total_mentions'], reverse=True):
        # Top channels
        sorted_channels = dict(sorted(data['channel_counts'].items(), key=lambda x: x[1], reverse=True)[:5])
        output_dict[display_name] = {
            'category': data['category'],
            'total_mentions': data['total_mentions'],
            'top_channels': sorted_channels,
            'sample_cues': data['sample_cues'][:3]
        }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    print(f"✍️  Writing {OUTPUT_FILE} ({len(output_dict)} tracked entities)...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        yaml.dump(output_dict, out_f, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=120)

    print("✅ Entity & Tool Index generation complete!")

if __name__ == '__main__':
    main()
