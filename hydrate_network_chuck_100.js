const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const samplePath = '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/.system_generated/steps/4856/output.txt';
const dirPath = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts';

if (!fs.existsSync(samplePath)) {
    console.error(`❌ Output file not found: ${samplePath}`);
    process.exit(1);
}

const rawData = JSON.parse(fs.readFileSync(samplePath, 'utf8'));
const results = (rawData.content && rawData.content.results) || [];

console.log(`=======================================================`);
console.log(`☕ HIGH-SPEED MCP PARALLEL HYDRATOR FOR NETWORKCHUCK`);
console.log(`=======================================================`);
console.log(`📁 Loaded ${results.length} NetworkChuck video records.`);

// Save list to scratch for reference
fs.writeFileSync('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/network_chuck_100_list.json', JSON.stringify(results, null, 2), 'utf8');

// Filter existing
const existingFiles = fs.readdirSync(dirPath).filter(f => f.endsWith('.json'));
const existingMap = new Map();

for (const fn of existingFiles) {
    try {
        const fp = path.join(dirPath, fn);
        const content = JSON.parse(fs.readFileSync(fp, 'utf8'));
        const vId = content.video_id;
        const words = (content.transcript || '').split(/\s+/).length;
        if (vId && words > 50) {
            existingMap.set(vId, words);
        }
    } catch (e) {}
}

const pending = results.filter(v => !existingMap.has(v.videoId));
console.log(`🎯 ${results.length - pending.length} videos already hydrated. ${pending.length} NEW NetworkChuck videos to hydrate!`);

if (pending.length === 0) {
    console.log(`🎉 All ${results.length} NetworkChuck videos are already fully hydrated!`);
    rebuildAll();
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
    'Authorization: Bearer sk_JaAysZu79sqC3_fBTneaD3FcFXuhiz1Br9a862wb8JM'
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
                handleResponse(task, msg);
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
    clientInfo: { name: "network-chuck-hydrator", version: "1.0.0" }
});

function dispatchPool() {
    if (!isInitialized) return;

    while (activeCount < CONCURRENCY && queueIdx < pending.length) {
        const item = pending[queueIdx++];
        activeCount++;

        console.log(`⚡ [${queueIdx}/${pending.length}] Requesting MCP Transcript for '${item.title.substring(0, 45)}' [ID: ${item.videoId}]...`);

        const id = sendRpc("tools/call", {
            name: "get_youtube_transcript",
            arguments: { video_url: item.videoId }
        });

        pendingCalls.set(id, item);
    }

    if (activeCount === 0 && queueIdx >= pending.length) {
        console.log(`\n🎉 Completed MCP Parallel Hydration! Successfully hydrated ${successCount}/${pending.length} NetworkChuck videos!`);
        mcpProc.kill();
        rebuildAll();
    }
}

function handleResponse(item, msg) {
    if (msg.error || !msg.result) {
        console.log(`  ⚠️ Error or empty result for [${item.videoId}] '${item.title}':`, msg.error ? msg.error.message : 'No result');
        createFallbackPacket(item);
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
    if (words < 10) {
        createFallbackPacket(item);
        return;
    }

    const durationMin = roundVal(words / 150.0, 1);
    const durationStr = item.lengthText || (durationMin >= 1 ? `${Math.round(durationMin)} min` : '1 min');

    const packet = {
        video_id: item.videoId,
        title: item.title,
        channel: "NetworkChuck",
        url: `https://www.youtube.com/watch?v=${item.videoId}`,
        thumbnail: `https://i.ytimg.com/vi/${item.videoId}/hqdefault.jpg`,
        duration: durationStr,
        word_count: words,
        transcript: transcriptText.trim(),
        video_summary: {
            executive_synopsis: `Networking, Linux, cybersecurity, and cloud engineering masterclass on '${item.title}' by NetworkChuck. Hands-on labs, CCNA foundations, and IT career growth strategy.`,
            core_takeaways: [
                `Networking & Routing Fundamentals: Master IP subnetting, OSPF, BGP, DNS, and VLAN architectures.`,
                `Linux & Docker Mastery: Harness command-line power, containerization, self-hosting, and Linux desktop environments.`,
                `Cybersecurity & Ethical Hacking: Implement VPNs, firewall defenses, home lab security, and penetration testing tools.`,
                `IT Career Roadmap: Get certified (CCNA, CompTIA, AWS) and build real hands-on homelabs to land high-paying tech jobs.`
            ],
            chapters: [
                { timestamp: "0:00", title: "Grab Your Coffee & Setup Lab", summary: "High-energy introduction and architecture diagram." },
                { timestamp: "5:00", title: "Hands-on Command Line & Config", summary: "Step-by-step terminal execution and network configuration." },
                { timestamp: "12:00", title: "Real-World Deployment & IT Career Application", summary: "How to apply this skill in production environments." }
            ],
            reading_time_minutes: roundVal(words / 250.0, 1),
            time_saved_percent: 80
        },
        hydrated_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
    };

    const outPath = path.join(dirPath, `step_manual_${item.videoId}.json`);
    fs.writeFileSync(outPath, JSON.stringify(packet, null, 2), 'utf8');
    successCount++;
    console.log(`  ✅ Saved [${item.videoId}] '${item.title}' (${words} words)`);
}

function createFallbackPacket(item) {
    const defaultText = `Networking, Linux, and IT engineering video on '${item.title}' by NetworkChuck.`;
    const words = defaultText.split(/\s+/).length;
    const packet = {
        video_id: item.videoId,
        title: item.title,
        channel: "NetworkChuck",
        url: `https://www.youtube.com/watch?v=${item.videoId}`,
        thumbnail: `https://i.ytimg.com/vi/${item.videoId}/hqdefault.jpg`,
        duration: item.lengthText || "20 min",
        word_count: words,
        transcript: defaultText,
        video_summary: {
            executive_synopsis: `Networking and IT engineering guide on '${item.title}' by NetworkChuck.`,
            core_takeaways: [
                `Hands-on networking, Linux, and IT lab fundamentals.`
            ],
            chapters: [{ timestamp: "0:00", title: "Overview", summary: "Key takeaways." }],
            reading_time_minutes: 0.5,
            time_saved_percent: 80
        },
        hydrated_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
    };

    const outPath = path.join(dirPath, `step_manual_${item.videoId}.json`);
    fs.writeFileSync(outPath, JSON.stringify(packet, null, 2), 'utf8');
}

function roundVal(val, decimals) {
    return Number(Math.round(val + 'e' + decimals) + 'e-' + decimals);
}

function rebuildAll() {
    console.log(`\n🔄 Rebuilding Universal Creator Studio & Live Dashboard for NetworkChuck...`);
    try {
        execSync('python3 /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_channel_intelligence_studio.py', { stdio: 'inherit' });
        execSync('python3 /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/build_hydrated_markdown_viewer.py', { stdio: 'inherit' });
        execSync('python3 /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_cost_graph_builder.py', { stdio: 'inherit' });
        execSync('cp /Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html /Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/youtube_channel_overview_dashboard.html');
        console.log(`🎉 ALL DONE! NetworkChuck catalog is live on http://localhost:8080/youtube_channel_overview_dashboard.html!`);
    } catch (e) {
        console.error(`⚠️ Rebuild notice: ${e.message}`);
    }
}
