import os
import sys
import json

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'

def fuse_cores(core_ids):
    fused_first_principles = []
    fused_taxonomy = {}
    fused_playbooks = []
    channels_combined = set()
    total_words = 0
    total_vids = 0

    seen_principles = set()

    for cid in core_ids:
        fn = f"{cid}_master_archive.json"
        fp = os.path.join(SCRATCH_DIR, fn)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                cdata = json.load(f)
                total_words += cdata.get('total_spoken_words', 0)
                total_vids += cdata.get('total_videos_archived', 0)
                channels_combined.update(cdata.get('channels_included', []))

                for pr in cdata.get('first_principles', []):
                    if pr not in seen_principles:
                        seen_principles.add(pr)
                        fused_first_principles.append(pr)

                for k, v in cdata.get('taxonomy_dictionary', {}).items():
                    fused_taxonomy[k] = v

    fused = {
        "fused_cores": core_ids,
        "title": f"Fused Archival Core ({', '.join(core_ids)})",
        "channels_included": sorted(list(channels_combined)),
        "total_videos_archived": total_vids,
        "total_spoken_words": total_words,
        "first_principles": fused_first_principles,
        "taxonomy_dictionary": fused_taxonomy
    }
    return fused

if __name__ == '__main__':
    res = fuse_cores(['core_software_engineering', 'core_business_monetization'])
    print(json.dumps(res, indent=2))
