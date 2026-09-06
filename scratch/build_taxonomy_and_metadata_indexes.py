#!/usr/bin/env python3
"""
build_taxonomy_and_metadata_indexes.py

Generates two decoupled taxonomy & metadata index files:
1. `video_metadata_registry.yaml` (Ground-Up):
   Maps each video_id to its domain, topics, tags, synopsis, and key takeaways.
2. `topic_taxonomy_index.yaml` (Top-Down):
   Inverted index mapping domains and topics to list of referencing video IDs, titles, and channels.
"""

import os
import re
import json
import yaml
from collections import defaultdict

try:
    from yaml import CSafeDumper as Dumper, CSafeLoader as Loader
except ImportError:
    from yaml import SafeDumper as Dumper, SafeLoader as Loader

FORMATTED_DIR = "formatted_transcripts"
DOWNLOADED_DIR = "downloaded_transcripts"
TAXONOMY_DIR = "taxonomy"

DOMAIN_KEYWORDS = {
    'software_engineering': {
        'title': 'Software Engineering, Systems & Game Dev',
        'keywords': [
            'primeagen', 'freecodecamp', 'web dev simplified', 'cherno', 'coding train',
            'codeparade', 'game maker', 'mayuko', 'sokpop', 'typecraft', 'derek banas',
            'engineer', 'python', 'javascript', 'rust', 'react', 'code', 'developer',
            'algorithm', 'software', 'programming', 'noclip', 'frontend', 'backend',
            'api', 'neovim', 'vim', 'git', 'css', 'html', 'compiler', 'c++', 'typescript'
        ]
    },
    'cybersecurity_homelabs': {
        'title': 'Cybersecurity, Networking & Homelabs',
        'keywords': [
            'networkchuck', 'seytonic', 'david bombal', 'techquickie', 'cyber',
            'security', 'hack', 'linux', 'homelab', 'docker', 'networking', 'router',
            'vpn', 'firewall', 'terminal', 'bash', 'packet', 'wireshark', 'dns'
        ]
    },
    'business_systems': {
        'title': 'Business Systems, Career & Offer Scaling',
        'keywords': [
            'hormozi', 'ferriss', 'revenue', 'saas', 'sales', 'business', 'offer',
            'marketing', 'startup', 'monetization', 'salary', 'career', 'negotiat',
            'interview', 'hiring', 'pricing', 'wealth', 'invest'
        ]
    },
    'cognitive_psychology': {
        'title': 'Cognitive Psychology & Mental Processing',
        'keywords': [
            'healthygamer', 'dr. k', 'julienhimself', 'theramintrees', 'art of accomplishment',
            'psychology', 'burnout', 'adhd', 'trauma', 'emotional', 'mind', 'depression',
            'therapy', 'anxiety', 'ego', 'shame', 'guilt', 'narcissis'
        ]
    },
    'pali_philosophy': {
        'title': 'Pāli Canon & Contemplative Philosophy',
        'keywords': [
            'doug', 'dharma', 'buddhis', 'sutta', 'pali', 'mindfulness', 'karma',
            'meditation', 'dukkha', 'four noble truths', 'eightfold', 'sangha'
        ]
    },
    'science_philosophy': {
        'title': 'Science, Physics & Foundational Philosophy',
        'keywords': [
            'sabine', 'hossenfelder', 'academy of ideas', 'veritasium', 'action lab',
            'exurb1a', 'accepting the universe', 'physics', 'quantum', 'philosophy',
            'nietzsche', 'stoic', 'jung', 'relativity', 'cosmology', 'epistemology'
        ]
    },
    'longevity_creative_tech': {
        'title': 'Longevity, Robotics & Creative Technology',
        'keywords': [
            'bryan johnson', 'michael reeves', 'pierre', 'generative music',
            'longevity', 'blueprint', 'robot', 'hardware', 'biotech', 'health'
        ]
    },
    'news_media_culture': {
        'title': 'Digital News, Media Analysis & Current Affairs',
        'keywords': [
            'philip defranco', 'defranco', 'phillydefranco', 'news', 'politics',
            'scandal', 'trial', 'supreme court', 'investigation', 'whistleblower'
        ]
    }
}

STOPWORDS = {
    'video', 'watch', 'learn', 'course', 'full', 'tutorial', 'how', 'to', 'the', 'and', 'for',
    'with', 'this', 'that', 'your', 'from', 'patreon', 'support', 'join', 'wishlist', 'here',
    'twitter', 'discord', 'instagram', 'youtube', 'step', 'part', 'review', 'best'
}

def clean_tag(tag):
    tag = tag.strip().lower().replace('#', '').replace(' ', '_').replace('-', '_')
    tag = re.sub(r'[^a-z0-9_]', '', tag)
    return tag

def classify_domain(channel, title):
    text = f"{channel.lower()} {title.lower()}"
    for domain_id, meta in DOMAIN_KEYWORDS.items():
        if any(kw in text for kw in meta['keywords']):
            return domain_id
    return 'general_knowledge'

