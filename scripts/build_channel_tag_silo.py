#!/usr/bin/env python3
"""
build_channel_tag_silo.py

Compiles a 3-Tier Tagging Hierarchy from `formatted_transcripts/`:
1. First-Order Tags: Video-Bound (specific timestamps and video context)
2. Second-Order Tags: Channel-Bound (creator thematic pillars and vocabulary)
3. Third-Order Tags: Unbound / Global (universal conceptual nodes across all channels)

Exports:
- `tag_silo/<channel_slug>/videos/<video_id>.yaml` (Per-video tag records)
- `tag_silo/<channel_slug>/channel_taxonomy.yaml` (Second-order channel taxonomy)
- `tag_silo/<channel_slug>/inverted_tag_index.json` (Tag -> [video_ids, timestamps])
- `tag_silo/<channel_slug>/channel_tag_report.md` (Executive report)
- `tag_silo/third_order_unbound_tags.yaml` (Third-order global tags)
- `tag_silo/tag_hierarchy_manifest.json` (D3.js graph manifest for SvelteKit SPA)
"""

import os
import sys
import json
import yaml
import re
import argparse
from collections import defaultdict, Counter
from datetime import datetime

try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

class CleanDumper(SafeDumper):
    pass

def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

CleanDumper.add_representer(str, str_representer)

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
FORMATTED_DIR = os.path.join(SCRATCH_DIR, 'formatted_transcripts')
TAG_SILO_ROOT = os.path.join(SCRATCH_DIR, 'tag_silo')

THERAMINTREES_TITLES = {
    "jWLZfeKpIhg": "losing (part 1) | relationship autopsy & parental narcissism",
    "xFt_aeQw2GA": "concealing abuse | family denial & systemic protection",
    "6F58ZJt_qYU": "exposing abuse (part 2) | the fallout of truth-telling",
    "TsvJMlg_SaM": "exposing abuse (part 1) | breaking the silence",
    "c39F04inLJ0": "infantilisation | forced dependency & preventing adulthood",
    "oX3qM4VqbJo": "nobody's follower | reclaiming self-sovereignty & leaving groups",
    "sXcTIkuzQ3I": "save | deconstructing the messiah & rescue complex",
    "u91ctugBCsg": "compelled love / weaponised love | love as emotional debt",
    "zcRUj8H3rc4": "death of a narcissist | grief without reconciliation",
    "kMeehIpxH5k": "abuse in therapy | predatory dynamics & ethical boundaries",
    "vnSiJOOdo30": "what we look for | attraction, trauma bonding & compatibility",
    "qjZ3f-IXEXU": "bowing to narcissists | appeasement & institutional enabling",
    "PEexQAkhFpM": "resisting emotional blackmail | boundaries against fog",
    "K4YZoNxSZNU": "living with abusers | survival tactics in hostile environments",
    "mdDAHekq9yc": "giving up on fixing people | accepting unchangeable dynamics",
    "OsAaxOFOUl4": "moral values | developing autonomous ethical frameworks",
    "o1G4JFuLlO8": "rumination | cognitive loops, injustice & breaking mental replay",
    "YIQocoxv5tg": "copying enemies | adopting abusive tactics to survive",
    "sUazbGC_XI4": "double-binds | communicative traps & guaranteed failure",
    "Cx4GvzjRMx8": "tribalism | in-group dogmatism & cognitive isolation",
    "e-2WZsP6LA0": "false equivalence | neutralizing abuse through both-sides fallacy",
    "o6-Htscvf4k": "dogmatism & indoctrination | deconstructing authoritarian control",
    "XSShv4lhgKQ": "shame & guilt | weaponized conscience & reclaiming autonomy",
    "NkLM8HTYY1g": "destructive relationships | how people get trapped",
    "YqnCwp9Ia68": "imaginary flaws | projected defects & invalidation",
    "4D5tZoF8cC4": "impersonation & boundary defense | direct channel memo"
}

