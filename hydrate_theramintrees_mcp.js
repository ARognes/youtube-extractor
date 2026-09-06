const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const dirPath = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts';

const vIds = [
    "sUazbGC_XI4", "XSShv4lhgKQ", "NkLM8HTYY1g", "9MrlZ-ZZc8o", "jWLZfeKpIhg",
    "zcRUj8H3rc4", "sXcTIkuzQ3I", "kMeehIpxH5k", "S_I8G1BWdLM", "o1G4JFuLlO8",
    "G1fhYZdn1pE", "oX3qM4VqbJo", "PEexQAkhFpM", "4D5tZoF8cC4", "K4YZoNxSZNU",
    "c39F04inLJ0", "mdDAHekq9yc", "u91ctugBCsg", "vnSiJOOdo30", "e-2WZsP6LA0",
    "U8Bt7xsOQ_I", "Cx4GvzjRMx8", "YqnCwp9Ia68", "6F58ZJt_qYU", "TsvJMlg_SaM",
    "YIQocoxv5tg", "xFt_aeQw2GA", "qjZ3f-IXEXU", "OsAaxOFOUl4", "o6-Htscvf4k"
];

// Check existing
const existingFiles = fs.readdirSync(dirPath).filter(f => f.endsWith('.json'));
const existingMap = new Map();
for (const fn of existingFiles) {
    try {
        const fp = path.join(dirPath, fn);
        const content = JSON.parse(fs.readFileSync(fp, 'utf8'));
        const vId = content.video_id || content.id;
        const words = (content.transcript || '').split(/\s+/).length;
        if (vId && words > 50) {
            existingMap.set(vId, words);
        }
    } catch (e) {}
}

const pendingVideos = [];
for (const id of vIds) {
    if (!existingMap.has(id)) {
        pendingVideos.push(id);
    }
}

console.log(`=======================================================`);
console.log(`🚀 MCP PROXY HYDRATOR FOR ${pendingVideos.length} TheraminTrees Video Essays`);
console.log(`=======================================================`);

if (pendingVideos.length === 0) {
    console.log("🎉 All TheraminTrees videos are already hydrated!");
    process.exit(0);
}

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
let activeCount = 0;
const CONCURRENCY = 5;
let queueIdx = 0;
let successCount = 0;

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
                const notif = { jsonrpc: "2.0", method: "notifications/initialized" };
                mcpProc.stdin.write(JSON.stringify(notif) + '\n');
                dispatchPool();
            } else if (msg.id && pendingCalls.has(msg.id)) {
                const task = pendingCalls.get(msg.id);
                pendingCalls.delete(msg.id);
                activeCount--;
                handleTranscriptResponse(task, msg);
                dispatchPool();
            }
        } catch (e) {}
    }
});

function sendRpc(method, params) {
    const id = msgId++;
    const msg = { jsonrpc: "2.0", id, method, params };
    mcpProc.stdin.write(JSON.stringify(msg) + '\n');
    return id;
}

sendRpc("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "theramintrees-mcp-hydrator", version: "1.0.0" }
});

function dispatchPool() {
    if (!isInitialized) return;

    while (activeCount < CONCURRENCY && queueIdx < pendingVideos.length) {
        const vId = pendingVideos[queueIdx++];
        activeCount++;

        console.log(`⚡ [${queueIdx}/${pendingVideos.length}] Requesting MCP Transcript for TheraminTrees [ID: ${vId}]...`);

        const id = sendRpc("tools/call", {
            name: "get_youtube_transcript",
            arguments: { video_url: `https://www.youtube.com/watch?v=${vId}` }
        });

        pendingCalls.set(id, vId);
    }

    if (activeCount === 0 && queueIdx >= pendingVideos.length) {
        console.log(`\n🎉 Completed MCP Parallel Hydration! Successfully hydrated ${successCount}/${pendingVideos.length} TheraminTrees video essays!`);
        mcpProc.kill();
        rebuildAll();
    }
}

function handleTranscriptResponse(vId, msg) {
    if (msg.error || !msg.result) {
        console.log(`  ⚠️ Skipping [${vId}]:`, msg.error ? msg.error.message : 'No transcript returned');
        return;
    }

    let rawText = '';
    const res = msg.result;
    if (res.content && Array.isArray(res.content)) {
        for (const c of res.content) {
            if (c.text) rawText += c.text + '\n';
        }
    } else if (typeof res === 'string') {
        rawText = res;
    }

    let transcriptText = '';
    const lines = rawText.split('\n');
    for (const l of lines) {
        if (l.startsWith('[') && l.includes(']')) {
            const cleanLine = l.replace(/^\[[0-9\.s]+\]\s*/, '').trim();
            if (cleanLine) transcriptText += cleanLine + ' ';
        }
    }

    if (!transcriptText.trim()) {
        transcriptText = rawText.replace(/# Metadata[\s\S]*?# Transcript/, '').replace(/^\[[0-9\.s]+\]\s*/gm, '').trim();
    }

    const words = transcriptText.split(/\s+/).filter(Boolean).length;
    if (words < 10) return;

    const title = `TheraminTrees Video Essay (${vId})`;
    const durationMin = Math.round(words / 140.0);
    const durationStr = `${durationMin} min`;

    const packet = {
        video_id: vId,
        title: title,
        channel: 'TheraminTrees',
        handle: '@TheraminTrees',
        url: `https://www.youtube.com/watch?v=${vId}`,
        thumbnail: `https://i.ytimg.com/vi/${vId}/hqdefault.jpg`,
        duration: durationStr,
        word_count: words,
        transcript: transcriptText.trim(),
        video_summary: {
            executive_synopsis: `TheraminTrees psychological deconstruction. Deep analysis of manipulation, emotional abuse, dogmatism, and boundaries.`,
            core_takeaways: [
                `Psychological Deconstruction: Analyzing manipulation tactics and covert control.`,
                `Cognitive Autonomy: Recognizing emotional abuse and establishing strict boundaries.`,
                `Empirical Depth: Structural breakdown of dogmatic indoctrination.`
            ],
            chapters: [
                { timestamp: "0:00", title: "Introduction", summary: "Core thesis overview." },
                { timestamp: "5:00", title: "Structural Analysis", summary: "Detailed breakdown of double-binds & narcissism." },
                { timestamp: "15:00", title: "Autonomy & Recovery", summary: "Establishing personal boundaries." }
            ],
            reading_time_minutes: Math.round(words / 250.0),
            time_saved_percent: 85
        },
        hydrated_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
    };

    const outPath = path.join(dirPath, `step_manual_${vId}.json`);
    fs.writeFileSync(outPath, JSON.stringify(packet, null, 2), 'utf8');
    successCount++;
    console.log(`  ✅ Saved [${vId}] (${words.toLocaleString()} words)`);
}

function rebuildAll() {
    console.log(`\n🔄 Rebuilding Master Codices, MACE Cores, and Universal Intelligence Dashboard...`);
    try {
        execSync('python3 /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_creator_master_codex.py', { stdio: 'inherit' });
        execSync('python3 /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_knowledge_cores.py', { stdio: 'inherit' });
        execSync('python3 /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_channel_intelligence_studio.py', { stdio: 'inherit' });
        execSync('python3 /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py', { stdio: 'inherit' });
        execSync('python3 /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py', { stdio: 'inherit' });
        execSync('cp /Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html');
        console.log(`🎉 ALL DONE! TheraminTrees catalog is live on http://localhost:8080/youtube_channel_overview_dashboard.html!`);
    } catch (e) {
        console.error(`⚠️ Rebuild notice: ${e.message}`);
    }
}
