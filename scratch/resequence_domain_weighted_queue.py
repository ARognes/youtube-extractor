#!/usr/bin/env python3
import json
import os

QUEUE_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json"
PENDING_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/pending_real_video_downloads.json"

SOFTWARE_ENG_KEYWORDS = [
    'code', 'coding', 'coder', 'software', 'developer', 'dev', 'c++', 'rust', 'python',
    'laurie', 'prime', 'blow', 'cherno', 'barker', 'liveoverflow', 'reso', 'pilfold',
    'computer', 'algorithm', 'linux', 'ai', 'humanoid', 'meta muse', 'game engine',
    'utf-8', 'github', 'programming', 'script', 'system', 'terminal', 'bytecode',
    'engineer', 'engineering', 'syntax', 'framework', 'database', 'sql', 'boot.dev'
]

LANGUAGE_KEYWORDS = [
    'french', 'spanish', 'francais', 'espanol', 'fluentu', 'innerfrench',
    'talk in french', 'lemonde', 'le monde', 'argentina', 'simpsons'
]

def classify_channel_priority(ch_name, handle, title=""):
    text = f"{ch_name} {handle} {title}".lower()
    
    # 1. Language channels -> Very low weight (0.25x)
    if any(kw in text for kw in LANGUAGE_KEYWORDS):
        return 'LANGUAGE', 0.25

    # 2. Software Engineering channels -> Heavy weight (8.0x)
    if any(kw in text for kw in SOFTWARE_ENG_KEYWORDS):
        return 'SOFTWARE_ENG', 8.0

    # 3. Default Subscribed vs Tangential
    return 'GENERAL', 1.0

def main():
    if not os.path.exists(QUEUE_FILE):
        print("Queue file not found.")
        return

    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    print(f"Total Queue Items: {len(queue):,}")

    # Separate items into priority buckets
    swe_items = []
    sub_general_items = []
    tang_general_items = []
    lang_items = []

    for item in queue:
        ch_name = item.get('channel_name', '')
        handle = item.get('channel_handle', '')
        title = item.get('title', '')
        cat = item.get('category', 'Tangential')

        p_type, multiplier = classify_channel_priority(ch_name, handle, title)
        item['domain_type'] = p_type

        if p_type == 'LANGUAGE':
            item['domain_weight'] = 0.25
            lang_items.append(item)
        elif p_type == 'SOFTWARE_ENG':
            item['domain_weight'] = 8.0
            swe_items.append(item)
        else:
            if cat == 'Subscribed':
                item['domain_weight'] = 4.0
                sub_general_items.append(item)
            else:
                item['domain_weight'] = 1.0
                tang_general_items.append(item)

    print(f"\n📊 Priority Bucket Counts:")
    print(f"  💻 Software Engineering (8.0x Weight): {len(swe_items):,} items")
    print(f"  ⭐ General Subscribed (4.0x Weight):    {len(sub_general_items):,} items")
    print(f"  🔹 General Tangential (1.0x Weight):    {len(tang_general_items):,} items")
    print(f"  🌐 French / Spanish Languages (0.25x):   {len(lang_items):,} items")

    # Weighted Interleaving: 8 Software Eng : 4 General Subscribed : 1 General Tangential : 0.25 Language
    # In each round: 8 SWE, 4 General Sub, 1 General Tangential, 0.25 Language (1 per 4 rounds)
    new_queue = []
    swe_idx = 0
    sub_idx = 0
    tang_idx = 0
    lang_idx = 0

    round_count = 0

    while (swe_idx < len(swe_items) or sub_idx < len(sub_general_items) or
           tang_idx < len(tang_general_items) or lang_idx < len(lang_items)):
        round_count += 1

        # 1. Take up to 8 Software Engineering items
        for _ in range(8):
            if swe_idx < len(swe_items):
                new_queue.append(swe_items[swe_idx])
                swe_idx += 1

        # 2. Take up to 4 General Subscribed items
        for _ in range(4):
            if sub_idx < len(sub_general_items):
                new_queue.append(sub_general_items[sub_idx])
                sub_idx += 1

        # 3. Take 1 General Tangential item
        if tang_idx < len(tang_general_items):
            new_queue.append(tang_general_items[tang_idx])
            tang_idx += 1

        # 4. Take 1 Language item every 4th round (giving 4:1 language de-prioritization)
        if round_count % 4 == 0 and lang_idx < len(lang_items):
            new_queue.append(lang_items[lang_idx])
            lang_idx += 1

    # Recalculate sequence steps and cumulative cost/hours
    cum_cost = 0.0
    cum_hours = 0.0
    FREE_TIER_LIMIT_USD = 9.40

    for step_i, item in enumerate(new_queue, 1):
        item['sequence_step'] = step_i
        cost = item.get('cost_usd', 0.002)
        dur_hrs = item.get('duration_min', 15.0) / 60.0

        cum_cost += cost
        cum_hours += dur_hrs

        item['cum_cost_usd'] = round(cum_cost, 4)
        item['cum_hours'] = round(cum_hours, 1)
        item['is_free_covered'] = (cum_cost <= FREE_TIER_LIMIT_USD)
        item['weighted_roi_score'] = round(item.get('roi_score', 1000) * item['domain_weight'], 1)

    # Save updated queue
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_queue, f, indent=2, ensure_ascii=False)

    # Re-generate pending_real_video_downloads.json with new domain priority order
    pending_real = [item for item in new_queue if item.get('video_id') and len(str(item.get('video_id'))) == 11]
    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump(pending_real, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 Successfully re-sequenced queue with Domain-Weighted Priority!")
    print(f"   - Updated Queue Saved to: {QUEUE_FILE}")
    print(f"   - Re-ordered Real Pending Video Queue: {len(pending_real)} items in {PENDING_FILE}")

    print("\nTop 25 items in new Domain-Prioritized Queue:")
    for item in new_queue[:25]:
        dtype = item['domain_type']
        badge = "💻 [SOFTWARE ENG 8X]" if dtype == 'SOFTWARE_ENG' else ("⭐ [GENERAL SUB 4X]" if item['category'] == 'Subscribed' else ("🔻 [LANGUAGE 0.25X]" if dtype == 'LANGUAGE' else "🔹 [TANGENTIAL 1X]"))
        print(f"  Step #{item['sequence_step']:04d}: {badge} {item['channel_name']} - '{item['title'][:35]}'")

if __name__ == '__main__':
    main()