# Third-Order Global Unbound Tag Ontologies
THIRD_ORDER_UNBOUND_ONTOLOGY = {
    "T3_AUTONOMY_SOVEREIGNTY": {
        "name": "Autonomy & Cognitive Sovereignty",
        "category": "Foundational Epistemology",
        "description": "The fundamental capacity of an individual for self-governance, independent thought, and resistance to external psychological coercion.",
        "second_order_mapping": ["cognitive_autonomy_and_individuation", "relational_ethics_and_boundaries", "boundary_assertion_without_defense"]
    },
    "T3_EMOTIONAL_METABOLISM": {
        "name": "Emotional Digestion & Somatic Metabolism",
        "category": "Somatic & Contemplative Science",
        "description": "The physiological processing of undigested affective distress (Samskaras) without cognitive rationalization or behavioral avoidance.",
        "second_order_mapping": ["samskara_emotional_memory", "somatic_emotional_digestion", "dissociation_and_derealization", "alexithymia_emotional_disconnect"]
    },
    "T3_POWER_ASYMMETRY_MANIPULATION": {
        "name": "Power Asymmetry & Covert Exploitation",
        "category": "Interpersonal & Systemic Dynamics",
        "description": "Communicative and relational structures where authority or emotional leverage is abused to enforce dependency, compliance, or reality distortion.",
        "second_order_mapping": ["covert_psychological_manipulation", "double_bind_communicative_trap", "covert_narcissism_and_victimhood", "infantilisation_forced_dependency", "gaslighting_reality_denial", "fog_fear_obligation_guilt"]
    },
    "T3_NEURODIVERGENCE_EXECUTIVE_FUNCTION": {
        "name": "Neurodivergence & Dopaminergic Regulation",
        "category": "Neurobiology & Executive Function",
        "description": "Brain circuitry mechanics governing dopamine baselines, attention elasticity, task initiation friction, and burnout recovery.",
        "second_order_mapping": ["neurodivergence_and_adhd", "dopamine_baseline_and_receptors", "task_initiation_and_procrastination", "two_minute_frictionless_entry", "gifted_kid_burnout"]
    },
    "T3_ATTACHMENT_RELATIONAL_BONDING": {
        "name": "Attachment Systems & Relational Projection",
        "category": "Developmental & Relational Psychology",
        "description": "Early mammalian attachment security, relational attunement, romantic pedestal projection, and the trauma of emotional abandonment.",
        "second_order_mapping": ["attachment_styles_anxious_avoidant", "limerence_and_pedestals", "unrequited_love_and_friendzone", "weaponised_and_compelled_love", "family_estrangement_and_grief"]
    },
    "T3_SHAME_GUILT_EGO_PRESERVATION": {
        "name": "Ego Defense & Weaponized Conscience",
        "category": "Identity & Moral Psychology",
        "description": "The deconstruction of false guilt, social compliance reflexes, ego identity (Ahamkara), and the recovery of authentic self-worth.",
        "second_order_mapping": ["ahamkara_ego_identity", "toxic_guilt_and_false_responsibility", "compulsive_people_pleasing_appeasement", "decoupling_worth_from_achievement", "imposter_syndrome"]
    }
}

