#!/usr/bin/env python3
import json
import os

QUEUE_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json"
PENDING_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/pending_real_video_downloads.json"

def main():
    if not os.path.exists(QUEUE_FILE):
        print("Queue file not found.")
        return

    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    print(f"Original Queue Length: {len(queue):,} items")

    # 4:1 Subscribed Weighting Logic
    # 1. Separate into Subscribed vs Tangential queues
    sub_items = [item for item in queue if item.get('category') == 'Subscribed']
    tang_items = [item for item in queue if item.get('category') != 'Subscribed']

    print(f"  - Subscribed Queue Items: {len(sub_items):,}")
    print(f"  - Tangential Queue Items: {len(tang_items):,}")

    # 2. Interleave 4 Subscribed : 1 Tangential
    new_queue = []
    sub_idx = 0
    tang_idx = 0

    while sub_idx < len(sub_items) or tang_idx < len(tang_items):
        # Take up to 4 Subscribed items
        for _ in range(4):
            if sub_idx < len(sub_items):
                new_queue.append(sub_items[sub_idx])
                sub_idx += 1

        # Take 1 Tangential item
        if tang_idx < len(tang_items):
            new_queue.append(tang_items[tang_idx])
            tang_idx += 1

    # 3. Recalculate sequence steps and cumulative cost/hours
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

        # Apply 4x ROI boost tag for Subscribed items
        if item.get('category') == 'Subscribed':
            item['weighted_roi_score'] = round(item.get('roi_score', 1000) * 4.0, 1)
        else:
            item['weighted_roi_score'] = round(item.get('roi_score', 1000) * 1.0, 1)

    # Save updated queue
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_queue, f, indent=2, ensure_ascii=False)

    # Re-generate pending_real_video_downloads.json with new 4:1 priority order
    pending_real = [item for item in new_queue if item.get('video_id') and len(str(item.get('video_id'))) == 11]
    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump(pending_real, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 Successfully re-sequenced queue with 4:1 Subscribed Priority Interleaving!")
    print(f"   - Updated Queue Saved to: {QUEUE_FILE}")
    print(f"   - Re-ordered Real Pending Video Queue: {len(pending_real)} items in {PENDING_FILE}")

    # Display first 20 items of new 4:1 prioritized queue
    print("\nTop 20 items in new 4:1 Prioritized Queue:")
    for item in new_queue[:20]:
        cat_badge = "⭐ [SUBSCRIBED 4X]" if item['category'] == 'Subscribed' else "🔹 [TANGENTIAL 1X]"
        print(f"  Step #{item['sequence_step']:04d}: {cat_badge} {item['channel_name']} - '{item['title'][:35]}'")

if __name__ == '__main__':
    main()
