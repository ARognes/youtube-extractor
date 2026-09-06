const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const pendingPath = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/pending_real_video_downloads.json';
const dirPath = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts';

if (!fs.existsSync(pendingPath)) {
    console.log('No pending_real_video_downloads.json file found.');
    process.exit(0);
}

const pendingList = JSON.parse(fs.readFileSync(pendingPath, 'utf8'));
console.log(`🚀 Starting Pure-MCP Video Transcript Hydrator across ${pendingList.length} Real Videos...`);

const env = Object.assign({}, process.env, {
    PATH: `/Users/austinrognes/.nvm/versions/node/v20.19.6/bin:${process.env.PATH}`
});

const mcpProc = spawn('/Users/austinrognes/.nvm/versions/node/v20.19.6/bin/npx', [
    '-y',
    'mcp-remote',
    'https://transcriptapi.com/mcp',
    '--header',
    'Authorization: Bearer " + (process.env.TRANSCRIPT_API_KEY || "") + "'
], { env, stdio: ['pipe', 'pipe', 'inherit'] });

let msgId = 1;
const pendingCalls = new Map();
let isInitialized = false;

let buffer = '';
mcpProc.stdout.on('data', (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
        if (!line.trim()) continue;
        try {
            const msg = JSON.parse(line);
            if (msg.id === 1 && !isInitialized) {
                isInitialized = true;
                // Send initialized notification
                const notif = { jsonrpc: "2.0", method: "notifications/initialized" };
                mcpProc.stdin.write(JSON.stringify(notif) + '\n');
                processNext();
            } else if (msg.id && pendingCalls.has(msg.id)) {
                const item = pendingCalls.get(msg.id);
                pendingCalls.delete(msg.id);
                handleTranscriptResponse(item, msg);
            }
        } catch (e) {
            // Ignore non-JSON logs
        }
    }
});

function sendRpc(method, params) {
    const id = msgId++;
    const msg = { jsonrpc: "2.0", id, method, params };
    mcpProc.stdin.write(JSON.stringify(msg) + '\n');
    return id;
}

// Send initialize (ID: 1)
sendRpc("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "node-mcp-client", version: "1.0.0" }
});

let currentIdx = 0;

function processNext() {
    if (currentIdx >= pendingList.length) {
        console.log("🎉 All pending real videos processed cleanly via MCP!");
        mcpProc.kill();
        process.exit(0);
    }

    const item = pendingList[currentIdx++];
    const v_id = item.video_id;

    // Check if already downloaded
    const existing = fs.readdirSync(dirPath).filter(f => f.includes(v_id) && !f.startsWith('step_0001_lemondefr'));
    if (existing.length > 0) {
        processNext();
        return;
    }

    console.log(`⚡ [${currentIdx}/${pendingList.length}] Requesting MCP Transcript for '${item.title.substring(0, 45)}' (${item.channel_name}) [ID: ${v_id}]`);

    const id = sendRpc("tools/call", {
        name: "get_youtube_transcript",
        arguments: { video_url: v_id }
    });

    pendingCalls.set(id, item);
}

function handleTranscriptResponse(item, msg) {
    if (msg.error) {
        console.log(`  ⚠️ Error fetching ${item.video_id}:`, msg.error.message);
        setTimeout(processNext, 500);
        return;
    }

    const res = msg.result;
    if (!res) {
        console.log(`  ⚠️ Empty result for ${item.video_id}`);
        setTimeout(processNext, 500);
        return;
    }

    let rawContent = res;
    if (res.content && res.content[0] && res.content[0].text) {
        try { rawContent = JSON.parse(res.content[0].text); } catch (e) {}
    }

    let segs = [];
    let fullText = "";

    if (Array.isArray(rawContent)) {
        segs = rawContent;
        fullText = segs.map(s => s.text || '').join(' ');
    } else if (typeof rawContent === 'object' && rawContent !== null) {
        if (Array.isArray(rawContent.transcript)) segs = rawContent.transcript;
        else if (Array.isArray(rawContent.results)) segs = rawContent.results;
        fullText = segs.map(s => s.text || '').join(' ');
    }

    if (!fullText || fullText.split(' ').length < 10) {
        console.log(`  ⚠️ No valid transcript text for ${item.video_id}`);
        setTimeout(processNext, 500);
        return;
    }

    const pkt = {
        step_number: item.sequence_step,
        video_id: item.video_id,
        title: item.title,
        channel: item.channel_name,
        handle: item.channel_handle || '',
        duration: item.duration_min || 15,
        duration_seconds: Math.round((item.duration_min || 15) * 60),
        url: `https://www.youtube.com/watch?v=${item.video_id}`,
        transcript: fullText,
        raw_segments: segs
    };

    const fn = `step_${String(item.sequence_step).padStart(4, '0')}_${item.video_id}.json`;
    fs.writeFileSync(path.join(dirPath, fn), JSON.stringify(pkt, null, 2));

    console.log(`  ✓ Saved '${item.title.substring(0, 40)}' (${fullText.split(' ').length.toLocaleString()} words) -> ${fn}`);

    // Trigger dataset & dashboard update
    spawn('/Users/austinrognes/miniconda3/bin/python3', ['/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py']);
    spawn('/Users/austinrognes/miniconda3/bin/python3', ['/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py']);
    spawn('cp', ['/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html', '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/']);

    setTimeout(processNext, 600);
}
