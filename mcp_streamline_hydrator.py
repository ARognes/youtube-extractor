#!/usr/bin/env python3
import os
import sys
import json
import time
import urllib.request
import urllib.error
import subprocess

PENDING_FILE = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/pending_real_video_downloads.json"
TRANSCRIPTS_DIR = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts"
DASHBOARD_SRC = "/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html"
DASHBOARD_DST = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html"

TRANSCRIPTAPI_KEY = "sk_JaAysZu79sqC3_fBTneaD3FcFXuhiz1Br9a862wb8JM"
SUPADATA_KEY = "sd_32b8567c225df115f94f200dde8b8b61"

def call_transcriptapi_mcp(video_id):
    url = "https://transcriptapi.com/mcp"
    headers = {
        "Authorization": f"Bearer {TRANSCRIPTAPI_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_youtube_transcript",
            "arguments": {"video_url": video_id}
        }
    }
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            for line in body.splitlines():
                if line.startswith("data: "):
                    line = line[6:]
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    if "result" in obj:
                        return obj["result"]
                except Exception:
                    pass
    except Exception as e:
        print(f"    [transcriptapi error]: {e}", flush=True)
    return None

def call_supadata_mcp(video_id):
    url = "https://api.supadata.ai/mcp"
    headers = {
        "x-api-key": SUPADATA_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "supadata_transcript",
            "arguments": {"url": f"https://www.youtube.com/watch?v={video_id}"}
        }
    }
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            for line in body.splitlines():
                if line.startswith("data: "):
                    line = line[6:]
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    if "result" in obj:
                        return obj["result"]
                except Exception:
                    pass
    except Exception as e:
        print(f"    [supadata error]: {e}", flush=True)
    return None

def parse_mcp_result(res):
    if not res:
        return None, []
    
    raw = res
    if isinstance(res, dict) and "content" in res and isinstance(res["content"], list):
        if len(res["content"]) > 0 and "text" in res["content"][0]:
            try:
                raw = json.loads(res["content"][0]["text"])
            except Exception:
                raw = res["content"][0]["text"]

    segs = []
    full_text = ""
    
    if isinstance(raw, list):
        segs = raw
        full_text = " ".join([s.get("text", "") for s in segs if isinstance(s, dict)])
    elif isinstance(raw, dict):
        if "transcript" in raw and isinstance(raw["transcript"], list):
            segs = raw["transcript"]
            full_text = " ".join([s.get("text", "") for s in segs if isinstance(s, dict)])
        elif "results" in raw and isinstance(raw["results"], list):
            segs = raw["results"]
            full_text = " ".join([s.get("text", "") for s in segs if isinstance(s, dict)])
        elif "content" in raw and isinstance(raw["content"], list):
            segs = raw["content"]
            full_text = " ".join([s.get("text", "") for s in segs if isinstance(s, dict)])

    return full_text.strip(), segs

def rebuild_dashboard():
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["python3", "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(DASHBOARD_SRC):
        subprocess.run(["cp", DASHBOARD_SRC, DASHBOARD_DST], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    if not os.path.exists(PENDING_FILE):
        print(f"Pending file {PENDING_FILE} does not exist.", flush=True)
        return

    with open(PENDING_FILE, 'r', encoding='utf-8') as f:
        pending_list = json.load(f)

    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    existing_files = os.listdir(TRANSCRIPTS_DIR)

    print(f"🚀 Starting 100% Pure-MCP Proxy Hydrator over HTTP across {len(pending_list)} pending videos...", flush=True)
    print("🛡️ Zero local YouTube connections. All calls route through transcriptapi & supadata MCP servers.\n", flush=True)

    success_count = 0

    for idx, item in enumerate(pending_list, 1):
        v_id = item.get("video_id")
        if not v_id:
            continue

        # Check if already present
        already_has = any(v_id in fn and not fn.startswith("step_0001_lemondefr") for fn in existing_files)
        if already_has:
            continue

        title = item.get("title", "Untitled")
        channel = item.get("channel_name", "Unknown Channel")
        seq_step = item.get("sequence_step", idx)

        print(f"⚡ [{idx}/{len(pending_list)}] Requesting MCP Transcript for '{title[:45]}' ({channel}) [ID: {v_id}]...", flush=True)

        # Step 1: Call transcriptapi MCP
        res = call_transcriptapi_mcp(v_id)
        full_text, segs = parse_mcp_result(res)

        # Step 2: Fallback to supadata MCP if empty
        if not full_text or len(full_text.split()) < 10:
            print("    -> transcriptapi empty/404, falling back to supadata MCP...", flush=True)
            res_supa = call_supadata_mcp(v_id)
            full_text, segs = parse_mcp_result(res_supa)

        word_count = len(full_text.split()) if full_text else 0

        if word_count < 10:
            print(f"  ⚠️ No captions/transcript found via MCP proxy for {v_id}", flush=True)
            time.sleep(0.3)
            continue

        pkt = {
            "step_number": seq_step,
            "video_id": v_id,
            "title": title,
            "channel": channel,
            "handle": item.get("channel_handle", ""),
            "duration": item.get("duration_min", 15),
            "duration_seconds": int(round(item.get("duration_min", 15) * 60)),
            "url": f"https://www.youtube.com/watch?v={v_id}",
            "transcript": full_text,
            "raw_segments": segs
        }

        fn = f"step_{seq_step:04d}_{v_id}.json"
        out_path = os.path.join(TRANSCRIPTS_DIR, fn)
        with open(out_path, 'w', encoding='utf-8') as out_f:
            json.dump(pkt, out_f, indent=2, ensure_ascii=False)

        existing_files.append(fn)
        success_count += 1
        print(f"  ✓ Saved '{title[:35]}' ({word_count:,} words) -> {fn}", flush=True)

        # Rebuild live dashboard immediately
        rebuild_dashboard()
        print(f"  🎉 Dashboard rebuilt live! Progress: {success_count} new transcripts added.", flush=True)

        time.sleep(0.3)

    print("\n🎉 Pure-MCP Transcript Hydration completed cleanly!", flush=True)

if __name__ == "__main__":
    main()
