import http.server
import socketserver
import json
import os
import re
import urllib.parse

PORT = 8080
SCRATCH_DIR = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor'

class KnowledgeAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SCRATCH_DIR, **kwargs)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        tier = query.get('tier', ['2'])[0]

        # Endpoint 1: Multi-Tier Channel Master Codex (/api/v1/codex/<channel>?tier=1|2|3|4)
        if path.startswith('/api/v1/codex/'):
            channel_slug = path.replace('/api/v1/codex/', '').strip().lower()
            json_file = f"{channel_slug}_master_codex.json"
            full_path = os.path.join(SCRATCH_DIR, json_file)

            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    codex = json.load(f)

                if tier == '1': # Tier 1: Executive Snapshot (~500 tokens)
                    res = {
                        "channel_name": codex.get('channel_name'),
                        "tier": "Tier 1: Executive Snapshot",
                        "total_videos_analyzed": codex.get('total_videos_analyzed'),
                        "first_principles": codex.get('first_principles', [])
                    }
                    self.send_json(res)
                elif tier == '3': # Tier 3: Deep Technical Map (~15,000 tokens)
                    self.send_json(codex)
                elif tier == '4': # Tier 4: De-Noised Text Stream
                    res = {
                        "channel_name": codex.get('channel_name'),
                        "tier": "Tier 4: De-Noised Text Stream",
                        "catalog_previews": [v.get('transcript_preview') for v in codex.get('video_knowledge_catalog', [])]
                    }
                    self.send_json(res)
                else: # Tier 2: Default Tactical Codex (~3,000 tokens)
                    res = {
                        "channel_name": codex.get('channel_name'),
                        "tier": "Tier 2: Tactical Codex",
                        "first_principles": codex.get('first_principles', []),
                        "mental_model_dictionary": codex.get('mental_model_dictionary', {}),
                        "tactical_playbooks": codex.get('tactical_playbooks', [])
                    }
                    self.send_json(res)
            else:
                self.send_json({"error": f"Master Codex for '{channel_slug}' not found."}, status=404)
            return

        # Endpoint 2: MACE Archival Knowledge Cores List (/api/v1/cores)
        elif path == '/api/v1/cores':
            full_path = os.path.join(SCRATCH_DIR, 'knowledge_cores_registry.json')
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_json([], status=200)
            return

        # Endpoint 3: Dynamic Core Fusion (/api/v1/cores/fuse?cores=core1,core2)
        elif path == '/api/v1/cores/fuse':
            cores_param = query.get('cores', ['core_software_engineering,core_business_monetization'])[0]
            core_ids = [c.strip().lower() for c in cores_param.split(',') if c.strip()]
            from build_multi_core_fusion import fuse_cores
            fused_data = fuse_cores(core_ids)
            self.send_json(fused_data)
            return

        # Endpoint 4: Task Recommender (/api/v1/cores/recommend?prompt=...)
        elif path == '/api/v1/cores/recommend':
            prompt_str = query.get('prompt', ['How do I launch a SaaS product and configure Docker containers?'])[0]
            from recommend_task_core import recommend_core_for_prompt
            rec = recommend_core_for_prompt(prompt_str)
            self.send_json(rec)
            return

        # Endpoint 5: Specific Archival Core by core_id (/api/v1/cores/<core_id>?tier=1|2|3)
        elif path.startswith('/api/v1/cores/'):
            core_id = path.replace('/api/v1/cores/', '').strip().lower()
            json_file = f"{core_id}_master_archive.json"
            full_path = os.path.join(SCRATCH_DIR, json_file)

            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    core_data = json.load(f)

                if tier == '1':
                    res = {
                        "core_id": core_data.get('core_id'),
                        "title": core_data.get('title'),
                        "description": core_data.get('description'),
                        "total_videos_archived": core_data.get('total_videos_archived'),
                        "first_principles": core_data.get('first_principles', [])
                    }
                    self.send_json(res)
                else:
                    self.send_json(core_data)
            else:
                self.send_json({"error": f"Archival Core '{core_id}' not found."}, status=404)
            return

        # Endpoint 6: Version & Deprecation Audit (/api/v1/audit/versions)
        elif path == '/api/v1/audit/versions':
            audit_path = os.path.join(SCRATCH_DIR, 'version_deprecation_audit.json')
            if os.path.exists(audit_path):
                with open(audit_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                from audit_version_deprecation import audit_version_tags
                self.send_json(audit_version_tags())
            return

        # Endpoint 7: Search Across All Cores & Transcripts (/api/v1/search?q=...)
        elif path == '/api/v1/search':
            q_term = query.get('q', [''])[0].strip().lower()
            if not q_term:
                self.send_json({"error": "Query parameter 'q' required."}, status=400)
                return

            graph_path = os.path.join(SCRATCH_DIR, 'knowledge_graph_triples.json')
            results = []
            if os.path.exists(graph_path):
                with open(graph_path, 'r', encoding='utf-8') as f:
                    triples = json.load(f)
                    results = [t for t in triples if q_term in t.get('subject', '').lower() or q_term in t.get('object', '').lower()][:30]

            self.send_json({
                "query": q_term,
                "matches_count": len(results),
                "matched_triples": results
            })
            return

        # Endpoint 5: Cross-Creator Consensus Matrix (/api/v1/consensus)
        elif path == '/api/v1/consensus':
            full_path = os.path.join(SCRATCH_DIR, 'cross_creator_consensus.json')
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_json({"error": "Consensus matrix not found."}, status=404)
            return

        # Endpoint 3: Knowledge Graph Triples (/api/v1/graph)
        elif path == '/api/v1/graph':
            full_path = os.path.join(SCRATCH_DIR, 'knowledge_graph_triples.json')
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_json({"error": "Knowledge Graph triples not found."}, status=404)
            return

        # Endpoint 4: AI Personas (/api/v1/personas)
        elif path == '/api/v1/personas':
            full_path = os.path.join(SCRATCH_DIR, 'creator_personas.json')
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_json({"error": "Creator Personas not found."}, status=404)
            return

        # Endpoint 5: All Channels Catalog (/api/v1/channels)
        elif path == '/api/v1/channels':
            db_path = os.path.join(SCRATCH_DIR, 'universal_channel_intelligence_db.json')
            if os.path.exists(db_path):
                with open(db_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_json([], status=200)
            return

        # Fallback to static file serving
        super().do_GET()

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), KnowledgeAPIHandler) as httpd:
        print(f"🚀 Universal Multi-Tier Knowledge REST API active on http://localhost:{PORT}")
        httpd.serve_forever()
