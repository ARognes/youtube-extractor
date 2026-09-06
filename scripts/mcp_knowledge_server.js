const fs = require('fs');
const path = require('path');
const readline = require('readline');

const SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

function logErr(msg) {
    fs.appendFileSync(path.join(SCRATCH_DIR, 'mcp_server.log'), `[${new Date().toISOString()}] ${msg}\n`);
}

logErr("🚀 MACE Modular Knowledge MCP Server initialized.");

rl.on('line', (line) => {
    if (!line.trim()) return;
    try {
        const msg = JSON.parse(line);
        handleRpcMessage(msg);
    } catch (e) {
        logErr(`JSON Parse Error: ${e.message}`);
    }
});

function sendRpcResponse(id, result, error = null) {
    const resp = { jsonrpc: "2.0", id };
    if (error) {
        resp.error = error;
    } else {
        resp.result = result;
    }
    process.stdout.write(JSON.stringify(resp) + '\n');
}

function handleRpcMessage(msg) {
    const { id, method, params } = msg;

    if (method === 'initialize') {
        sendRpcResponse(id, {
            protocolVersion: "2024-11-05",
            capabilities: {
                tools: {}
            },
            serverInfo: {
                name: "mace-knowledge-cores-server",
                version: "1.0.0"
            }
        });
    } else if (method === 'tools/list') {
        sendRpcResponse(id, {
            tools: [
                {
                    name: "list_knowledge_cores",
                    description: "List all available MACE Archival Knowledge Cores (Software Engineering, Psychology, Business, Physics, Security, Philosophy).",
                    inputSchema: {
                        type: "object",
                        properties: {}
                    }
                },
                {
                    name: "load_knowledge_core",
                    description: "Load a specific Archival Knowledge Core by core_id at a desired compression tier (1: Snapshot, 2: Tactical Codex, 3: Full Deep Archive).",
                    inputSchema: {
                        type: "object",
                        properties: {
                            core_id: { type: "string", description: "Target core_id (e.g. core_software_engineering, core_cognitive_psychology, core_business_monetization)" },
                            tier: { type: "integer", description: "Compression tier (1: Executive Snapshot, 2: Tactical Codex, 3: Full Archive)", default: 2 }
                        },
                        required: ["core_id"]
                    }
                },
                {
                    name: "query_knowledge_graph",
                    description: "Search subject-predicate-object triples in the MACE Knowledge Graph.",
                    inputSchema: {
                        type: "object",
                        properties: {
                            query: { type: "string", description: "Subject or topic term to query (e.g. Grand Slam Offer, Samskara, Docker)" }
                        },
                        required: ["query"]
                    }
                }
            ]
        });
    } else if (method === 'tools/call') {
        const name = params ? params.name : '';
        const args = (params && params.arguments) ? params.arguments : {};

        if (name === 'list_knowledge_cores') {
            const regPath = path.join(SCRATCH_DIR, 'knowledge_cores_registry.json');
            if (fs.existsSync(regPath)) {
                const data = JSON.parse(fs.readFileSync(regPath, 'utf8'));
                sendRpcResponse(id, {
                    content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
                });
            } else {
                sendRpcResponse(id, { content: [{ type: "text", text: "No knowledge cores registry found." }] });
            }
        } else if (name === 'load_knowledge_core') {
            const coreId = args.core_id || 'core_software_engineering';
            const tier = args.tier || 2;
            const corePath = path.join(SCRATCH_DIR, `${coreId}_master_archive.json`);
            if (fs.existsSync(corePath)) {
                const data = JSON.parse(fs.readFileSync(corePath, 'utf8'));
                if (tier === 1) {
                    delete data.catalog_summary;
                    delete data.taxonomy_dictionary;
                }
                sendRpcResponse(id, {
                    content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
                });
            } else {
                sendRpcResponse(id, { content: [{ type: "text", text: `Knowledge core '${coreId}' not found.` }] });
            }
        } else if (name === 'query_knowledge_graph') {
            const q = (args.query || '').toLowerCase();
            const graphPath = path.join(SCRATCH_DIR, 'knowledge_graph_triples.json');
            if (fs.existsSync(graphPath)) {
                const data = JSON.parse(fs.readFileSync(graphPath, 'utf8'));
                const matches = data.filter(t => t.subject.toLowerCase().includes(q) || t.object.toLowerCase().includes(q) || t.predicate.toLowerCase().includes(q));
                sendRpcResponse(id, {
                    content: [{ type: "text", text: JSON.stringify(matches.slice(0, 50), null, 2) }]
                });
            } else {
                sendRpcResponse(id, { content: [{ type: "text", text: "Knowledge Graph triples not found." }] });
            }
        } else {
            sendRpcResponse(id, null, { code: -32601, message: `Tool '${name}' not found` });
        }
    } else {
        // Unhandled notification or method
        if (id) {
            sendRpcResponse(id, {});
        }
    }
}