# Second-Order Channel Lexicons
SECOND_ORDER_LEXICONS = {
    "healthygamergg": {
        "domains": {
            "clinical_psychiatry": ["psychiatry", "psychiatrist", "diagnosis", "dsm", "antidepressant", "medication", "clinical", "disorder", "therapy", "therapist", "did", "derealization", "bipolar", "schizoid"],
            "eastern_contemplative_psychology": ["sanskrit", "ayurveda", "vedanta", "monk", "monastery", "samkhya", "karma", "dharma", "yoga", "meditation", "pranayama", "chakra", "ashram", "guru", "mindfulness", "hinduism", "buddhism"],
            "neurobiology_and_neurotransmitters": ["dopamine", "prefrontal cortex", "amygdala", "serotonin", "neurotransmitter", "receptor", "baseline", "circuit", "limbic", "neurological", "downregulation", "biology", "brain"],
            "relational_and_attachment_psychology": ["attachment", "attachment style", "dating", "relationship", "intimacy", "breakup", "limerence", "friendzone", "confession", "marriage", "partner", "love", "crush"],
            "addiction_and_behavioral_medicine": ["addiction", "gaming addiction", "relapse", "tolerance", "craving", "withdrawal", "compulsion", "detox", "sobriety", "porn", "video games", "screens"],
            "developmental_and_childhood_trauma": ["childhood", "traumatic childhood", "parents", "mother", "father", "neglect", "emotional abuse", "upbringing", "developmental", "inner child"]
        },
        "concepts": {
            "samskara_emotional_memory": ["samskara", "emotional scar", "undigested emotion", "emotional memory", "unprocessed emotion", "trauma memory", "past experience"],
            "sakshi_witness_consciousness": ["sakshi", "witness", "neutral observer", "observer stance", "observing self", "awareness itself", "unattached awareness", "watching your thoughts"],
            "ahamkara_ego_identity": ["ahamkara", "ego", "identity", "self-image", "pride", "ego defense", "reputation", "who you think you are"],
            "attachment_styles_anxious_avoidant": ["attachment style", "anxious attachment", "avoidant attachment", "secure attachment", "disorganized attachment", "fearful avoidant"],
            "dopamine_baseline_and_receptors": ["dopamine baseline", "dopamine detox", "tonic dopamine", "phasic dopamine", "dopaminergic", "pleasure pain balance", "reward pathway"],
            "neurodivergence_and_adhd": ["adhd", "attention deficit", "neurodivergent", "executive function", "hyperfocus", "dopamine deficiency", "stimulation seeking", "inattentive"],
            "alexithymia_emotional_disconnect": ["alexithymia", "identifying feelings", "naming emotions", "emotional blindness", "disconnect from feelings", "can't feel"],
            "limerence_and_pedestals": ["limerence", "obsessive crush", "pedestal", "idealization", "romantic obsession", "infatuation", "love addiction"],
            "dissociation_and_derealization": ["derealization", "depersonalization", "dissociation", "dissociative", "out of body", "foggy", "not real"],
            "defensive_intellectualization": ["intellectualizing", "intellectualization", "analyzing feelings", "thinking about feelings", "living in the head", "rationalizing"]
        },
        "pain_points": {
            "task_initiation_and_procrastination": ["can't start", "procrastination", "procrastinating", "putting it off", "paralyzed", "stuck in bed", "avoiding work", "avoidance", "lazy", "task paralysis"],
            "gifted_kid_burnout": ["gifted burnout", "fell behind", "used to be smart", "burned out", "failed potential", "lazy genius", "fear of effort", "effortless"],
            "unrequited_love_and_friendzone": ["unrequited", "confess your love", "can't stop thinking about her", "obsessed with him", "friendzone", "rejection", "rejected"],
            "existential_anhedonia_and_numbness": ["numb", "empty", "nothing brings joy", "anhedonia", "apathetic", "why bother", "lost meaning", "hollow", "flat"],
            "imposter_syndrome": ["imposter syndrome", "fraud", "exposed", "not qualified", "faking it", "luck", "worthless"],
            "compulsive_people_pleasing": ["people pleaser", "saying no", "guilty saying no", "approval seeker", "pleasing everyone", "conflict avoidant"],
            "chronic_loneliness_and_isolation": ["lonely", "no friends", "isolated", "can't connect", "alienated", "nobody understands", "isolation"],
            "parental_conflict_and_guilt": ["fix your traumatic", "parents", "mom and dad", "family conflict", "parental approval", "strict parents"]
        },
        "actionable_protocols": {
            "two_minute_frictionless_entry": ["two minute", "2 minute", "lower the friction", "start small", "micro step", "just open the book", "frictionless"],
            "somatic_emotional_digestion": ["digest the emotion", "sit with the feeling", "feel the sensation", "metabolize", "body sensation", "belly", "chest", "throat", "allow the feeling"],
            "dopamine_fast_sensory_reset": ["dopamine fast", "dopamine detox", "24 hour fast", "boredom is the cure", "remove screens", "sensory deprivation"],
            "pranayama_and_breathwork": ["pranayama", "nadi shodhana", "alternate nostril", "breath of fire", "box breathing", "inhalation", "exhalation", "breathing exercise"],
            "decoupling_worth_from_achievement": ["separate self worth", "worth from achievement", "not your grades", "outcome independent", "ego detachment", "unconditional worth"],
            "boundary_assertion_without_defense": ["set boundaries", "hold a boundary", "say no", "assertive", "stop overcorrecting"]
        },
        "modalities": {
            "live_client_interview": ["interview", "viewer", "talking with", "client", "let's welcome", "how are you doing", "thanks for coming on", "lucas", "coaching"],
            "case_study_trial_breakdown": ["trial", "case study", "breakdown by expert", "lindsay clancy", "forensic", "court", "psychiatric breakdown"],
            "clinical_lecture": ["in this video", "today we are going to understand", "psychiatry explains", "let's look at the brain", "neurologically", "dr. k", "healthy gamer"],
            "q_and_a_unpacking": ["chat says", "viewer writes", "reddit", "question from", "post on the subreddit", "community"]
        }
    },
    "theramintrees": {
        "domains": {
            "systemic_family_therapy": ["family", "parent", "mother", "father", "childhood", "household", "sibling", "upbringing", "dynasty", "семей", "родител", "майка", "баща"],
            "covert_psychological_manipulation": ["manipulation", "manipulative", "covert", "control", "abusive", "predatory", "leverage", "tactics", "exploit", "манипул", "злоупотреб", "насил"],
            "dogmatic_indoctrination_and_cults": ["dogma", "indoctrination", "religion", "religious", "cult", "authoritarian", "ideology", "scripture", "belief system", "orthodoxy", "догм", "религи"],
            "cognitive_autonomy_and_individuation": ["autonomy", "sovereignty", "boundaries", "self-determination", "independent thought", "liberty", "agency", "автономи", "границ", "свобод"],
            "relational_ethics_and_boundaries": ["ethics", "moral", "reciprocity", "consent", "honesty", "exploitation", "fairness", "етик", "морал"]
        },
        "concepts": {
            "double_bind_communicative_trap": ["double-bind", "double bind", "no-win", "damned if you do", "contradictory demand", "catch-22", "impossible standard", "двойн"],
            "covert_narcissism_and_victimhood": ["covert narcissism", "narcissistic", "fragile narcissism", "victim playing", "self-absorbed", "martyr complex", "нарцис"],
            "fog_fear_obligation_guilt": ["emotional blackmail", "fog", "fear obligation guilt", "obligation", "guilt tripping", "emotional extortion", "изнудван", "дълг"],
            "infantilisation_forced_dependency": ["infantilisation", "infantilize", "infantile", "treating as a child", "forced dependency", "crippling independence", "инфантилиза"],
            "gaslighting_reality_denial": ["gaslighting", "gaslight", "reality denial", "question your sanity", "invented flaws", "rewriting history", "въображаем"],
            "weaponised_and_compelled_love": ["weaponised love", "compelled love", "love as debt", "conditional affection", "love bombing", "насилствена обич"],
            "false_equivalence_fallacy": ["false equivalence", "both sides", "neutralizing abuse", "equating victim with abuser", "фалшива еквивалентност"],
            "tribalism_and_in_group_isolation": ["tribalism", "in-group", "out-group", "echo chamber", "dogmatic isolation", "shunning", "трайб"]
        },
        "pain_points": {
            "toxic_guilt_and_false_responsibility": ["toxic guilt", "false guilt", "weaponized conscience", "guilty for existing", "guilty for boundaries", "irrational responsibility", "вина", "виновен"],
            "compulsive_people_pleasing_appeasement": ["people pleasing", "appeasement", "fawning", "placating", "walking on eggshells", "keeping the peace", "покланяне"],
            "family_estrangement_and_grief": ["estrangement", "cutting contact", "no contact", "leaving family", "bereavement", "death of a parent", "скръб", "смърт"],
            "cognitive_rumination_mental_loops": ["rumination", "ruminating", "mental loop", "replay", "obsessive replay", "unanswered grievance", "руминация", "мисловно предъвкване"],
            "loss_of_sovereignty_and_agency": ["trapped", "powerless", "helpless", "controlled", "micromanaged", "безпомощ"],
            "parental_invalidation_and_erasure": ["invalidation", "unheard", "dismissed", "denial", "scapegoat", "прикриване"]
        },
        "actionable_protocols": {
            "grey_rock_method_unreactivity": ["grey rock", "unreactive", "flatlining", "boring", "starve for fuel", "minimal response", "neutrality", "неутрал"],
            "anti_jade_boundaries": ["anti-jade", "do not justify", "don't defend", "no explanation", "declarative boundary", "firm refusal", "не се оправдавай"],
            "informational_starvation": ["informational diet", "withhold personal details", "share nothing vulnerable", "privacy protection", "информацион"],
            "giving_up_on_fixing_people": ["giving up on fixing", "accepting reality", "stop rehabilitating", "cannot change them", "abandon rescue fantasy", "откажи се"],
            "buffer_response_delay": ["let me check", "time buffer", "pause before answering", "refuse on-the-spot compliance", "време"]
        },
        "modalities": {
            "scripted_video_essay": ["video essay", "narrative", "in this essay", "let us examine", "scripted analysis", "есе"],
            "relationship_autopsy": ["relationship autopsy", "retrospective", "case study", "in part one", "in part two", "losing", "аутопсия"],
            "philosophical_deconstruction": ["deconstruction", "critique", "examining the dogma", "structural breakdown", "logical fallacy", "деконструкция"],
            "channel_editorial_memo": ["channel note", "memo", "update", "direct message to viewers", "alert"]
        }
    }
}

