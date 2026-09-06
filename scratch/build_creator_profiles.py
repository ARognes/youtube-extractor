#!/usr/bin/env python3
"""
build_creator_profiles.py

Synthesizes comprehensive intellectual dossiers and metrics for all 183 creators
across the 1,740 formatted YAML transcripts, outputting `taxonomy/creator_profiles.yaml`.
"""

import os
import re
import json
import yaml
from collections import defaultdict, Counter

try:
    from yaml import CSafeDumper as Dumper, CSafeLoader as Loader
except ImportError:
    from yaml import SafeDumper as Dumper, SafeLoader as Loader

FORMATTED_DIR = "formatted_transcripts"
TAXONOMY_REGISTRY = "taxonomy/video_metadata_registry.yaml"
SPEECH_DYNAMICS = "taxonomy/speech_dynamics.yaml"
PERSONAS_FILE = "creator_personas.json"
OUTPUT_FILE = "taxonomy/creator_profiles.yaml"

COMMON_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with',
    'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if',
    'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him',
    'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
    'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two',
    'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give',
    'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been', 'has', 'had', 'doing', 'does', 'yeah', 'um',
    'uh', 'right', 'really', 'going', 'kind', 'lot', 'thing', 'things', 'actually', 'mean', 'something'
}

def parse_duration_str(dur_str):
    if not dur_str:
        return 0
    parts = [int(p) for p in str(dur_str).split(':') if p.isdigit()]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 1:
        return parts[0]
    return 0

def main():
    print("🧠 Synthesizing Creator Dossiers & Mental Model Profiles...")

    # 1. Load existing registries
    video_registry = {}
    if os.path.exists(TAXONOMY_REGISTRY):
        with open(TAXONOMY_REGISTRY, 'r', encoding='utf-8') as f:
            video_registry = yaml.load(f, Loader=Loader)

    personas = {}
    if os.path.exists(PERSONAS_FILE):
        try:
            with open(PERSONAS_FILE, 'r', encoding='utf-8') as pf:
                raw_p = json.load(pf)
                for item in raw_p:
                    if isinstance(item, dict) and 'creator_name' in item:
                        personas[item['creator_name'].lower()] = item.get('system_prompt', '')
        except Exception:
            pass

    # 2. Accumulate stats per channel
    channel_data = defaultdict(lambda: {
        'handle': '',
        'domain_counts': Counter(),
        'videos': [],
        'shorts_count': 0,
        'standard_videos_count': 0,
        'total_words': 0,
        'total_duration_sec': 0,
        'word_counter': Counter(),
        'topic_counter': Counter(),
        'takeaways_pool': []
    })

    files = sorted([f for f in os.listdir(FORMATTED_DIR) if f.endswith('.yaml')])

    for fname in files:
        fpath = os.path.join(FORMATTED_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as fp:
            doc = yaml.load(fp, Loader=Loader)

        ch = doc.get('channel') or 'Unknown'
        handle = doc.get('handle')
        v_id = doc.get('video_id', '')
        title = doc.get('title', '')
        v_type = doc.get('type', 'video')
        dur_str = doc.get('duration', '00:00')
        transcript = doc.get('transcript', '')

        cd = channel_data[ch]
        if handle and not cd['handle']:
            cd['handle'] = handle

        dur_sec = parse_duration_str(dur_str)
        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', transcript)]
        w_count = len(words)

        cd['total_words'] += w_count
        cd['total_duration_sec'] += dur_sec

        if v_type == 'short':
            cd['shorts_count'] += 1
        else:
            cd['standard_videos_count'] += 1

        # Track vocabulary (excluding common English stop words)
        for w in words:
            if w not in COMMON_WORDS:
                cd['word_counter'][w] += 1

        # Track topics from video_registry
        meta = video_registry.get(v_id, {})
        dom = meta.get('domain', 'general_knowledge')
        cd['domain_counts'][dom] += 1
        for top in meta.get('topics', []):
            cd['topic_counter'][top] += 1
        for tkw in meta.get('takeaways', []):
            if len(cd['takeaways_pool']) < 10:
                cd['takeaways_pool'].append(tkw)

        cd['videos'].append({
            'video_id': v_id,
            'title': title,
            'type': v_type,
            'word_count': w_count,
            'duration': dur_str,
            'duration_sec': dur_sec
        })

    # 3. Build comprehensive profile per creator
    creator_profiles = {}

    for ch, cd in channel_data.items():
        total_sec = cd['total_duration_sec']
        total_words = cd['total_words']
        total_hours = round(total_sec / 3600.0, 2)
        total_vids = len(cd['videos'])

        primary_domain = cd['domain_counts'].most_common(1)[0][0] if cd['domain_counts'] else 'general_knowledge'
        avg_wpm = round(total_words / (total_sec / 60.0), 1) if total_sec > 60 else 0

        # Unique vocab size
        vocab_size = len(cd['word_counter'])
        lexical_diversity = round((vocab_size / total_words) * 100, 2) if total_words > 100 else 0

        # Signature keywords (top non-stopwords)
        signature_keywords = [w for w, _ in cd['word_counter'].most_common(8)]
        signature_topics = [t for t, _ in cd['topic_counter'].most_common(6)]

        # Top flagship lectures by word count
        flagship_videos = sorted(cd['videos'], key=lambda x: x['word_count'], reverse=True)[:3]
        clean_flagship = [
            {
                'video_id': v['video_id'],
                'title': v['title'],
                'type': v['type'],
                'word_count': v['word_count'],
                'duration': v['duration']
            }
            for v in flagship_videos
        ]

        profile = {
            'channel_name': ch,
            'handle': cd['handle'] if cd['handle'] else None,
            'primary_domain': primary_domain,
            'library_metrics': {
                'total_videos': total_vids,
                'standard_videos': cd['standard_videos_count'],
                'shorts': cd['shorts_count'],
                'total_spoken_hours': total_hours,
                'total_words_spoken': total_words,
                'vocabulary_size': vocab_size,
                'lexical_diversity_pct': lexical_diversity,
                'avg_wpm': avg_wpm
            },
            'signature_topics': signature_topics,
            'signature_vocabulary': signature_keywords,
            'flagship_lectures': clean_flagship
        }

        # Include sample principles from takeaways if available
        if cd['takeaways_pool']:
            profile['core_principles'] = cd['takeaways_pool'][:3]

        creator_profiles[ch] = profile

    # Sort profiles by total spoken hours
    sorted_profiles = dict(sorted(creator_profiles.items(), key=lambda x: x[1]['library_metrics']['total_spoken_hours'], reverse=True))

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    print(f"✍️  Writing {OUTPUT_FILE} ({len(sorted_profiles)} creator profiles)...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        yaml.dump(sorted_profiles, out_f, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=120)

    print(f"✅ Generated dossiers for {len(sorted_profiles)} creators successfully!")

if __name__ == '__main__':
    main()