def extract_topics(title, key_concepts, synopsis):
    topics = set()
    # 1. Title hashtags & key terms
    for tag in re.findall(r'#(\w+)', title):
        ct = clean_tag(tag)
        if ct and ct not in STOPWORDS and len(ct) > 2:
            topics.add(ct)

    # 2. Existing key_concepts
    for kc in (key_concepts or []):
        ct = clean_tag(kc)
        if ct and ct not in STOPWORDS and len(ct) > 2:
            topics.add(ct)

    # 3. Domain topic extraction from title
    title_words = re.findall(r'\b[A-Za-z0-9+#]{2,}\b', title)
    for w in title_words:
        cw = clean_tag(w)
        if cw in {'rust', 'python', 'javascript', 'docker', 'linux', 'ai', 'ui', 'react',
                  'neovim', 'vim', 'git', 'adhd', 'burnout', 'marketing', 'sales', 'css',
                  'sql', 'database', 'llm', 'security', 'hardware', 'math', 'quantum'}:
            topics.add(cw)

    return sorted(list(topics))

def main():
    print("🏗️  Building Decoupled Ground-Up & Top-Down Taxonomy Manifests...")

    formatted_files = sorted([f for f in os.listdir(FORMATTED_DIR) if f.endswith('.yaml')])
    video_registry = {}
    topic_index = defaultdict(lambda: {'title': '', 'topics': defaultdict(list)})

    # Initialize topic_index domains
    for dom_id, meta in DOMAIN_KEYWORDS.items():
        topic_index[dom_id]['title'] = meta['title']
    topic_index['general_knowledge']['title'] = 'General Knowledge & Broad Media'

    for fname in formatted_files:
        fpath = os.path.join(FORMATTED_DIR, fname)
        base = os.path.splitext(fname)[0]
        json_path = os.path.join(DOWNLOADED_DIR, f"{base}.json")

        with open(fpath, 'r', encoding='utf-8') as fp:
            doc = yaml.load(fp, Loader=Loader)

        v_id = doc.get('video_id') or base
        title = doc.get('title') or ''
        channel = doc.get('channel') or ''
        v_type = doc.get('type') or 'video'

        # Load rich summary from downloaded json if present
        synopsis = ""
        takeaways = []
        raw_concepts = []

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as jfp:
                    jdata = json.load(jfp)
                vsum = jdata.get('video_summary', {})
                if isinstance(vsum, dict):
                    synopsis = vsum.get('synopsis') or vsum.get('executive_synopsis') or ""
                    takeaways = vsum.get('key_takeaways') or vsum.get('core_takeaways') or []
                    raw_concepts = vsum.get('key_concepts') or []
            except Exception:
                pass

        domain = classify_domain(channel, title)
        topics = extract_topics(title, raw_concepts, synopsis)

        # 1. Ground-Up Entry
        ground_up_entry = {
            'title': title,
            'channel': channel,
            'type': v_type,
            'domain': domain,
            'topics': topics,
        }
        if synopsis:
            ground_up_entry['synopsis'] = synopsis[:300].strip() + ("..." if len(synopsis) > 300 else "")
        if takeaways:
            ground_up_entry['takeaways'] = [t[:180].strip() for t in takeaways[:3]]

        video_registry[v_id] = ground_up_entry

        # 2. Top-Down Entries
        video_ref = {
            'video_id': v_id,
            'title': title,
            'channel': channel,
            'type': v_type
        }

        # Index under domain general
        topic_index[domain]['topics']['all_videos'].append(v_id)

        # Index under specific topics
        for t in topics:
            topic_index[domain]['topics'][t].append(v_id)

    os.makedirs(TAXONOMY_DIR, exist_ok=True)
    video_reg_path = os.path.join(TAXONOMY_DIR, 'video_metadata_registry.yaml')
    topic_index_path = os.path.join(TAXONOMY_DIR, 'topic_taxonomy_index.yaml')

    # Write video_metadata_registry.yaml (Ground-Up)
    print(f"✍️  Writing {video_reg_path} ({len(video_registry)} videos)...")
    with open(video_reg_path, 'w', encoding='utf-8') as out_f:
        yaml.dump(video_registry, out_f, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=120)

    # Format Top-Down index cleanly
    top_down_output = {}
    for dom_id, dom_data in topic_index.items():
        topic_dict = {}
        for top_name, v_list in sorted(dom_data['topics'].items()):
            topic_dict[top_name] = {
                'count': len(v_list),
                'video_ids': v_list
            }
        top_down_output[dom_id] = {
            'title': dom_data['title'],
            'topic_count': len(topic_dict),
            'topics': topic_dict
        }

    # Write topic_taxonomy_index.yaml (Top-Down)
    print(f"✍️  Writing {topic_index_path} ({len(top_down_output)} domains)...")
    with open(topic_index_path, 'w', encoding='utf-8') as out_f:
        yaml.dump(top_down_output, out_f, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=120)

    print("✅ Completed both decoupled manifests successfully!")

if __name__ == '__main__':
    main()