def format_timestamp(seconds):
    try:
        s = int(round(float(seconds)))
        m, sec = divmod(s, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"
    except:
        return "00:00"

def parse_seconds_from_duration(dur_str):
    if not dur_str or dur_str == 'N/A':
        return 600.0
    dur_str = str(dur_str).strip()
    if 'min' in dur_str:
        try:
            return float(dur_str.replace('min', '').strip()) * 60.0
        except:
            pass
    parts = [int(p) for p in dur_str.split(':') if p.isdigit()]
    if len(parts) == 3:
        return float(parts[0] * 3600 + parts[1] * 60 + parts[2])
    elif len(parts) == 2:
        return float(parts[0] * 60 + parts[1])
    return 600.0

def extract_timestamps_and_segments(transcript_text, duration_sec):
    segments = []
    sec_matches = list(re.finditer(r'\[(\d+(?:\.\d+)?)s?\]', transcript_text))
    if len(sec_matches) > 5:
        for i, match in enumerate(sec_matches):
            t_sec = float(match.group(1))
            start_idx = match.end()
            end_idx = sec_matches[i+1].start() if i + 1 < len(sec_matches) else len(transcript_text)
            chunk = transcript_text[start_idx:end_idx].strip()
            if chunk:
                segments.append({
                    "seconds": t_sec,
                    "timestamp": format_timestamp(t_sec),
                    "text": chunk
                })
        return segments

    time_matches = list(re.finditer(r'\[(?:(\d+):)?(\d+):(\d+)\]', transcript_text))
    if len(time_matches) > 5:
        for i, match in enumerate(time_matches):
            h = int(match.group(1)) if match.group(1) else 0
            m = int(match.group(2))
            s = int(match.group(3))
            t_sec = float(h * 3600 + m * 60 + s)
            start_idx = match.end()
            end_idx = time_matches[i+1].start() if i + 1 < len(time_matches) else len(transcript_text)
            chunk = transcript_text[start_idx:end_idx].strip()
            if chunk:
                segments.append({
                    "seconds": t_sec,
                    "timestamp": format_timestamp(t_sec),
                    "text": chunk
                })
        return segments

    clean_text = re.sub(r'\[.*?\]', '', transcript_text).strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(s.strip()) > 15]
    if not sentences:
        sentences = [clean_text]
    sec_step = duration_sec / max(1, len(sentences))
    for i, sent in enumerate(sentences):
        t_sec = i * sec_step
        segments.append({
            "seconds": t_sec,
            "timestamp": format_timestamp(t_sec),
            "text": sent
        })
    return segments

