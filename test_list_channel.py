import urllib.request, json

url = "https://transcriptapi.com/mcp"
headers = {
    "Authorization": "Bearer sk_JaAysZu79sqC3_fBTneaD3FcFXuhiz1Br9a862wb8JM",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "list_channel_videos",
        "arguments": {"channel": "@PhilipDeFranco"}
    }
}
req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
        for line in body.splitlines():
            if line.startswith("data: "):
                obj = json.loads(line[6:])
                if "result" in obj:
                    res = obj["result"]
                    print("Status: Success!")
                    content = res.get("content", {})
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except:
                            pass
                    if isinstance(content, dict):
                        videos = content.get("results") or content.get("videos") or []
                        print(f"Got {len(videos)} videos")
                        cont = content.get("continuation") or content.get("continuation_token")
                        print("Continuation token present:", bool(cont))
                        if videos:
                            print("First video:", videos[0].get("title"))
                            print("Last video:", videos[-1].get("title"))
                    else:
                        print("Content type:", type(content))
except Exception as e:
    print("Error:", e)
