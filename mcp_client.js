const { spawn } = require('child_process');

const mcpProc = spawn('/Users/austinrognes/.nvm/versions/node/v20.19.6/bin/npx', [
    '-y',
    'mcp-remote',
    'https://transcriptapi.com/mcp',
    '--header',
    'Authorization: Bearer sk_JaAysZu79sqC3_fBTneaD3FcFXuhiz1Br9a862wb8JM'
], {
    stdio: ['pipe', 'pipe', 'inherit']
});

let buffer = '';

mcpProc.stdout.on('data', (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split('\n');
    buffer = lines.pop(); // keep last incomplete line

    for (const line of lines) {
        if (!line.trim()) continue;
        try {
            const msg = JSON.parse(line);
            console.log('MCP Response:', JSON.stringify(msg, null, 2));
        } catch (e) {
            console.log('RAW output:', line);
        }
    }
});

// Step 1: Initialize
const initMsg = {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "node-mcp-client", version: "1.0.0" }
    }
};

mcpProc.stdin.write(JSON.stringify(initMsg) + '\n');

setTimeout(() => {
    // Step 2: Call get_youtube_transcript
    const callMsg = {
        jsonrpc: "2.0",
        id: 2,
        method: "tools/call",
        params: {
            name: "get_youtube_transcript",
            arguments: { video_url: "b-P5ZQ1NxxE" }
        }
    };
    mcpProc.stdin.write(JSON.stringify(callMsg) + '\n');
}, 1500);

setTimeout(() => {
    mcpProc.kill();
}, 5000);