def extract_key_phrases(transcript_text, top_n=6):
    clean = re.sub(r'\[.*?\]', ' ', transcript_text.lower())
    clean = re.sub(r'[^a-z0-9\s-]', ' ', clean)
    words = [w for w in clean.split() if len(w) > 3 and w not in {
        'that', 'this', 'with', 'from', 'have', 'were', 'which', 'about', 'there',
        'what', 'when', 'where', 'your', 'they', 'them', 'their', 'because', 'would',
        'could', 'should', 'people', 'going', 'really', 'think', 'know', 'like', 'just',
        'well', 'then', 'into', 'some', 'other', 'than', 'want', 'look', 'make', 'even',
        'music', 'snorts'
    }]
    
    bigrams = []
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        if w1 != w2:
            bigrams.append(f"{w1} {w2}")
            
    counts = Counter(bigrams)
    return [phrase for phrase, _ in counts.most_common(top_n)]

def analyze_video_3tier(video_data, channel_slug, lexicon):
    transcript = video_data.get('transcript_text', '')
    title = video_data.get('title', '')
    dur_sec = parse_seconds_from_duration(video_data.get('duration'))
    combined_text = (title + " " + transcript).lower()

    segments = extract_timestamps_and_segments(transcript, dur_sec)

    matched_second_order = []
    first_order_tags = []
    matched_third_order = set()

    # Match Second-Order Tags
    for dim_name in ["domains", "concepts", "pain_points", "actionable_protocols", "modalities"]:
        dim_dict = lexicon.get(dim_name, {})
        for tag_name, keywords in dim_dict.items():
            hit = False
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', title.lower()):
                    matched_second_order.append(tag_name)
                    hit = True
                    break
            if hit:
                continue
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', combined_text):
                    matched_second_order.append(tag_name)
                    break

    # Contextual defaults if empty
    if not matched_second_order:
        matched_second_order.append("clinical_lecture" if channel_slug == "healthygamergg" else "scripted_video_essay")

    # Match First-Order Tags (Video-bound with timestamps)
    for seg in segments:
        seg_lower = seg["text"].lower()
        for t2 in matched_second_order:
            # find keywords
            kw_list = []
            for d in ["concepts", "pain_points", "actionable_protocols"]:
                if t2 in lexicon.get(d, {}):
                    kw_list = lexicon[d][t2]
                    break
            if any(re.search(r'\b' + re.escape(kw) + r'\b', seg_lower) for kw in kw_list):
                snippet = seg["text"][:140] + ("..." if len(seg["text"]) > 140 else "")
                first_order_tags.append({
                    "tag": f"vtag_{t2}",
                    "bound_second_order": t2,
                    "timestamp": seg["timestamp"],
                    "seconds": round(seg["seconds"], 1),
                    "context": snippet
                })

    # Deduplicate first order tags per minute
    deduped_first_order = []
    seen = set()
    for fo in first_order_tags:
        k = (int(fo["seconds"] // 60), fo["bound_second_order"])
        if k not in seen:
            seen.add(k)
            deduped_first_order.append(fo)
        if len(deduped_first_order) >= 15:
            break

    # Resolve Third-Order Unbound Tags
    second_set = set(matched_second_order)
    for t3_id, t3_meta in THIRD_ORDER_UNBOUND_ONTOLOGY.items():
        if any(s2 in second_set for s2 in t3_meta["second_order_mapping"]):
            matched_third_order.add(t3_id)

    key_phrases = extract_key_phrases(transcript, top_n=6)
    summary_hook = f"Explores {', '.join(matched_second_order[:3])}."

    return {
        "video_id": video_data.get("video_id"),
        "title": title,
        "channel": video_data.get("channel"),
        "url": video_data.get("url"),
        "duration": video_data.get("duration"),
        "word_count": video_data.get("word_count"),
        "first_order_tags": deduped_first_order,
        "second_order_tags": sorted(list(set(matched_second_order))),
        "third_order_tags": sorted(list(matched_third_order)),
        "key_phrases": key_phrases,
        "summary_hook": summary_hook
    }

def process_channels():
    os.makedirs(TAG_SILO_ROOT, exist_ok=True)
    target_channels = [("healthygamergg", "healthygamergg"), ("theramintrees", "theramintrees")]

    all_channel_records = {}
    manifest_nodes = []
    manifest_links = []

    # 1. Add Third-Order Unbound Nodes to Graph
    for t3_id, t3_meta in THIRD_ORDER_UNBOUND_ONTOLOGY.items():
        manifest_nodes.append({
            "id": t3_id,
            "label": t3_meta["name"],
            "order": 3,
            "category": t3_meta["category"],
            "description": t3_meta["description"],
            "radius": 24,
            "color": "#a855f7" # Purple core
        })

    for channel_slug, channel_query in target_channels:
        print(f"\n=======================================================")
        print(f"🚀 Processing 3-Tier Tag Silo for: '{channel_slug.upper()}'")
        print(f"=======================================================")

        channel_dir = os.path.join(TAG_SILO_ROOT, channel_slug)
        videos_dir = os.path.join(channel_dir, 'videos')
        os.makedirs(videos_dir, exist_ok=True)

        lexicon = SECOND_ORDER_LEXICONS.get(channel_slug, {})

        matched_videos = []
        all_files = sorted([f for f in os.listdir(FORMATTED_DIR) if f.endswith('.yaml')])
        for fn in all_files:
            fp = os.path.join(FORMATTED_DIR, fn)
            with open(fp, 'r', encoding='utf-8') as yf:
                header_lines = [yf.readline() for _ in range(12)]
                header_str = ''.join(header_lines).lower()
                if channel_query not in header_str:
                    continue
                yf.seek(0)
                data = yaml.load(yf, Loader=SafeLoader)
                ch = (data.get('channel') or '').strip().lower()
                if channel_query not in ch:
                    continue

                vid_id = data.get('video_id', '')
                title = data.get('title', '')
                if channel_slug == 'theramintrees' and vid_id in THERAMINTREES_TITLES:
                    title = THERAMINTREES_TITLES[vid_id]
                elif 'TheraminTrees Video Essay' in title and vid_id in THERAMINTREES_TITLES:
                    title = THERAMINTREES_TITLES[vid_id]

                tr = data.get('transcript') or ''
                if isinstance(tr, str) and tr.startswith('{"content":'):
                    try:
                        inner = json.loads(tr)
                        tr_text = inner.get('content', '')
                    except:
                        tr_text = tr
                else:
                    tr_text = str(tr)

                matched_videos.append({
                    "video_id": vid_id,
                    "title": title,
                    "channel": data.get('channel'),
                    "url": data.get('url') or f"https://www.youtube.com/watch?v={vid_id}",
                    "duration": data.get('duration', 'N/A'),
                    "word_count": len(tr_text.split()),
                    "transcript_text": tr_text
                })

        print(f"Loaded {len(matched_videos)} videos for {channel_slug}.")

        tag_counts = defaultdict(int)
        tag_dimension_map = {}
        inverted_index = defaultdict(list)
        total_words = 0
        channel_records = []

        for vdata in matched_videos:
            rec = analyze_video_3tier(vdata, channel_slug, lexicon)
            channel_records.append(rec)
            total_words += rec["word_count"]

            # Save per-video YAML record
            v_yaml_path = os.path.join(videos_dir, f"{rec['video_id']}.yaml")
            with open(v_yaml_path, 'w', encoding='utf-8') as vf:
                yaml.dump(rec, vf, Dumper=CleanDumper, sort_keys=False, allow_unicode=True)

            # Inverted Index & Counts
            for t2 in rec["second_order_tags"]:
                tag_counts[t2] += 1
                ts_list = [fo["timestamp"] for fo in rec["first_order_tags"] if fo["bound_second_order"] == t2]
                inverted_index[t2].append({
                    "video_id": rec["video_id"],
                    "title": rec["title"],
                    "timestamps": ts_list
                })

        all_channel_records[channel_slug] = channel_records

        # Second-Order Channel Taxonomy
        channel_color = "#10b981" if channel_slug == "healthygamergg" else "#f59e0b"
        taxonomy = {
            "channel": channel_slug,
            "order": 2,
            "scope": "channel_bound",
            "total_videos_analyzed": len(matched_videos),
            "total_spoken_words": total_words,
            "compiled_at": datetime.now().isoformat(),
            "second_order_tags": {}
        }

        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            prevalence = round((count / max(1, len(matched_videos))) * 100, 1)
            taxonomy["second_order_tags"][tag] = {
                "tag": tag,
                "channel": channel_slug,
                "video_occurrences": count,
                "prevalence_pct": prevalence
            }

            # Add Second-Order Node to Manifest
            t2_node_id = f"{channel_slug}:{tag}"
            manifest_nodes.append({
                "id": t2_node_id,
                "label": tag.replace("_", " ").title(),
                "order": 2,
                "channel": channel_slug,
                "occurrences": count,
                "prevalence": prevalence,
                "radius": max(10, min(20, count // 2)),
                "color": channel_color
            })

            # Link Second-Order to Third-Order
            for t3_id, t3_meta in THIRD_ORDER_UNBOUND_ONTOLOGY.items():
                if tag in t3_meta["second_order_mapping"]:
                    manifest_links.append({
                        "source": t3_id,
                        "target": t2_node_id,
                        "type": "unbound_to_channel",
                        "value": 2
                    })

        tax_path = os.path.join(channel_dir, 'channel_taxonomy.yaml')
        with open(tax_path, 'w', encoding='utf-8') as tf:
            yaml.dump(taxonomy, tf, Dumper=CleanDumper, sort_keys=False, allow_unicode=True)

        inv_path = os.path.join(channel_dir, 'inverted_tag_index.json')
        with open(inv_path, 'w', encoding='utf-8') as jf:
            json.dump({
                "channel": channel_slug,
                "total_tags": len(inverted_index),
                "index": inverted_index
            }, jf, indent=2)

        # Sample First-Order Video Nodes into Graph (Top 15 per channel to avoid clutter)
        sample_vids = sorted(channel_records, key=lambda x: -x["word_count"])[:15]
        for v in sample_vids:
            v_node_id = f"vid:{v['video_id']}"
            manifest_nodes.append({
                "id": v_node_id,
                "label": v["title"][:28] + "...",
                "full_title": v["title"],
                "order": 1,
                "channel": channel_slug,
                "duration": v["duration"],
                "url": v["url"],
                "radius": 6,
                "color": "#38bdf8"
            })
            for t2 in v["second_order_tags"][:3]:
                manifest_links.append({
                    "source": f"{channel_slug}:{t2}",
                    "target": v_node_id,
                    "type": "channel_to_video",
                    "value": 1
                })

    # 3. Export Third-Order Unbound Tags YAML
    t3_export_path = os.path.join(TAG_SILO_ROOT, 'third_order_unbound_tags.yaml')
    with open(t3_export_path, 'w', encoding='utf-8') as yf:
        yaml.dump({
            "order": 3,
            "scope": "global_unbound",
            "compiled_at": datetime.now().isoformat(),
            "total_unbound_tags": len(THIRD_ORDER_UNBOUND_ONTOLOGY),
            "unbound_tags": THIRD_ORDER_UNBOUND_ONTOLOGY
        }, yf, Dumper=CleanDumper, sort_keys=False, allow_unicode=True)

    # 4. Export Combined Tag Hierarchy Graph Manifest for SvelteKit D3 SPA
    manifest_path = os.path.join(TAG_SILO_ROOT, 'tag_hierarchy_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as jf:
        json.dump({
            "compiled_at": datetime.now().isoformat(),
            "summary": {
                "third_order_count": len(THIRD_ORDER_UNBOUND_ONTOLOGY),
                "channels_indexed": len(target_channels),
                "total_nodes": len(manifest_nodes),
                "total_links": len(manifest_links)
            },
            "third_order_ontology": THIRD_ORDER_UNBOUND_ONTOLOGY,
            "nodes": manifest_nodes,
            "links": manifest_links
        }, jf, indent=2)

    print(f"\n✅ 3-Tier Tagging Hierarchy compiled successfully!")
    print(f" - Third-Order Global Tags: {t3_export_path}")
    print(f" - D3 Graph Manifest for SPA: {manifest_path} ({len(manifest_nodes)} nodes, {len(manifest_links)} links)")

if __name__ == '__main__':
    process_channels()
