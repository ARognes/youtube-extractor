import os
import sys
import json
import re

SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'
TRANSCRIPTS_DIR = os.path.join(SCRATCH_DIR, 'downloaded_transcripts')

def audit_version_tags():
    print("⚡ Auditing transcripts for software versioning & temporal tags...", flush=True)

    files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith('.json')]
    version_audit = {
        "legacy_versions_flagged": [],
        "current_versions_flagged": [],
        "total_audited_videos": len(files)
    }

    legacy_patterns = [r"python 2\.[0-7]", r"react 15", r"angularjs", r"docker 1\."]
    current_patterns = [r"python 3\.1[0-3]", r"react 1[8-9]", r"next\.js 14", r"rust 2024"]

    for f in files:
        fp = os.path.join(TRANSCRIPTS_DIR, f)
        try:
            with open(fp, 'r', encoding='utf-8') as jf:
                pkt = json.load(jf)
                text = (pkt.get('transcript') or '').lower()
                title = pkt.get('title') or ''

                for lp in legacy_patterns:
                    if re.search(lp, text):
                        version_audit["legacy_versions_flagged"].append({
                            "title": title,
                            "pattern": lp,
                            "status": "LEGACY_DEPRECATED"
                        })

                for cp in current_patterns:
                    if re.search(cp, text):
                        version_audit["current_versions_flagged"].append({
                            "title": title,
                            "pattern": cp,
                            "status": "CURRENT_RECOMMENDED"
                        })
        except Exception:
            pass

    out_path = os.path.join(SCRATCH_DIR, 'version_deprecation_audit.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(version_audit, f, indent=2)

    print(f"🎉 Version Audit Complete! Flagged {len(version_audit['legacy_versions_flagged'])} legacy & {len(version_audit['current_versions_flagged'])} current version references. Saved to {out_path}", flush=True)
    return version_audit

if __name__ == '__main__':
    audit_version_tags()
