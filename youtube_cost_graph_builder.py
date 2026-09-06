import json, os

def build_dashboard():
    dataset_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/channel_structures_dataset.json'
    queue_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/sequential_video_queue.json'
    hydrated_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/hydrated_viewer_dataset.json'
    granularity_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/text_granularity_analytics_dataset.json'
    ling_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/video_linguistic_analytics_dataset.json'
    ch_db_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/channel_aggregate_database.json'
    global_topic_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/global_topic_taxonomy.json'
    
    with open(dataset_path, 'r') as f: channels = json.load(f)
    with open(queue_path, 'r') as f: video_queue = json.load(f)
    with open(hydrated_path, 'r') as f: hydrated_videos = json.load(f)
    with open(granularity_path, 'r') as f: granularity_data = json.load(f)
    with open(ling_path, 'r') as f: linguistic_data = json.load(f)
    with open(ch_db_path, 'r') as f: channel_db = json.load(f)
    with open(global_topic_path, 'r') as f: global_topic_db = json.load(f)

    out_path = '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/youtube_channel_overview_dashboard.html'

    subscribed = [c for c in channels if c['category'] == 'Subscribed']
    tangential = [c for c in channels if c['category'] == 'Tangential']

    total_channels = len(channels)
    total_subscribed = len(subscribed)
    total_tangential = len(tangential)

    total_videos = len(video_queue)
    total_hours = sum(c['total_hours'] for c in channels)
    total_cost = sum(c['transcript_cost_usd'] for c in channels)
    avg_hours_per_channel = round(total_hours / total_channels, 1) if total_channels > 0 else 0

    free_tier_credits_usd = 9.40
    free_videos_covered = sum(1 for v in video_queue if v.get('is_free_covered', False))

    # Catalog Hydration completeness calculation
    hydrated_count = len(hydrated_videos)
    catalog_completeness_pct = round((hydrated_count / float(max(1, total_videos))) * 100.0, 1)

    top_channels_for_graph = ['LaurieWired', 'Alex Hormozi', 'freeCodeCamp.org', 'Linus Tech Tips', 'Yellow Cherry Jam', 'The PrimeTime', 'Angela Collier', 'COULOU']
    
    graph_data = {}
    for c in channels:
        if c['name'] in top_channels_for_graph or c['handle'] in top_channels_for_graph:
            vcount = c['video_count']
            step = max(1, vcount // 20)
            points = []
            for n in range(0, vcount + 1, step):
                cost = round(n * 0.002, 3)
                hours = round((n * c['avg_duration_min']) / 60.0, 1)
                points.append({'video_num': n, 'cost': cost, 'hours': hours})
            graph_data[c['name']] = points

    queue_sample = video_queue[:300]

    g_total_chars = sum(g['chars'] for g in granularity_data)
    g_total_words = sum(g['words'] for g in granularity_data)
    g_total_clauses = sum(g.get('clauses', g.get('sentences', 0)) for g in granularity_data)
    g_avg_wpm = round(sum(g['wpm'] for g in granularity_data) / max(1, len(granularity_data)), 1)
    g_avg_cps = round(sum(g['cps'] for g in granularity_data) / max(1, len(granularity_data)), 1)

    channels_json_str = json.dumps(channels)
    graph_json_str = json.dumps(graph_data)
    queue_json_str = json.dumps(queue_sample)
    hydrated_json_str = json.dumps(hydrated_videos)
    granularity_json_str = json.dumps(granularity_data)
    linguistic_json_str = json.dumps(linguistic_data)
    channel_db_json_str = json.dumps(channel_db)
    global_topic_db_json_str = json.dumps(global_topic_db)
    universal_studio_db_path = "/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/universal_channel_intelligence_db.json"
    universal_studio_db = {}
    if os.path.exists(universal_studio_db_path):
        with open(universal_studio_db_path, 'r', encoding='utf-8') as f:
            universal_studio_db = json.load(f)
    universal_studio_db_json_str = json.dumps(universal_studio_db)

    try:
        import hydrate_single_video
        bal_info = hydrate_single_video.check_apify_balance()
        apify_spend_usd = bal_info["spend"]
        apify_cap_usd = bal_info["account_limit"]
        apify_remaining_usd = bal_info["remaining"]
    except Exception:
        apify_spend_usd = 5.0594
        apify_cap_usd = 5.00
        apify_remaining_usd = 0.00

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Channel Structure &amp; Scraping Cost-Graph Dashboard</title>
    <script src="chart.umd.js"></script>
    <script>if (typeof Chart === 'undefined') {{ document.write('<script src="https://cdn.jsdelivr.net/npm/chart.js"><\\/script>'); }}</script>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-purple: #c084fc;
            --accent-green: #4ade80;
            --accent-amber: #fbbf24;
            --accent-rose: #fb7185;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 24px;
        }}
        .header {{
            margin-bottom: 16px;
        }}
        .header h1 {{
            font-size: 28px;
            margin: 0 0 8px 0;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header p {{
            color: var(--text-muted);
            margin: 0;
            font-size: 15px;
        }}

        /* Multi-Stage Generation Progress Bar Monitor Header */
        .pipeline-progress-card {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1.5px solid var(--accent-blue);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(56, 189, 248, 0.1);
        }}
        .progress-title-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .progress-title-bar h3 {{
            margin: 0;
            font-size: 15px;
            color: var(--accent-blue);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .progress-track {{
            width: 100%;
            height: 10px;
            background-color: #334155;
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 10px;
        }}
        .progress-fill {{
            height: 100%;
            width: {catalog_completeness_pct}%;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
            border-radius: 5px;
            transition: width 0.4s ease;
        }}
        .progress-stages-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 10px;
            font-size: 12px;
        }}
        .stage-pill {{
            background-color: #0f172a;
            border: 1px solid var(--card-border);
            padding: 6px 10px;
            border-radius: 6px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .stage-pill.ready {{
            border-color: var(--accent-green);
            color: var(--accent-green);
        }}

        /* Main Tabs */
        .tab-bar {{
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            border-bottom: 2px solid var(--card-border);
            padding-bottom: 8px;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 15px;
            font-weight: 600;
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{
            color: var(--text-main);
            background-color: rgba(255,255,255,0.05);
        }}
        .tab-btn.active {{
            color: var(--accent-blue);
            background-color: rgba(56, 189, 248, 0.12);
            border-bottom: 2px solid var(--accent-blue);
        }}
        .tab-pane {{
            display: none;
        }}
        .tab-pane.active {{
            display: block;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }}
        .stat-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .stat-label {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .stat-value {{
            font-size: 22px;
            font-weight: 700;
            color: var(--text-main);
        }}
        .stat-sub {{
            font-size: 11px;
            color: var(--accent-green);
            margin-top: 2px;
        }}
        
        .timeline-card {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1.5px solid var(--accent-blue);
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 28px;
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.1);
        }}
        .timeline-title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .timeline-title h2 {{
            margin: 0;
            font-size: 20px;
            color: var(--accent-blue);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .budget-tool-card {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1.5px solid var(--accent-green);
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 28px;
            box-shadow: 0 6px 20px rgba(74, 222, 128, 0.1);
        }}
        .budget-tool-title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .budget-tool-title h2 {{
            margin: 0;
            font-size: 20px;
            color: var(--accent-green);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .budget-slider-container {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .budget-slider {{
            flex: 1;
            min-width: 260px;
            height: 10px;
            border-radius: 5px;
            background: #334155;
            outline: none;
            accent-color: var(--accent-green);
        }}
        .budget-input-wrapper {{
            display: flex;
            align-items: center;
            gap: 6px;
            background-color: #0f172a;
            border: 1px solid var(--accent-green);
            padding: 6px 14px;
            border-radius: 8px;
        }}
        .budget-input-wrapper span {{
            color: var(--accent-green);
            font-weight: 700;
            font-size: 18px;
        }}
        .budget-number-input {{
            background: transparent;
            border: none;
            color: var(--text-main);
            font-size: 20px;
            font-weight: 700;
            width: 70px;
            outline: none;
        }}
        .budget-results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            background-color: rgba(15, 23, 42, 0.6);
            padding: 16px;
            border-radius: 10px;
            border: 1px solid var(--card-border);
        }}
        .budget-res-item {{
            display: flex;
            flex-direction: column;
        }}
        .budget-res-label {{
            font-size: 12px;
            color: var(--text-muted);
        }}
        .budget-res-val {{
            font-size: 20px;
            font-weight: 700;
            color: var(--accent-green);
            margin-top: 2px;
        }}

        .chart-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }}
        .chart-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .chart-card h3 {{
            margin: 0 0 12px 0;
            font-size: 15px;
            color: var(--text-main);
        }}

        /* Channel Deep-Dive Layout */
        .channel-db-container {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 20px;
            min-height: 650px;
        }}
        .channel-db-sidebar {{
            background-color: var(--card-bg);
            border: 1.5px solid var(--card-border);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
        }}
        .channel-search-box {{
            margin-bottom: 12px;
        }}
        .channel-db-list {{
            flex: 1;
            overflow-y: auto;
            max-height: 580px;
        }}
        .channel-db-item {{
            padding: 10px 12px;
            border-radius: 8px;
            margin-bottom: 6px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.15s;
        }}
        .channel-db-item:hover {{
            background-color: rgba(255,255,255,0.04);
        }}
        .channel-db-item.active {{
            background-color: rgba(56, 189, 248, 0.12);
            border-color: var(--accent-blue);
        }}
        .channel-db-item-title {{
            font-size: 13px;
            font-weight: 700;
            color: var(--text-main);
        }}
        .channel-db-item-meta {{
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            margin-top: 2px;
        }}

        /* Drill-down Breadcrumb Button for Channel Topic Pie Chart */
        .ch-back-btn {{
            display: none;
            align-items: center;
            gap: 6px;
            background-color: #0f172a;
            border: 1px solid var(--accent-blue);
            color: var(--accent-blue);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            margin-bottom: 8px;
            transition: all 0.15s;
        }}
        .ch-back-btn:hover {{
            background-color: var(--accent-blue);
            color: #0f172a;
        }}

        /* Full-Width Hierarchical Narrative Terrain Panel */
        .terrain-panel {{
            background-color: var(--card-bg);
            border: 1.5px solid var(--accent-amber);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
            width: 100%;
            box-sizing: border-box;
            box-shadow: 0 4px 16px rgba(251, 191, 36, 0.1);
        }}
        .terrain-title-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .terrain-panel h3 {{
            margin: 0;
            font-size: 16px;
            color: var(--accent-amber);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Full-Width Calligrapher's Pen Topic Density Span Panel */
        .topic-span-panel {{
            background-color: var(--card-bg);
            border: 1.5px solid var(--accent-blue);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
            width: 100%;
            box-sizing: border-box;
            box-shadow: 0 4px 16px rgba(56, 189, 248, 0.1);
        }}
        .topic-span-title-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .topic-span-panel h3 {{
            margin: 0;
            font-size: 16px;
            color: var(--accent-blue);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Topic Pools Bar */
        .topic-pools-panel {{
            background-color: #0f172a;
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .topic-pill {{
            background-color: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: var(--accent-blue);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .topic-pill:hover {{
            background-color: rgba(56, 189, 248, 0.25);
        }}
        .topic-pill.active {{
            background-color: var(--accent-blue);
            color: #0f172a;
            border-color: var(--accent-blue);
        }}

        .table-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .controls {{
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .search-input, .select-input {{
            background-color: #0f172a;
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
        }}
        .search-input {{
            flex: 1;
            min-width: 200px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            text-align: left;
        }}
        th, td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--card-border);
        }}
        th {{
            background-color: #0f172a;
            color: var(--text-muted);
            font-weight: 600;
            cursor: pointer;
        }}
        th:hover {{
            color: var(--accent-blue);
        }}
        tr:hover {{
            background-color: rgba(255,255,255,0.02);
        }}
        tr.selected-row {{
            background-color: rgba(74, 222, 128, 0.08);
            border-left: 3px solid var(--accent-green);
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .badge-sub {{ background-color: rgba(56, 189, 248, 0.2); color: var(--accent-blue); }}
        .badge-tangential {{ background-color: rgba(192, 132, 252, 0.2); color: var(--accent-purple); }}
        .badge-selected {{ background-color: rgba(74, 222, 128, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .badge-free {{ background-color: rgba(251, 191, 36, 0.2); color: var(--accent-amber); }}
        .badge-topic {{ background-color: rgba(192, 132, 252, 0.2); color: var(--accent-purple); border: 1px solid rgba(192, 132, 252, 0.4); margin-right: 6px; font-size: 10px; }}

        /* Hydrated Transcripts Viewer Layout */
        .viewer-container {{
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
            height: calc(100vh - 180px);
            min-height: 700px;
        }}
        .viewer-sidebar {{
            background-color: var(--card-bg);
            border: 1.5px solid var(--card-border);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .sort-controls {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--card-border);
        }}
        .sort-label {{
            font-size: 11px;
            font-weight: 700;
            color: var(--accent-blue);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .viewer-list {{
            flex: 1;
            overflow-y: auto;
        }}
        .viewer-item {{
            padding: 10px 12px;
            border-radius: 8px;
            margin-bottom: 6px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.15s;
        }}
        .viewer-item:hover {{
            background-color: rgba(255,255,255,0.04);
        }}
        .viewer-item.active {{
            background-color: rgba(56, 189, 248, 0.12);
            border-color: var(--accent-blue);
        }}
        .viewer-item-title {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 4px;
            line-height: 1.3;
        }}
        .viewer-item-meta {{
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
        }}
        .viewer-content {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }}
        .viewer-header {{
            margin-bottom: 14px;
            padding-bottom: 14px;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .viewer-header-info h2 {{
            margin: 0 0 4px 0;
            font-size: 19px;
            color: var(--text-main);
        }}
        .viewer-header-info p {{
            margin: 0;
            font-size: 13px;
            color: var(--text-muted);
        }}

        /* Focused Layer Switcher Bar */
        .layer-bar {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
            flex-wrap: wrap;
        }}
        .layer-btn {{
            background-color: #0f172a;
            border: 1px solid var(--card-border);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .layer-btn.active {{
            background-color: rgba(56, 189, 248, 0.15);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}

        .copy-btn {{
            background-color: rgba(74, 222, 128, 0.15);
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .copy-btn:hover {{
            background-color: var(--accent-green);
            color: #0f172a;
        }}
        .transcript-md-box {{
            flex: 1;
            min-height: 320px;
            background-color: #0f172a;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 18px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.65;
            color: #e2e8f0;
            overflow-y: auto;
            white-space: pre-wrap;
        }}
        .subtab-btn {{
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.25);
            color: #94a3b8;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .subtab-btn:hover {{
            color: #f8fafc;
            border-color: var(--accent-blue);
        }}
        .subtab-btn.active {{
            background: var(--accent-blue);
            color: #0f172a;
            border-color: var(--accent-blue);
            font-weight: 700;
        }}
        .dashboard-drawer summary::-webkit-details-marker {{
            display: none;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>YouTube Video-by-Video Download Timeline &amp; Cost Dashboard</h1>
        <p>Sequential video priority queue across <strong>{total_subscribed} Subscribed Channels</strong> &amp; <strong>{total_tangential} Tangential Channels</strong>. Videos are downloaded video-by-video based on maximum Bang-for-Buck ROI.</p>
    </div>

    <!-- Multi-Stage Progressive Data Generation & Progress Bar Header -->
    <div class="pipeline-progress-card">
        <div class="progress-title-bar">
            <h3>📊 Catalog Hydration &amp; Overarching Data Pipeline Progress</h3>
            <span style="font-size:13px; font-weight:700; color:var(--accent-green);">{hydrated_count} / {total_videos:,} Videos Hydrated ({catalog_completeness_pct}%)</span>
        </div>
        <div class="progress-track">
            <div class="progress-fill"></div>
        </div>
        <div class="progress-stages-grid">
            <div class="stage-pill ready">✓ Stage 1: Channel Cataloging (100%)</div>
            <div class="stage-pill ready">✓ Stage 2: Video Hydration ({catalog_completeness_pct}%)</div>
            <div class="stage-pill ready">✓ Stage 3: Channel Aggregates ({len(channel_db)} Channels Ready)</div>
            <div class="stage-pill ready">✓ Stage 4: Global Topic Taxonomy ({len(global_topic_db)} Topics Ready)</div>
        </div>
    </div>

    <!-- Main Navigation Tabs (Separated into Dedicated Pages) -->
    <div class="tab-bar">
        <button class="tab-btn active" onclick="switchTab('overviewTab', this)">📊 Overview &amp; Budget Allocator</button>
        <button class="tab-btn" onclick="switchTab('analyticsTab', this)">📈 Visual Analytics &amp; Topic Charts</button>
        <button class="tab-btn" onclick="switchTab('catalogTab', this)">📺 Channels Master Catalog &amp; Queue ({total_channels})</button>
        <button class="tab-btn" onclick="switchTab('viewerTab', this)">📜 Video-by-Video Analyzer &amp; Transcripts ({len(hydrated_videos)} Ready)</button>
        <button class="tab-btn" onclick="switchTab('channelDbTab', this)">🏛️ Creator Intelligence Studio ({len(channel_db)} Creators)</button>
        <button class="tab-btn" onclick="switchTab('globalTopicTab', this)">🌐 Global Topic Taxonomy</button>
        <button class="tab-btn" onclick="switchTab('granularityTab', this)">📈 Granularity Analytics</button>
    </div>

    <!-- PAGE 1: Overview & Budget Allocator -->
    <div id="overviewTab" class="tab-pane active">
        <!-- Top KPI Summary Grid -->
        <div class="stats-grid" style="margin-bottom: 20px;">
            <div class="stat-card">
                <div class="stat-label">Total Channels</div>
                <div class="stat-value">{total_channels}</div>
                <div class="stat-sub">{total_subscribed} Subscribed / {total_tangential} Tangential</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Videos Monitored</div>
                <div class="stat-value">{total_videos:,}</div>
                <div class="stat-sub">Across all catalog histories</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Content Hours</div>
                <div class="stat-value">{total_hours:,.0f} hrs</div>
                <div class="stat-sub">Average ~{avg_hours_per_channel} hrs / channel</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Gross Scraping Cost</div>
                <div class="stat-value">${total_cost:,.2f}</div>
                <div class="stat-sub">Net Out-of-Pocket: ${max(0.0, total_cost - free_tier_credits_usd):,.2f}</div>
            </div>
        </div>

        <!-- Budget Slider & ROI Calculator Card -->
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; margin-bottom: 20px; padding: 18px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #f8fafc;">⚙️ Name-Your-Price Scraping Allocator &amp; Free Tier Offset</h3>
            <p style="color: var(--text-muted); font-size: 13px; margin: 0 0 14px 0;">Optimizes channel selection using Cost-to-Benefit ratio (Hours / $).</p>
            <div class="budget-slider-container">
                <input type="range" id="budgetSlider" class="budget-slider" min="1" max="{int(total_cost + 1)}" value="20" step="1">
                <div class="budget-input-wrapper">
                    <span>$</span>
                    <input type="number" id="budgetInput" class="budget-number-input" value="20" min="1" max="{int(total_cost + 1)}">
                </div>
            </div>

            <div class="budget-results-grid">
                <div class="budget-res-item">
                    <div class="budget-res-label">Gross Budget Target</div>
                    <div class="budget-res-val" id="resGrossBudget">$20.00</div>
                </div>
                <div class="budget-res-item">
                    <div class="budget-res-label">Free Tier Applied</div>
                    <div class="budget-res-val" id="resFreeApplied" style="color: var(--accent-amber);">$9.40 ($0 out-of-pocket)</div>
                </div>
                <div class="budget-res-item">
                    <div class="budget-res-label">Net Out-of-Pocket Cost</div>
                    <div class="budget-res-val" id="resNetCost" style="color: var(--accent-rose);">$10.60</div>
                </div>
                <div class="budget-res-item">
                    <div class="budget-res-label">Channels Selected</div>
                    <div class="budget-res-val" id="resChannels">0 / {total_channels}</div>
                </div>
                <div class="budget-res-item">
                    <div class="budget-res-label">Content Hours Unlocked</div>
                    <div class="budget-res-val" id="resHours">0.0 hrs</div>
                </div>
                <div class="budget-res-item">
                    <div class="budget-res-label">Net ROI Ratio</div>
                    <div class="budget-res-val" id="resRatio" style="color: var(--accent-blue);">0.0 hrs/$</div>
                </div>
            </div>
        </div>

        <!-- On-Demand Video Hydration & Credit Tracker -->
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 18px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #f8fafc;">➕ On-Demand Video Hydration &amp; Credit Balance Tracker</h3>
            <div style="display: grid; grid-template-columns: 1fr 340px; gap: 20px; align-items: start; margin-top: 10px;">
                <div>
                    <p style="font-size: 13px; color: var(--text-muted); margin: 0 0 10px 0;">Paste any YouTube Video URL or Video ID below to immediately extract its spoken transcript, executive synopsis, 4 core takeaways, and timestamped chapters into your live catalog.</p>
                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="manualUrlInput" class="search-input" style="flex: 1; padding: 10px 14px; font-size: 13.5px;" placeholder="Paste YouTube link (e.g. https://www.youtube.com/watch?v=... or Video ID)">
                        <button class="subtab-btn active" style="background: var(--accent-green); color: #022c22; font-weight: 700; padding: 10px 18px; border: none; border-radius: 6px; cursor: pointer;" onclick="alert('To hydrate video on-demand, run terminal command:\npython3 hydrate_single_video.py ' + (document.getElementById('manualUrlInput').value || '<URL>'))">⚡ Hydrate Video</button>
                    </div>
                </div>

                <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px 16px;">
                    <div style="font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 8px; display: flex; justify-content: space-between;">
                        <span>💳 Apify Account Balance</span>
                        <span style="color: var(--accent-green); font-size: 11px;">Cap: ${apify_cap_usd:.2f} USD</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                        <span style="color: var(--text-muted);">Current Account Spend:</span>
                        <span style="font-weight: 700; color: var(--accent-amber);">${apify_spend_usd:.4f} USD</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 8px;">
                        <span style="color: var(--text-muted);">Remaining Buffer:</span>
                        <span style="font-weight: 700; color: var(--accent-green);">${apify_remaining_usd:.4f} USD</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- PAGE 2: Visual Analytics & Topic Charts -->
    <div id="analyticsTab" class="tab-pane">
        <div class="subtab-panel" style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 18px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">
                <h3 style="margin: 0; font-size: 15px; color: #f8fafc;">📈 Visual Analytics &amp; Topic Taxonomy</h3>
                <div style="display: flex; gap: 8px;">
                    <button class="subtab-btn active" onclick="switchOverviewSubTab('graphViewPane', this)">📉 Cost Curves &amp; ROI Scatter</button>
                    <button class="subtab-btn" onclick="switchOverviewSubTab('topicViewPane', this)">🍩 2-Level Channel Topics Chart</button>
                </div>
            </div>

            <!-- Sub-Pane 2A: Cost Curves Line Chart -->
            <div id="graphViewPane" class="subtab-pane">
                <div class="chart-section" style="grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div class="chart-card">
                        <h3>Sequential Cost-Graph (Cumulative Cost vs. Video Uploads)</h3>
                        <canvas id="costGraphChart" height="240"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Content Density ROI (Highlighted by Budget Selection)</h3>
                        <canvas id="roiScatterChart" height="240"></canvas>
                    </div>
                </div>
            </div>

            <!-- Sub-Pane 2B: 2-Level Doughnut Topic Chart -->
            <div id="topicViewPane" class="subtab-pane" style="display: none;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: center;">
                    <div style="height: 320px; position: relative;">
                        <canvas id="channelTopicChart"></canvas>
                    </div>
                    <div>
                        <button id="chBackBtn" onclick="resetChannelTopicChart()" style="display:none; margin-bottom: 12px; background: rgba(56, 189, 248, 0.2); border: 1px solid var(--accent-blue); color: var(--accent-blue); padding: 6px 14px; border-radius: 6px; font-weight: 700; cursor: pointer;">⬅️ Back to Macro Categories</button>
                        <h4 style="margin: 0 0 8px 0; color: #f8fafc;">💡 Interactive 2-Level Topic Drill-Down</h4>
                        <p style="color: var(--text-muted); font-size: 13px; line-height: 1.5; margin: 0 0 12px 0;">
                            Click any category slice in the doughnut chart to expand it into granular sub-topic distributions across all creator channels.
                        </p>
                        <div id="topicDrillInfo" style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px; font-size: 12.5px; color: #cbd5e1;">
                            Showing <strong>Level 1 Macro Categories</strong>. Click a slice to drill down into Level 2 sub-topics.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- PAGE 3: Channels Master Catalog & Queue -->
    <div id="catalogTab" class="tab-pane">
        <div class="subtab-panel" style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 18px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">
                <h3 style="margin: 0; font-size: 15px; color: #f8fafc;">📺 Channels Master Catalog &amp; Priority Queue</h3>
                <div style="display: flex; gap: 8px;">
                    <button class="subtab-btn active" onclick="switchOverviewSubTab('channelsTablePane', this)">📺 Channels Master Database ({total_channels})</button>
                    <button class="subtab-btn" onclick="switchOverviewSubTab('queueTablePane', this)">📋 Priority Queue ({total_videos:,} Steps)</button>
                </div>
            </div>

            <!-- Sub-Pane 3A: Channels Master Database Table -->
            <div id="channelsTablePane" class="subtab-pane">
                <div class="controls" style="margin-bottom: 12px;">
                    <input type="text" id="searchInput" class="search-input" placeholder="Search channel name or handle...">
                    <select id="categoryFilter" class="select-input">
                        <option value="ALL">All Categories ({total_channels})</option>
                        <option value="SELECTED_ONLY">Selected by Budget Tool</option>
                        <option value="FREE_COVERED">Covered 100% Free</option>
                        <option value="Subscribed">Subscribed ({total_subscribed})</option>
                        <option value="Tangential">Tangential ({total_tangential})</option>
                    </select>
                </div>
                <div style="max-height: 480px; overflow-y: auto; background-color: #0f172a; border-radius: 8px; border: 1px solid var(--card-border);">
                    <table id="channelsTable">
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)">Category</th>
                                <th onclick="sortTable(1)">Channel Name</th>
                                <th onclick="sortTable(2)">Handle</th>
                                <th onclick="sortTable(3)">Video Count</th>
                                <th onclick="sortTable(4)">Playlists</th>
                                <th onclick="sortTable(5)">Avg Length</th>
                                <th onclick="sortTable(6)">Total Hours</th>
                                <th onclick="sortTable(7)">Est. Cost ($)</th>
                                <th onclick="sortTable(8)">ROI Score</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody">
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Sub-Pane 3B: Priority Queue Table -->
            <div id="queueTablePane" class="subtab-pane" style="display: none;">
                <div style="margin-bottom: 10px;">
                    <p style="color: var(--text-muted); font-size: 13px; margin: 0;">
                        Ranked by 8x Software Engineering + 4:1 Subscribed priority weighting. First <strong>{free_videos_covered:,} videos ($0 out-of-pocket)</strong> covered 100% Free.
                    </p>
                </div>
                <div style="max-height: 480px; overflow-y: auto; background-color: #0f172a; border-radius: 8px; border: 1px solid var(--card-border);">
                    <table>
                        <thead>
                            <tr>
                                <th>Step #</th>
                                <th>Video Item &amp; Title</th>
                                <th>Channel</th>
                                <th>Duration</th>
                                <th>Cum. Hours</th>
                                <th>Incremental / Cum. Cost</th>
                                <th>Tier Status</th>
                            </tr>
                        </thead>
                        <tbody id="queueTableBody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- PAGE 4: Video-by-Video Analyzer & Transcripts Workspace -->
    <div id="viewerTab" class="tab-pane">
        <div class="viewer-container">
            <div class="viewer-sidebar">
                <div class="sort-controls">
                    <span class="sort-label">Sort Transcripts By</span>
                    <select id="vSortSelect" class="select-input" onchange="sortViewerList(this.value)">
                        <option value="title_asc">Title (A &rarr; Z)</option>
                        <option value="title_desc">Title (Z &rarr; A)</option>
                        <option value="channel_asc">Channel Name (A &rarr; Z)</option>
                        <option value="channel_desc">Channel Name (Z &rarr; A)</option>
                        <option value="dur_desc">Duration (Longest &rarr; Shortest)</option>
                        <option value="dur_asc">Duration (Shortest &rarr; Longest)</option>
                    </select>
                </div>
                <div class="viewer-list" id="viewerList">
                </div>
            </div>
            <div class="viewer-content">
                <div class="viewer-header">
                    <div class="viewer-header-info">
                        <h2 id="vTitle">Select a video from the list</h2>
                        <p id="vMeta">Choose any hydrated transcript on the left to view formatted MM:SS timestamps.</p>
                    </div>
                    <button class="copy-btn" id="copyBtn" onclick="copyMarkdown()">📋 Copy View Text</button>
                </div>

                <!-- Executive Video Summary & Key Takeaways Card Panel -->
                <div id="vSummaryPanel"></div>

                <!-- Video-by-Video Stats Cards Embedded -->
                <div class="stats-grid" id="nlpStatsGrid">
                </div>

                <!-- Narrative Terrain Contour Map -->
                <div class="terrain-panel">
                    <div class="terrain-title-bar">
                        <h3>⛰️ Hierarchical Narrative Terrain Map (Topographical Contour Stack)</h3>
                    </div>
                    <div style="height: 160px; position: relative;">
                        <canvas id="terrainCanvas" style="width: 100%; height: 100%; display: block; border-radius: 8px; background: #0f172a;"></canvas>
                    </div>
                </div>

                <!-- UNIFIED TOPIC SIMILARITY & ORGANIC SHIFTS PANEL WITH SEGMENT TOGGLE -->
                <div class="topic-span-panel" style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 16px; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">
                        <h3 style="margin: 0; font-size: 15px; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                            <span>🎯 Topic Similarity &amp; Organic Shift Analyzer</span>
                        </h3>
                        <div style="display: flex; gap: 6px; background: #0f172a; padding: 4px; border-radius: 8px; border: 1px solid var(--card-border);">
                            <button class="subtab-btn active" id="btnHighSim" onclick="switchSimilarityView('high', this)">🎯 High Topic Similarity (Ribbons)</button>
                            <button class="subtab-btn" id="btnLowSim" onclick="switchSimilarityView('low', this)">⚡ Low Topic Similarity (Topic Shifts &amp; Breakpoints)</button>
                        </div>
                    </div>

                    <!-- High Similarity View (Calligrapher Ribbons Scatter & Topic Pools) -->
                    <div id="highSimViewPane">
                        <div style="height: 180px; position: relative; margin-bottom: 12px;">
                            <canvas id="topicSpanScatterChart"></canvas>
                        </div>
                        <div class="topic-pools-panel" id="topicPoolsBar" style="margin-bottom:0;"></div>
                    </div>

                    <!-- Low Similarity / Organic Topic Shift Breakpoints View -->
                    <div id="lowSimViewPane" style="display: none;">
                        <div id="organicSectionsBox" style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 14px;">
                            <h4 style="margin: 0 0 10px 0; font-size: 14px; color: var(--accent-amber);">⚡ Organic Topic Shift Break Points &amp; Dominant Transitions</h4>
                            <div id="organicSectionsContent" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px;"></div>
                        </div>
                    </div>
                </div>

                <!-- Timeline Heatmap Chart -->
                <div class="malleable-heatmap-panel">
                    <div class="malleable-title-bar">
                        <h3>🔥 Malleable Video Timeline Heatmap &amp; 1-Second Sub-Bucket Engine</h3>
                        <div class="malleable-controls-bar">
                            <span style="font-size:11px; color:var(--text-muted); font-weight:700;">METRICS:</span>
                            <button class="toggle-btn active" id="togWPM" onclick="toggleHeatmapMetric('wpm')">⚡ WPM Velocity</button>
                            <button class="toggle-btn active" id="togSubstance" onclick="toggleHeatmapMetric('substance')">🎯 Substance %</button>
                            <button class="toggle-btn active" id="togWordLen" onclick="toggleHeatmapMetric('wordLen')">🔤 Word Size</button>
                            <button class="toggle-btn active" id="togNounsVerbs" onclick="toggleHeatmapMetric('nounsVerbs')">📖 Nouns &amp; Verbs</button>
                            
                            <div class="window-slider-container">
                                <span style="font-size:11px; color:var(--accent-purple); font-weight:700;">WINDOW:</span>
                                <input type="range" id="windowGradientSlider" class="window-gradient-slider" min="1" max="120" value="30" step="1" oninput="updateGradientSliderValue(this.value)">
                                <span style="font-size:12px; color:var(--text-main); font-weight:700; width:38px;" id="winSliderVal">30s</span>
                            </div>
                        </div>
                    </div>
                    <div style="height: 180px; position: relative;">
                        <canvas id="timelineHeatmapChart"></canvas>
                    </div>
                </div>

                <!-- Video-by-Video NLP & Topic Pools Graphs Embedded -->
                <div class="chart-section" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                    <div class="chart-card">
                        <h3>Semantic Topic Pools Composition</h3>
                        <canvas id="topicDoughnutChart" height="180"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Part-of-Speech (POS) Breakdown</h3>
                        <canvas id="posBarChart" height="180"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Substance vs. Filler Ratio</h3>
                        <canvas id="substanceDoughnutChart" height="180"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Word Size Distribution</h3>
                        <canvas id="wordLengthChart" height="180"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Net Speech Speed vs Gross WPM</h3>
                        <canvas id="wpmBoostChart" height="180"></canvas>
                    </div>
                </div>

                <!-- Dedicated 3-View Switcher Bar -->
                <div class="layer-bar">
                    <span style="font-size:13px; color:var(--text-muted); font-weight:600;">Transcript View:</span>
                    <button class="layer-btn active" id="layerBtn1" onclick="switchLayer(1)">⏱️ Timestamped Raw Captions</button>
                    <button class="layer-btn" id="layerBtn05" onclick="switchLayer(0.5)">🎯 Punctuation Clauses (. ! ? / Pauses)</button>
                    <button class="layer-btn" id="layerBtn2" onclick="switchLayer(2)">🏷️ Topic Tagged Clauses</button>
                </div>

                <div class="transcript-md-box" id="vTranscriptBox">Select a transcript to inspect...</div>
            </div>
        </div>
    </div>
                        <option value="title_asc">Title (A &rarr; Z)</option>
                        <option value="title_desc">Title (Z &rarr; A)</option>
                        <option value="channel_asc">Channel Name (A &rarr; Z)</option>
                        <option value="channel_desc">Channel Name (Z &rarr; A)</option>
                        <option value="dur_desc">Duration (Longest &rarr; Shortest)</option>
                        <option value="dur_asc">Duration (Shortest &rarr; Longest)</option>
                    </select>
                </div>
                <div class="viewer-list" id="viewerList">
                </div>
            </div>
            <div class="viewer-content">
                <div class="viewer-header">
                    <div class="viewer-header-info">
                        <h2 id="vTitle">Select a video from the list</h2>
                        <p id="vMeta">Choose any hydrated transcript on the left to view formatted MM:SS timestamps.</p>
                    </div>
                    <button class="copy-btn" id="copyBtn" onclick="copyMarkdown()">📋 Copy View Text</button>
                </div>

                <!-- Executive Video Summary & Key Takeaways Card Panel -->
                <div id="vSummaryPanel"></div>

                <!-- Video-by-Video Stats Cards Embedded -->
                <div class="stats-grid" id="nlpStatsGrid">
                </div>

                <!-- Full-Width Hierarchical Narrative Terrain Canvas Box (Topographical Layered Plateau Map) -->
                <div class="terrain-panel">
                    <div class="terrain-title-bar">
                        <h3>⛰️ Hierarchical Narrative Terrain Map (Topographical Contour Stack &amp; Elevation Ridges)</h3>
                    </div>
                    <div style="height: 160px; position: relative;">
                        <canvas id="terrainCanvas" style="width: 100%; height: 100%; display: block; border-radius: 8px; background: #0f172a;"></canvas>
                    </div>
                </div>

                <!-- Full-Width Malleable Timeline Heatmap Chart with Continuous Gradient Range Slider -->
                <div class="malleable-heatmap-panel">
                    <div class="malleable-title-bar">
                        <h3>🔥 Malleable Video Timeline Heatmap &amp; 1-Second Sub-Bucket Engine</h3>
                        <div class="malleable-controls-bar">
                            <span style="font-size:11px; color:var(--text-muted); font-weight:700;">METRICS:</span>
                            <button class="toggle-btn active" id="togWPM" onclick="toggleHeatmapMetric('wpm')">⚡ WPM Velocity</button>
                            <button class="toggle-btn active" id="togSubstance" onclick="toggleHeatmapMetric('substance')">🎯 Substance %</button>
                            <button class="toggle-btn active" id="togWordLen" onclick="toggleHeatmapMetric('wordLen')">🔤 Word Size</button>
                            <button class="toggle-btn active" id="togNounsVerbs" onclick="toggleHeatmapMetric('nounsVerbs')">📖 Nouns &amp; Verbs</button>
                            
                            <div class="window-slider-container">
                                <span style="font-size:11px; color:var(--accent-purple); font-weight:700;">WINDOW:</span>
                                <input type="range" id="windowGradientSlider" class="window-gradient-slider" min="1" max="120" value="30" step="1" oninput="updateGradientSliderValue(this.value)">
                                <span style="font-size:12px; color:var(--text-main); font-weight:700; width:38px;" id="winSliderVal">30s</span>
                            </div>
                        </div>
                    </div>
                    <div style="height: 180px; position: relative;">
                        <canvas id="timelineHeatmapChart"></canvas>
                    </div>
                </div>

                <!-- Video-by-Video NLP & Topic Pools Graphs Embedded -->
                <div class="chart-section" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                    <div class="chart-card">
                        <h3>Semantic Topic Pools Composition</h3>
                        <canvas id="topicDoughnutChart" height="180"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Part-of-Speech (POS) Breakdown</h3>
                        <canvas id="posBarChart" height="180"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Substance vs. Filler Ratio</h3>
                        <canvas id="substanceDoughnutChart" height="180"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Word Size Distribution</h3>
                        <canvas id="wordLengthChart" height="180"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Net Speech Speed vs Gross WPM</h3>
                        <canvas id="wpmBoostChart" height="180"></canvas>
                    </div>
                </div>

                <!-- Full-Width Calligrapher's Pen Topic Density Span Panel -->
                <div class="topic-span-panel">
                    <div class="topic-span-title-bar">
                        <h3>🖊️ Calligrapher's Pen Topic Ribbons</h3>
                    </div>
                    <div style="height: 180px; position: relative;">
                        <canvas id="topicSpanScatterChart"></canvas>
                    </div>
                </div>

                <!-- Interactive Topic Pool Filter Bar with Span Metrics -->
                <div class="topic-pools-panel" id="topicPoolsBar">
                </div>

                <!-- Dedicated 3-View Switcher Bar -->
                <div class="layer-bar">
                    <span style="font-size:13px; color:var(--text-muted); font-weight:600;">Transcript View:</span>
                    <button class="layer-btn active" id="layerBtn1" onclick="switchLayer(1)">⏱️ Timestamped Raw Captions</button>
                    <button class="layer-btn" id="layerBtn05" onclick="switchLayer(0.5)">🎯 Punctuation Clauses (. ! ? / Pauses)</button>
                    <button class="layer-btn" id="layerBtn2" onclick="switchLayer(2)">🏷️ Topic Tagged Clauses</button>
                </div>

                <div class="transcript-md-box" id="vTranscriptBox">Select a transcript to inspect...</div>
            </div>
        </div>
    </div>

    <!-- TAB 3: Channel Deep-Dive Database & Creator Intelligence Studio -->
    <div id="channelDbTab" class="tab-pane">
        <div class="channel-db-container">
            <div class="channel-db-sidebar">
                <div class="channel-search-box">
                    <input type="text" id="chSearchInput" class="search-input" style="width:100%; box-sizing:border-box;" placeholder="Search creator name..." oninput="filterChannelDbList(this.value)">
                </div>
                <div class="channel-db-list" id="channelDbList">
                </div>
            </div>
            <div class="viewer-content">
                <div class="viewer-header">
                    <div class="viewer-header-info">
                        <h2 id="chTitle">Select a channel from the left</h2>
                        <p id="chMeta">Choose any creator to view aggregated channel statistics, speech profiles, and topic composition.</p>
                    </div>
                </div>

                <div class="stats-grid" id="chStatsGrid">
                </div>

                <!-- CREATOR CHANNEL INTELLIGENCE STUDIO WORKBENCH (For "A Life Engineered") -->
                <div id="channelIntelligenceStudio" style="display:none; background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.4);">
                    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 16px;">
                        <div>
                            <h3 id="studioHeaderTitle" style="margin:0; font-size:18px; color:var(--accent-blue);">🏛️ Universal Channel Intelligence Studio</h3>
                            <p id="studioHeaderSub" style="margin:4px 0 0 0; font-size:12.5px; color:var(--text-muted);">Multi-Perspective Knowledge Synthesis &amp; Technical Playbooks across Hydrated Creator Catalog</p>
                        </div>
                        <div style="display:flex; gap:6px;">
                            <button class="subtab-btn active" onclick="switchStudioLens('lensPillars', this)">🧭 1. Topic Pillars</button>
                            <button class="subtab-btn" onclick="switchStudioLens('lensPlaybooks', this)">🧠 2. Career Playbooks</button>
                            <button class="subtab-btn" onclick="switchStudioLens('lensRoles', this)">🎓 3. Role Matrix</button>
                            <button class="subtab-btn" onclick="switchStudioLens('lensQuotes', this)">🔍 4. Quote Search</button>
                            <button class="subtab-btn" onclick="switchStudioLens('lensRoi', this)">⏱️ 5. ROI Sorting</button>
                        </div>
                    </div>

                    <!-- LENS 1: Conceptual Topic Pillars -->
                    <div id="lensPillars" class="studio-lens-pane">
                        <div id="pillarsContent"></div>
                    </div>

                    <!-- LENS 2: Synthesized Playbooks -->
                    <div id="lensPlaybooks" class="studio-lens-pane" style="display:none;">
                        <div id="playbooksContent"></div>
                    </div>

                    <!-- LENS 3: Role & Experience Level Matrix -->
                    <div id="lensRoles" class="studio-lens-pane" style="display:none;">
                        <div style="margin-bottom: 14px; display: flex; gap: 8px; align-items: center;">
                            <span style="font-size: 13px; color: var(--text-muted); font-weight: 600;">Filter by Role Stage:</span>
                            <button class="subtab-btn active" onclick="filterStudioRole('ALL', this)">All Stage Videos</button>
                            <button class="subtab-btn" onclick="filterStudioRole('Junior / Mid-Level (L4/SDE1)', this)">Junior SDE (L4)</button>
                            <button class="subtab-btn" onclick="filterStudioRole('Senior Engineer (L5/SDE2)', this)">Senior SDE (L5)</button>
                            <button class="subtab-btn" onclick="filterStudioRole('Staff / Principal (L6/L7+)', this)">Staff/Principal (L6+)</button>
                            <button class="subtab-btn" onclick="filterStudioRole('Engineering Manager', this)">Eng Manager</button>
                        </div>
                        <div id="rolesContent"></div>
                    </div>

                    <!-- LENS 4: Cross-Video Spoken Quote Search -->
                    <div id="lensQuotes" class="studio-lens-pane" style="display:none;">
                        <div style="margin-bottom: 14px;">
                            <input type="text" id="quoteSearchInput" class="search-input" style="width: 100%; box-sizing: border-box; font-size: 14px; padding: 10px 14px;" placeholder="Type any keyword (e.g. promo, pip, salary, offer, meta, level, conflict) to search exact spoken quotes across all 73 transcripts..." oninput="searchStudioQuotes(this.value)">
                        </div>
                        <div id="quotesContent" style="max-height: 480px; overflow-y: auto; background: #0f172a; border-radius: 8px; border: 1px solid var(--card-border); padding: 12px;"></div>
                    </div>

                    <!-- LENS 5: ROI & Takeaways -->
                    <div id="lensRoi" class="studio-lens-pane" style="display:none;">
                        <div id="roiContent"></div>
                    </div>
                </div>

                <div class="chart-section" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); margin-bottom:20px;">
                    <div class="chart-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <h3 id="chChartTitle" style="margin:0;">Channel Topic Focus Breakdown</h3>
                            <button id="chBackBtn" class="ch-back-btn" onclick="resetChannelTopicChartLevel()">⬅️ Back to Macro Categories</button>
                        </div>
                        <p id="chChartSub" style="font-size:11px; color:var(--text-muted); margin:0 0 10px 0;">Click any macro category slice to expand into granular sub-topics!</p>
                        <canvas id="chTopicDoughnutChart" height="220"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Hydrated Videos per Channel</h3>
                        <div style="max-height: 240px; overflow-y: auto; background-color: #0f172a; border-radius: 8px; padding: 10px;">
                            <table style="font-size:12px;">
                                <thead>
                                    <tr>
                                        <th>Video Title</th>
                                        <th>Duration</th>
                                        <th>Words</th>
                                    </tr>
                                </thead>
                                <tbody id="chVideoTableBody">
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 4: Global Topic & Category Taxonomy -->
    <div id="globalTopicTab" class="tab-pane">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Generated Topics</div>
                <div class="stat-value" style="color:var(--accent-blue);">{len(global_topic_db)} Topics</div>
                <div class="stat-sub">Across 4 Macro Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Macro Categories</div>
                <div class="stat-value" style="color:var(--accent-purple);">4 Categories</div>
                <div class="stat-sub">Hardware, AI/Software, Esports, Brain/Design</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Topic Word Coverage</div>
                <div class="stat-value" style="color:var(--accent-green);">{sum(t['total_words'] for t in global_topic_db.values()):,} words</div>
                <div class="stat-sub">Across {hydrated_count} hydrated videos</div>
            </div>
        </div>

        <div class="chart-section" style="grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); margin-bottom:20px;">
            <div class="chart-card">
                <h3>Global Topic Prevalence Matrix (Total Words Covered)</h3>
                <canvas id="globalTopicBarChart" height="260"></canvas>
            </div>
            <div class="chart-card">
                <h3>Macro Category Share Composition</h3>
                <canvas id="macroCategoryDoughnutChart" height="260"></canvas>
            </div>
        </div>

        <div class="table-card">
            <h3>Global Topic &amp; Category Taxonomy Matrix</h3>
            <table>
                <thead>
                    <tr>
                        <th>Macro Category</th>
                        <th>Topic Name</th>
                        <th>Channels Covered</th>
                        <th>Videos Covered</th>
                        <th>Total Clauses</th>
                        <th>Total Words</th>
                    </tr>
                </thead>
                <tbody id="globalTopicTableBody">
                </tbody>
            </table>
        </div>
    </div>

    <!-- TAB 5: Text Granularity Analytics -->
    <div id="granularityTab" class="tab-pane">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Characters</div>
                <div class="stat-value" style="color: var(--accent-blue);">{g_total_chars:,}</div>
                <div class="stat-sub">~{g_avg_cps} chars / sec avg pace</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Words</div>
                <div class="stat-value" style="color: var(--accent-purple);">{g_total_words:,}</div>
                <div class="stat-sub">~{g_avg_wpm} WPM average speaking rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Clauses (. ! ? / Pauses)</div>
                <div class="stat-value" style="color: var(--accent-green);">{g_total_clauses:,}</div>
                <div class="stat-sub">Average ~{round(g_total_words/max(1, g_total_clauses), 1)} words / clause</div>
            </div>
        </div>

        <div class="chart-section" style="grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));">
            <div class="chart-card">
                <h3>Speech Velocity Profile (Words / Min vs. Characters / Sec per Creator)</h3>
                <canvas id="velocityChart" height="260"></canvas>
            </div>
            <div class="chart-card">
                <h3>Text Abstraction Volumes (Characters vs. Words vs. Clauses)</h3>
                <canvas id="volumeChart" height="260"></canvas>
            </div>
        </div>

        <div class="table-card">
            <h3>Hydrated Videos Granularity Matrix</h3>
            <div class="controls">
                <input type="text" id="gSearchInput" class="search-input" placeholder="Search title or channel...">
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Channel</th>
                        <th>Video Title</th>
                        <th>Duration</th>
                        <th>Characters</th>
                        <th>Words</th>
                        <th>Clauses (. ! ? / Pauses)</th>
                        <th>WPM</th>
                        <th>Words/Clause</th>
                    </tr>
                </thead>
                <tbody id="granularityTableBody">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const channelsData = {channels_json_str};
        const graphData = {graph_json_str};
        const queueSample = {queue_json_str};
        let hydratedVideos = {hydrated_json_str};
        const granularityData = {granularity_json_str};
        const linguisticData = {linguistic_json_str};
        const channelDb = {channel_db_json_str};
        const universalStudioDb = {universal_studio_db_json_str};
        const globalTopicDb = {global_topic_db_json_str};
        const FREE_TIER_CREDITS = 9.40;

        const MACRO_CATEGORY_MAP = {{
            'Hardware & Electronics Repair': ['Console Hardware & Components', 'Diagnostics & Liquid Repair', 'eBay Sourcing & Profit Margins'],
            'AI, Computing & Software': ['AI, LLMs & Neural Models', 'Software Architecture & Code', 'Operating Systems & Dev Tools', 'Performance & Benchmarks'],
            'Esports & Creator Content': ['VCT Match Strategy & Rounds', 'Streamer Reactions & Commentary'],
            'Science, Brain & Design': ['Neuroscience & Home Design', 'Productivity & Knowledge Work']
        }};

        let selectedChannelNames = new Set();
        let freeCoveredNames = new Set();
        let activeHydratedId = hydratedVideos.length > 0 ? hydratedVideos[0].id : null;
        let activeChannelDbName = Object.keys(channelDb).length > 0 ? Object.keys(channelDb)[0] : null;

        let currentLayer = 1;
        let activeTopicFilter = 'ALL';
        let granularityChartsInitialized = false;
        let globalTopicChartsInitialized = false;

        let heatmapChartInst = null;
        let topicSpanScatterInst = null;
        let metricToggles = {{ wpm: true, substance: true, wordLen: true, nounsVerbs: true }};
        let currentWindowSec = 30;

        let topicChartInst = null;
        let posChartInst = null;
        let substanceChartInst = null;
        let wordLengthChartInst = null;
        let wpmBoostChartInst = null;
        
        let chTopicChartInst = null;
        let chTopicChartLevel = 1; // 1 = Macro Categories, 2 = Granular Sub-Topics

        // Custom Calligrapher's Pen Topic Ribbon Plugin
        const calligraphersPenRibbonPlugin = {{
            id: 'calligraphersPenRibbon',
            afterDatasetsDraw(chart) {{
                const {{ ctx, chartArea, scales }} = chart;
                if (!chartArea || !scales || !scales.x || !scales.y) return;
                const x = scales.x;
                const y = scales.y;
                if (!chart.config.options.customMultiSpans) return;

                const mDataMap = chart.config.options.customMultiSpans;
                const pools = chart.config.options.customPools || [];
                const colors = ['#38bdf8', '#c084fc', '#4ade80', '#fbbf24', '#fb7185', '#a78bfa'];

                ctx.save();
                pools.forEach((pool, pIdx) => {{
                    const topicName = pool.topic;
                    const data = mDataMap[topicName] || {{}};
                    const yPixel = y.getPixelForValue(pIdx);
                    const color = colors[pIdx % colors.length];

                    const allSpans = [...(data.tight_spans||[]), ...(data.moderate_spans||[]), ...(data.loose_spans||[])];

                    allSpans.forEach(span => {{
                        if (span.match_count < 2) return;

                        const subStart = x.getPixelForValue(span.start_sec);
                        const subEnd = x.getPixelForValue(span.end_sec);
                        const densRatio = Math.min(1.0, Math.max(0.1, span.density_pct / 100.0));
                        
                        const ribbonH = Math.round(3 + (densRatio * 13));
                        const ribbonR = ribbonH / 2;

                        const subLeft = subStart - ribbonR;
                        const subRight = subEnd + ribbonR;
                        const subW = Math.max(ribbonH, subRight - subLeft);
                        const subTop = yPixel - ribbonR;

                        ctx.beginPath();
                        ctx.fillStyle = color + '66';
                        ctx.strokeStyle = color;
                        ctx.lineWidth = 1.5;

                        ctx.arc(subStart, subTop + ribbonR, ribbonR, Math.PI / 2, (3 * Math.PI) / 2);
                        ctx.lineTo(subEnd, subTop);
                        ctx.arc(subEnd, subTop + ribbonR, ribbonR, (3 * Math.PI) / 2, Math.PI / 2);
                        ctx.lineTo(subStart, subTop + ribbonH);
                        ctx.fill();
                        ctx.stroke();
                    }});
                }});
                ctx.restore();
            }}
        }};

        // Render Hierarchical Topographical Narrative Terrain Canvas
        function renderHierarchicalTerrainCanvas(item) {{
            const canvas = document.getElementById('terrainCanvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * 2;
            canvas.height = rect.height * 2;
            ctx.scale(2, 2);

            const W = rect.width;
            const H = rect.height;

            ctx.clearRect(0, 0, W, H);

            const sections = item.organic_sections || [];
            const mDataMap = item.multi_strength_spans || {{}};
            const pools = item.topic_pools || [];
            const buckets1s = item.timeseries_1s || [];
            const maxSec = buckets1s.length > 0 ? buckets1s[buckets1s.length - 1].s : 600;

            const padX = 20;
            const drawW = W - (padX * 2);
            const groundY = H - 24;

            const layerColors = ['#1e293b', '#0284c7', '#7c3aed', '#059669', '#d97706', '#e11d48'];

            // 1. BASE LAYER 0
            sections.forEach((sec, idx) => {{
                const xStart = padX + (sec.start_sec / parseFloat(maxSec)) * drawW;
                const xEnd = padX + (sec.end_sec / parseFloat(maxSec)) * drawW;
                const wSec = Math.max(12, xEnd - xStart);
                const hBase = 32;

                const grad = ctx.createLinearGradient(xStart, groundY - hBase, xStart, groundY);
                grad.addColorStop(0, '#334155');
                grad.addColorStop(1, '#1e293b');

                ctx.beginPath();
                ctx.fillStyle = grad;
                ctx.strokeStyle = '#475569';
                ctx.lineWidth = 1.5;
                ctx.roundRect(xStart, groundY - hBase, wSec, hBase, [8, 8, 0, 0]);
                ctx.fill();
                ctx.stroke();
            }});

            // 2. LAYER 1
            pools.forEach((pool, pIdx) => {{
                const tName = pool.topic;
                const data = mDataMap[tName] || {{}};
                const modSpans = data.moderate_spans || [];
                const cColor = layerColors[(pIdx + 1) % layerColors.length];

                modSpans.forEach(sp => {{
                    const xStart = padX + (sp.start_sec / parseFloat(maxSec)) * drawW;
                    const xEnd = padX + (sp.end_sec / parseFloat(maxSec)) * drawW;
                    const wSpan = Math.max(14, xEnd - xStart);
                    const hLevel1 = 65;

                    const grad = ctx.createLinearGradient(xStart, groundY - hLevel1, xStart, groundY - 32);
                    grad.addColorStop(0, cColor + 'aa');
                    grad.addColorStop(1, cColor + '33');

                    ctx.beginPath();
                    ctx.fillStyle = grad;
                    ctx.strokeStyle = cColor;
                    ctx.lineWidth = 1.5;
                    ctx.roundRect(xStart, groundY - hLevel1, wSpan, 33, [12, 12, 4, 4]);
                    ctx.fill();
                    ctx.stroke();
                }});
            }});

            // 3. LAYER 2
            pools.forEach((pool, pIdx) => {{
                const tName = pool.topic;
                const data = mDataMap[tName] || {{}};
                const tightSpans = data.tight_spans || [];
                const cColor = layerColors[(pIdx + 1) % layerColors.length];

                tightSpans.forEach(sp => {{
                    const xStart = padX + (sp.start_sec / parseFloat(maxSec)) * drawW;
                    const xEnd = padX + (sp.end_sec / parseFloat(maxSec)) * drawW;
                    const wSpan = Math.max(16, xEnd - xStart);
                    const hPeak = 105;

                    const grad = ctx.createLinearGradient(xStart, groundY - hPeak, xStart, groundY - 65);
                    grad.addColorStop(0, '#f8fafc');
                    grad.addColorStop(1, cColor);

                    ctx.beginPath();
                    ctx.fillStyle = grad;
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 2;
                    ctx.roundRect(xStart, groundY - hPeak, wSpan, 40, [16, 16, 6, 6]);
                    ctx.fill();
                    ctx.stroke();
                }});
            }});

            ctx.beginPath();
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2;
            ctx.moveTo(padX, groundY);
            ctx.lineTo(W - padX, groundY);
            ctx.stroke();
        }}

        function switchTab(tabId, btnElem) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btnElem.classList.add('active');

            if (tabId === 'viewerTab' && hydratedVideos.length > 0) {{
                sortViewerList(document.getElementById('vSortSelect').value || 'title_asc');
                const idx = hydratedVideos.findIndex(v => v.id === activeHydratedId);
                loadHydratedVideo(idx >= 0 ? idx : 0);
            }} else if (tabId === 'channelDbTab') {{
                renderChannelDbList(channelDb);
                if (activeChannelDbName) loadChannelDbProfile(activeChannelDbName);
            }} else if (tabId === 'globalTopicTab' && !globalTopicChartsInitialized) {{
                initGlobalTopicCharts();
                renderGlobalTopicTable(globalTopicDb);
                globalTopicChartsInitialized = true;
            }} else if (tabId === 'granularityTab' && !granularityChartsInitialized) {{
                initGranularityCharts();
                renderGranularityTable(granularityData);
                granularityChartsInitialized = true;
            }}
        }}

        function switchOverviewSubTab(paneId, btnElem) {{
            const container = btnElem.closest('.subtab-panel');
            if (!container) return;
            
            container.querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
            btnElem.classList.add('active');

            container.querySelectorAll('.subtab-pane').forEach(p => p.style.display = 'none');
            const target = container.querySelector('#' + paneId);
            if (target) target.style.display = 'block';

            if (paneId === 'topicViewPane' && typeof channelTopicChartInstance !== 'undefined' && !channelTopicChartInstance) {{
                initChannelTopicChart();
            }}
        }}

        /* Channel Deep-Dive Functions */
        function renderChannelDbList(dbMap) {{
            const listEl = document.getElementById('channelDbList');
            listEl.innerHTML = '';
            const names = Object.keys(dbMap).sort();
            names.forEach(name => {{
                const item = dbMap[name];
                const div = document.createElement('div');
                div.className = `channel-db-item ${{name === activeChannelDbName ? 'active' : ''}}`;
                div.onclick = () => loadChannelDbProfile(name);
                div.innerHTML = `
                    <div class="channel-db-item-title">${{name}}</div>
                    <div class="channel-db-item-meta">
                        <span>${{item.video_count}} Hydrated Videos</span>
                        <span>${{item.total_words.toLocaleString()}} Words</span>
                    </div>
                `;
                listEl.appendChild(div);
            }});
        }}

        function filterChannelDbList(q) {{
            const filtered = {{}};
            const query = q.toLowerCase();
            for (const [name, data] of Object.entries(channelDb)) {{
                if (name.toLowerCase().includes(query) || (data.handle && data.handle.toLowerCase().includes(query))) {{
                    filtered[name] = data;
                }}
            }}
            renderChannelDbList(filtered);
        }}

        /* Creator Channel Intelligence Studio Functions */
        let currentStudioChannel = 'A Life Engineered';

        function getActiveStudioDb() {{
            return (universalStudioDb && universalStudioDb[currentStudioChannel]) ? universalStudioDb[currentStudioChannel] : null;
        }}

        function switchStudioLens(lensId, btn) {{
            const parent = btn.closest('#channelIntelligenceStudio');
            if (!parent) return;
            parent.querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            parent.querySelectorAll('.studio-lens-pane').forEach(p => p.style.display = 'none');
            const target = parent.querySelector('#' + lensId);
            if (target) target.style.display = 'block';
        }}

        function renderStudioPillars() {{
            const el = document.getElementById('pillarsContent');
            const studioData = getActiveStudioDb();
            if (!el || !studioData || !studioData.pillars) return;
            let html = '';
            Object.entries(studioData.pillars).forEach(([pillarName, vList]) => {{
                if (vList.length === 0) return;
                html += `
                    <details class="dashboard-drawer" open style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; margin-bottom: 14px; padding: 12px 16px;">
                        <summary style="font-size: 14.5px; font-weight: 700; color: var(--accent-blue); cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
                            <span>${{pillarName}} (${{vList.length}} Videos)</span>
                            <span style="font-size: 11px; color: var(--text-muted);">▼ Toggle Videos</span>
                        </summary>
                        <div style="margin-top: 12px; display: grid; gap: 10px;">
                `;
                vList.forEach(v => {{
                    const readTime = (v.word_count / 220).toFixed(1);
                    const savedPct = Math.round(100 - (readTime / Math.max(0.1, v.duration) * 100));
                    html += `
                        <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                                <a href="${{v.url}}" target="_blank" style="font-weight: 700; font-size: 13.5px; color: #f8fafc; text-decoration: none;">${{v.title}}</a>
                                <span style="font-size: 11px; background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); padding: 3px 8px; border-radius: 4px; font-weight: 600; white-space: nowrap;">Read ${{readTime}}m (Saved ${{savedPct}}%)</span>
                            </div>
                            <p style="font-size: 12.5px; color: var(--text-muted); margin: 6px 0 8px 0; line-height: 1.4;">${{v.synopsis}}</p>
                            ${{v.takeaways && v.takeaways.length > 0 ? `
                                <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #cbd5e1; line-height: 1.5;">
                                    ${{v.takeaways.map(t => `<li style="margin-bottom:2px;">${{t}}</li>`).join('')}}
                                </ul>
                            ` : ''}}
                        </div>
                    `;
                }});
                html += `</div></details>`;
            }});
            el.innerHTML = html;
        }}

        function renderStudioPlaybooks() {{
            const el = document.getElementById('playbooksContent');
            const studioData = getActiveStudioDb();
            if (!el || !studioData || !studioData.playbooks) return;
            let html = '';
            studioData.playbooks.forEach(pb => {{
                html += `
                    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(124, 58, 237, 0.35); border-radius: 10px; margin-bottom: 16px; padding: 16px;">
                        <h4 style="margin: 0 0 4px 0; font-size: 15.5px; color: var(--accent-purple);">${{pb.title}}</h4>
                        <p style="margin: 0 0 12px 0; font-size: 12px; color: var(--text-muted);">${{pb.subtitle}}</p>
                        <div style="display: grid; gap: 10px;">
                `;
                pb.rules.forEach(r => {{
                    html += `
                        <div style="background: rgba(15, 23, 42, 0.7); border-left: 3px solid var(--accent-purple); border-radius: 6px; padding: 12px;">
                            <div style="font-weight: 700; font-size: 13.5px; color: #f8fafc; margin-bottom: 4px;">${{r.rule}}</div>
                            <div style="font-size: 12.5px; color: #cbd5e1; margin-bottom: 6px; line-height: 1.4;"><strong>Core Insight:</strong> ${{r.insight}}</div>
                            <div style="font-size: 12px; color: var(--accent-green); font-weight: 600;">⚡ Actionable Rule: ${{r.action}}</div>
                        </div>
                    `;
                }});
                html += `</div></div>`;
            }});
            el.innerHTML = html;
        }}

        function renderStudioRoles(selectedRole) {{
            const el = document.getElementById('rolesContent');
            const studioData = getActiveStudioDb();
            if (!el || !studioData || !studioData.videos) return;
            const filtered = studioData.videos;
            let html = `<div style="font-size:12.5px; color:var(--text-muted); margin-bottom:12px;">Showing <strong>${{filtered.length}} videos</strong> for <strong>${{currentStudioChannel}}</strong>:</div><div style="display:grid; gap:10px;">`;
            filtered.forEach(v => {{
                html += `
                    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
                            <a href="${{v.url}}" target="_blank" style="font-weight: 700; font-size: 13.5px; color: #f8fafc; text-decoration: none;">${{v.title}}</a>
                            <span style="font-size:11px; background:rgba(16,185,129,0.15); color:var(--accent-green); padding:2px 6px; border-radius:4px; white-space:nowrap;">${{v.pillar}}</span>
                        </div>
                        <p style="font-size: 12px; color: #cbd5e1; margin: 6px 0 0 0;">${{v.synopsis}}</p>
                    </div>
                `;
            }});
            html += `</div>`;
            el.innerHTML = html;
        }}

        function filterStudioRole(role, btn) {{
            btn.closest('#lensRoles').querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderStudioRoles(role);
        }}

        function searchStudioQuotes(query) {{
            const el = document.getElementById('quotesContent');
            const studioData = getActiveStudioDb();
            if (!el || !studioData || !studioData.quotes) return;
            const q = query.toLowerCase().trim();
            const matches = q ? studioData.quotes.filter(item => item.quote.toLowerCase().includes(q) || item.video_title.toLowerCase().includes(q)) : studioData.quotes.slice(0, 35);

            let html = `<div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">Found <strong>${{matches.length}} timestamped spoken quote matches</strong> across all ${{studioData.total_videos}} transcripts:</div>`;
            matches.forEach(m => {{
                html += `
                    <div style="background: rgba(30, 41, 59, 0.6); border-left: 3px solid var(--accent-blue); padding: 8px 12px; margin-bottom: 8px; border-radius: 4px;">
                        <div style="font-size: 11px; color: var(--accent-blue); font-weight: 700; margin-bottom: 2px;">${{m.video_title}}</div>
                        <div style="font-size: 12.5px; color: #e2e8f0; font-style: italic;">"${{m.quote}}"</div>
                    </div>
                `;
            }});
            el.innerHTML = html;
        }}

        function renderStudioRoi() {{
            const el = document.getElementById('roiContent');
            const studioData = getActiveStudioDb();
            if (!el || !studioData || !studioData.videos) return;
            const sorted = [...studioData.videos].sort((a, b) => b.word_count - a.word_count);
            let html = '<div style="display:grid; gap:10px;">';
            sorted.forEach(v => {{
                const readTime = (v.word_count / 220).toFixed(1);
                const savedPct = Math.round(100 - (readTime / Math.max(0.1, v.duration) * 100));
                html += `
                    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <a href="${{v.url}}" target="_blank" style="font-weight: 700; font-size: 13.5px; color: #f8fafc; text-decoration: none;">${{v.title}}</a>
                            <div style="font-size: 11.5px; color: var(--text-muted); margin-top:2px;">${{v.pillar}} • ${{v.word_count.toLocaleString()}} spoken words</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size: 13px; font-weight: 700; color: var(--accent-green);">${{savedPct}}% Time Saved</div>
                            <div style="font-size: 11px; color: var(--text-muted);">Watch ${{v.duration}}m ➜ Read ${{readTime}}m</div>
                        </div>
                    </div>
                `;
            }});
            html += '</div>';
            el.innerHTML = html;
        }}

        function loadChannelDbProfile(chName) {{
            const data = channelDb[chName];
            if (!data) return;
            activeChannelDbName = chName;
            currentStudioChannel = chName;
            chTopicChartLevel = 1;

            document.getElementById('chTitle').innerText = `🏛️ Creator Profile: ${{chName}}`;
            document.getElementById('chMeta').innerText = `Aggregated catalog stats across ${{data.video_count}} hydrated video transcripts.`;

            const studioEl = document.getElementById('channelIntelligenceStudio');
            const studioData = getActiveStudioDb();

            if (studioEl) {{
                if (studioData && studioData.videos && studioData.videos.length > 0) {{
                    studioEl.style.display = 'block';
                    document.getElementById('studioHeaderTitle').innerText = `🏛️ Channel Intelligence Studio: "${{chName}}"`;
                    document.getElementById('studioHeaderSub').innerText = `Multi-Perspective Knowledge Synthesis across ${{studioData.total_videos}} Hydrated Videos (${{studioData.total_words.toLocaleString()}} spoken words)`;
                    renderStudioPillars();
                    renderStudioPlaybooks();
                    renderStudioRoles('ALL');
                    searchStudioQuotes('');
                    renderStudioRoi();
                }} else {{
                    studioEl.style.display = 'none';
                }}
            }}

            const totClauses = data.total_clauses || data.total_sentences || 0;

            const grid = document.getElementById('chStatsGrid');
            grid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Hydrated Videos</div>
                    <div class="stat-value" style="color:var(--accent-blue);">${{data.video_count}} Videos</div>
                    <div class="stat-sub">Across creator catalog</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Aggregated Words</div>
                    <div class="stat-value" style="color:var(--accent-purple);">${{data.total_words.toLocaleString()}} words</div>
                    <div class="stat-sub">Across all transcripts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Clauses (. ! ? / Pauses)</div>
                    <div class="stat-value" style="color:var(--accent-green);">${{totClauses.toLocaleString()}} clauses</div>
                    <div class="stat-sub">~${{(data.total_words/Math.max(1, totClauses)).toFixed(1)}} words / clause</div>
                </div>
            `;

            // Channel Video List Table
            const tbody = document.getElementById('chVideoTableBody');
            tbody.innerHTML = '';
            (data.videos || []).forEach(v => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${{v.title}}</strong></td>
                    <td>${{v.duration}}</td>
                    <td>${{v.words.toLocaleString()}}</td>
                `;
                tbody.appendChild(tr);
            }});

            renderChannelTopicDoughnutLevel1(data);
            renderChannelDbList(channelDb);
        }}

        // Level 1: Macro Categories Pie Chart for Channel
        function renderChannelTopicDoughnutLevel1(data) {{
            if (typeof Chart === 'undefined') return;
            const topicCounts = data.topic_counts || {{}};

            // Group topicCounts into 4 Macro Categories
            const macroTotals = {{}};
            Object.entries(topicCounts).forEach(([tName, count]) => {{
                let foundCat = 'General / Uncategorized';
                for (const [catName, subList] of Object.entries(MACRO_CATEGORY_MAP)) {{
                    if (subList.includes(tName)) {{
                        foundCat = catName;
                        break;
                    }}
                }}
                macroTotals[foundCat] = (macroTotals[foundCat] || 0) + count;
            }});

            const labels = Object.keys(macroTotals);
            const values = Object.values(macroTotals);

            document.getElementById('chChartTitle').innerText = 'Channel Macro Category Focus (Click Slice to Drill Down)';
            document.getElementById('chChartSub').innerText = 'Click any category slice to expand into granular sub-topic breakdown!';
            document.getElementById('chBackBtn').style.display = 'none';

            if (chTopicChartInst) chTopicChartInst.destroy();

            chTopicChartInst = new Chart(document.getElementById('chTopicDoughnutChart').getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: values,
                        backgroundColor: ['#38bdf8', '#c084fc', '#4ade80', '#fbbf24', '#fb7185']
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    onClick: (evt, elements) => {{
                        if (elements && elements.length > 0) {{
                            const sliceIndex = elements[0].index;
                            const selectedCat = labels[sliceIndex];
                            drillDownChannelTopicCategory(data, selectedCat);
                        }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 10 }} }} }},
                        tooltip: {{
                            callbacks: {{
                                label: (ctx) => `${{ctx.label}}: ${{ctx.raw}} clauses (Click to Drill Down 🔍)`
                            }}
                        }}
                    }}
                }}
            }});
        }}

        // Level 2: Drill-down Sub-Topics Pie Chart for Selected Macro Category
        function drillDownChannelTopicCategory(data, catName) {{
            if (typeof Chart === 'undefined') return;
            const topicCounts = data.topic_counts || {{}};
            const subTopicsAllowed = MACRO_CATEGORY_MAP[catName] || [];

            const subLabels = [];
            const subValues = [];

            Object.entries(topicCounts).forEach(([tName, count]) => {{
                if (subTopicsAllowed.includes(tName) || (catName === 'General / Uncategorized' && !Object.values(MACRO_CATEGORY_MAP).flat().includes(tName))) {{
                    subLabels.push(tName);
                    subValues.push(count);
                }}
            }});

            if (subLabels.length === 0) return;

            chTopicChartLevel = 2;
            document.getElementById('chChartTitle').innerText = `🔍 Sub-Topics: [${{catName}}]`;
            document.getElementById('chChartSub').innerText = `Detailed granular sub-topic composition within ${{catName}}.`;
            document.getElementById('chBackBtn').style.display = 'inline-flex';

            if (chTopicChartInst) chTopicChartInst.destroy();

            chTopicChartInst = new Chart(document.getElementById('chTopicDoughnutChart').getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: subLabels,
                    datasets: [{{
                        data: subValues,
                        backgroundColor: ['#38bdf8', '#c084fc', '#4ade80', '#fbbf24', '#fb7185', '#a78bfa']
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{
                        legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 10 }} }} }},
                        tooltip: {{
                            callbacks: {{
                                label: (ctx) => `${{ctx.label}}: ${{ctx.raw}} clauses`
                            }}
                        }}
                    }}
                }}
            }});
        }}

        function resetChannelTopicChartLevel() {{
            const data = channelDb[activeChannelDbName];
            if (data) renderChannelTopicDoughnutLevel1(data);
        }}

        /* Global Topic & Category Taxonomy Functions */
        function initGlobalTopicCharts() {{
            if (typeof Chart === 'undefined') return;

            const topics = Object.values(globalTopicDb).sort((a, b) => b.total_words - a.total_words);

            new Chart(document.getElementById('globalTopicBarChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: topics.map(t => t.topic),
                    datasets: [{{
                        label: 'Total Words Covered',
                        data: topics.map(t => t.total_words),
                        backgroundColor: '#38bdf8'
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}, grid: {{ color: '#334155' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            // Macro Category Share
            const catMap = {{}};
            topics.forEach(t => {{
                catMap[t.category] = (catMap[t.category] || 0) + t.total_words;
            }});

            new Chart(document.getElementById('macroCategoryDoughnutChart').getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: Object.keys(catMap),
                    datasets: [{{
                        data: Object.values(catMap),
                        backgroundColor: ['#38bdf8', '#c084fc', '#4ade80', '#fbbf24']
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 11 }} }} }} }}
                }}
            }});
        }}

        function renderGlobalTopicTable(dbMap) {{
            const tbody = document.getElementById('globalTopicTableBody');
            tbody.innerHTML = '';
            const topics = Object.values(dbMap).sort((a, b) => b.total_words - a.total_words);
            topics.forEach(t => {{
                const totC = t.total_clauses || t.total_sentences || 0;
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="badge badge-sub">${{t.category}}</span></td>
                    <td><strong>${{t.topic}}</strong></td>
                    <td style="color:var(--accent-blue);">${{t.channel_count}} Channels</td>
                    <td style="color:var(--accent-purple);">${{t.videos_covered}} Videos</td>
                    <td>${{totC.toLocaleString()}}</td>
                    <td style="color:var(--accent-green);"><strong>${{t.total_words.toLocaleString()}} words</strong></td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function switchSimilarityView(mode, btn) {{
            document.getElementById('btnHighSim').classList.remove('active');
            document.getElementById('btnLowSim').classList.remove('active');
            btn.classList.add('active');

            if (mode === 'high') {{
                document.getElementById('highSimViewPane').style.display = 'block';
                document.getElementById('lowSimViewPane').style.display = 'none';
            }} else {{
                document.getElementById('highSimViewPane').style.display = 'none';
                document.getElementById('lowSimViewPane').style.display = 'block';
            }}
        }}

        function renderOrganicSections(item) {{
            const container = document.getElementById('organicSectionsContent');
            if (!container) return;

            const sections = item.organic_sections || [];
            if (sections.length === 0) {{
                container.innerHTML = '<div style="color:var(--text-muted); font-size:13px;">No organic topic shift break points detected for this video.</div>';
                return;
            }}

            let html = '';
            sections.forEach((sec, idx) => {{
                html += `
                    <div style="background: #0f172a; border: 1px solid var(--card-border); border-radius: 8px; padding: 10px 14px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 11px; font-weight: 700; color: var(--accent-amber);">Section #${{idx+1}} [${{sec.start_time || '00:00'}} - ${{sec.end_time || 'End'}}]</span>
                            <span class="badge badge-topic" style="margin:0;">Dominant: ${{sec.dominant_topic || 'General'}}</span>
                        </div>
                        <div style="font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">${{sec.title || 'Topic Shift Section'}}</div>
                        <div style="font-size: 11.5px; color: var(--text-muted);">${{sec.summary || 'Organic clause transition shift.'}}</div>
                    </div>
                `;
            }});
            container.innerHTML = html;
        }}

        function parseDurationSec(durStr) {{
            if (!durStr) return 0;
            const parts = durStr.split(':').map(Number);
            if (parts.length === 3) return parts[0]*3600 + parts[1]*60 + parts[2];
            if (parts.length === 2) return parts[0]*60 + parts[1];
            return parseFloat(durStr) || 0;
        }}

        function sortViewerList(sortKey) {{
            hydratedVideos.sort((a, b) => {{
                if (sortKey === 'title_asc') return a.title.localeCompare(b.title);
                if (sortKey === 'title_desc') return b.title.localeCompare(a.title);
                if (sortKey === 'channel_asc') return a.channel.localeCompare(b.channel);
                if (sortKey === 'channel_desc') return b.channel.localeCompare(a.channel);
                if (sortKey === 'dur_asc') return parseDurationSec(a.duration) - parseDurationSec(b.duration);
                if (sortKey === 'dur_desc') return parseDurationSec(b.duration) - parseDurationSec(a.duration);
                return 0;
            }});
            renderViewerList(hydratedVideos);
        }}

        function switchLayer(layerNum) {{
            currentLayer = layerNum;
            document.getElementById('layerBtn1').classList.toggle('active', layerNum === 1);
            document.getElementById('layerBtn05').classList.toggle('active', layerNum === 0.5);
            document.getElementById('layerBtn2').classList.toggle('active', layerNum === 2);
            const idx = hydratedVideos.findIndex(v => v.id === activeHydratedId);
            loadHydratedVideo(idx >= 0 ? idx : 0);
        }}

        function setTopicFilter(topicName) {{
            activeTopicFilter = topicName;
            const idx = hydratedVideos.findIndex(v => v.id === activeHydratedId);
            if (idx >= 0) {{
                renderTopicPoolsBar(hydratedVideos[idx]);
                renderTranscriptContent(hydratedVideos[idx]);
            }}
        }}

        function toggleHeatmapMetric(metricKey) {{
            metricToggles[metricKey] = !metricToggles[metricKey];
            const btnId = 'tog' + metricKey.charAt(0).toUpperCase() + metricKey.slice(1);
            const btn = document.getElementById(btnId);
            if (btn) btn.classList.toggle('active', metricToggles[metricKey]);
            const idx = hydratedVideos.findIndex(v => v.id === activeHydratedId);
            if (idx >= 0) renderMalleableTimelineChart(hydratedVideos[idx]);
        }}

        function updateGradientSliderValue(valStr) {{
            currentWindowSec = parseInt(valStr) || 30;
            document.getElementById('winSliderVal').innerText = currentWindowSec + 's';
            const idx = hydratedVideos.findIndex(v => v.id === activeHydratedId);
            if (idx >= 0) renderMalleableTimelineChart(hydratedVideos[idx]);
        }}

        function renderViewerList(list) {{
            const container = document.getElementById('viewerList');
            container.innerHTML = '';
            list.forEach((item, idx) => {{
                const div = document.createElement('div');
                div.className = `viewer-item ${{item.id === activeHydratedId ? 'active' : ''}}`;
                div.onclick = () => loadHydratedVideo(idx);
                div.innerHTML = `
                    <div class="viewer-item-title">${{item.title}}</div>
                    <div class="viewer-item-meta">
                        <span>${{item.channel}}</span>
                        <span>${{item.duration}}</span>
                    </div>
                `;
                container.appendChild(div);
            }});
        }}

        function loadHydratedVideo(idx) {{
            const item = hydratedVideos[idx];
            if (!item) return;
            activeHydratedId = item.id;
            activeTopicFilter = 'ALL';

            document.getElementById('vTitle').innerText = item.title;
            document.getElementById('vMeta').innerHTML = `<strong>Channel:</strong> ${{item.channel}} (${{item.handle}}) | <strong>Duration:</strong> ${{item.duration}} | <a href="${{item.url}}" target="_blank" style="color:var(--accent-blue);">Open URL</a>`;
            
            loadEmbeddedVideoNLP(item);
            renderExecutiveSummaryCard(item);
            renderHierarchicalTerrainCanvas(item);
            renderTopicPoolsBar(item);
            renderMalleableTimelineChart(item);
            renderTopicSpanScatterChart(item);
            renderOrganicSections(item);
            renderTranscriptContent(item);

            renderViewerList(hydratedVideos);
        }}

        function renderExecutiveSummaryCard(item) {{
            const container = document.getElementById('vSummaryPanel');
            if (!container) return;
            const summary = item.video_summary;
            if (!summary) {{
                container.style.display = 'none';
                return;
            }}
            container.style.display = 'block';

            const savedPct = summary.watch_time_min > 0 ? Math.round((summary.saved_time_min / summary.watch_time_min) * 100) : 0;

            let chaptersHtml = (summary.timestamped_chapters || []).map(ch => 
                `<span style="display:inline-block; background:rgba(30, 41, 59, 0.9); border:1px solid rgba(56, 189, 248, 0.3); border-radius:6px; padding:4px 8px; font-size:12px; margin:3px 4px 3px 0; color:#e2e8f0;">
                    <strong style="color:var(--accent-blue);">[${{ch.start}} - ${{ch.end}}]</strong> ${{ch.title}}
                </span>`
            ).join('');

            let conceptsHtml = (summary.key_concepts || []).map(c => 
                `<span style="display:inline-block; background:rgba(192, 132, 252, 0.15); border:1px solid rgba(192, 132, 252, 0.4); border-radius:12px; padding:2px 10px; font-size:11px; font-weight:700; color:#e9d5ff; margin-right:5px;">
                    🛠️ ${{c}}
                </span>`
            ).join('');

            let takeawaysHtml = (summary.key_takeaways || []).map(t => 
                `<li style="margin-bottom:6px; color:#cbd5e1; font-size:13px;">${{t}}</li>`
            ).join('');

            container.innerHTML = `
                <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 18px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">
                        <h3 style="margin: 0; font-size: 16px; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                            📄 Executive Video Summary &amp; Key Takeaways
                        </h3>
                        <span style="background: rgba(74, 222, 128, 0.15); border: 1px solid rgba(74, 222, 128, 0.4); color: #4ade80; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">
                            ⏱️ Watch: ${{summary.watch_time_min}}m ➜ Read: ${{summary.read_time_min}}m (${{savedPct}}% Time Saved)
                        </span>
                    </div>

                    <p style="margin: 0 0 14px 0; color: #94a3b8; font-size: 13.5px; line-height: 1.5; font-style: italic;">
                        "${{summary.synopsis}}"
                    </p>

                    <div style="margin-bottom: 14px;">
                        <h4 style="margin: 0 0 8px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--accent-blue);">
                            🎯 Core Technical Takeaways
                        </h4>
                        <ul style="margin: 0; padding-left: 18px; list-style-type: square;">
                            ${{takeawaysHtml}}
                        </ul>
                    </div>

                    <div style="margin-bottom: 14px;">
                        <h4 style="margin: 0 0 8px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--accent-purple);">
                            ⏱️ Spoken Chapter Breakdown
                        </h4>
                        <div>${{chaptersHtml}}</div>
                    </div>

                    <div>
                        <h4 style="margin: 0 0 8px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #34d399;">
                            🛠️ Key Concepts &amp; Vocabulary
                        </h4>
                        <div>${{conceptsHtml}}</div>
                    </div>
                </div>
            `;
        }}

        function renderTopicPoolsBar(item) {{
            const bar = document.getElementById('topicPoolsBar');
            if (!bar) return;
            const pools = item.topic_pools || [];

            let html = `<span style="font-size:12px; color:var(--text-muted); font-weight:700; margin-right:4px;">SEMANTIC TOPIC RIBBONS:</span>`;
            
            const totalClauses = (item.punct_clauses || item.punct_sentences || []).length;
            const allActive = activeTopicFilter === 'ALL' ? 'active' : '';
            html += `<button class="topic-pill ${{allActive}}" onclick="setTopicFilter('ALL')">🏷️ All Topics (${{totalClauses}})</button>`;

            pools.forEach(p => {{
                const isAct = activeTopicFilter === p.topic ? 'active' : '';
                const cCount = p.clause_count || p.sentence_count || 0;
                const hInfo = (p.tight_span_count !== undefined) ? ` | ${{p.tight_span_count + p.moderate_span_count + p.loose_span_count}} Spans (${{p.max_density_pct}}% Peak Density)` : '';
                html += `<button class="topic-pill ${{isAct}}" onclick="setTopicFilter('${{p.topic.replace(/'/g, "\\'")}}')">🏷️ ${{p.topic}} (${{cCount}} Clauses)${{hInfo}}</button>`;
            }});

            bar.innerHTML = html;
        }}

        function renderTranscriptContent(item) {{
            const box = document.getElementById('vTranscriptBox');
            if (!box) return;

            if (currentLayer === 2) {{
                const tagged = item.tagged_clauses || item.tagged_sentences || [];
                let filtered = tagged;
                if (activeTopicFilter !== 'ALL') {{
                    filtered = tagged.filter(s => s.topics && s.topics.includes(activeTopicFilter));
                }}

                const lines = filtered.map(s => {{
                    const hasTopics = s.topics && s.topics.length > 0;
                    const badges = hasTopics ? s.topics.map(t => `<span class="badge badge-topic">[${{t}}]</span>`).join(' ') : '';
                    const badgeLine = hasTopics ? `<div style="margin-bottom:3px;">${{badges}}</div>` : '';
                    return `<div style="margin-bottom:14px;">${{badgeLine}}<div>${{s.text}}</div></div>`;
                }});
                box.innerHTML = lines.join('');
            }} else if (currentLayer === 0.5) {{
                const clauses = item.punct_clauses || item.punct_sentences || [];
                box.innerText = clauses.join('\\n');
            }} else {{
                const mdText = (item.formatted_md_lines || []).join('\\n');
                box.innerText = mdText;
            }}
        }}

        function loadEmbeddedVideoNLP(item) {{
            const v = linguisticData.find(l => l.id === item.id) || {{
                net_wpm: item.net_wpm || 0,
                gross_wpm: item.gross_wpm || 0,
                pause_duration_sec: item.pause_duration_sec || 0,
                linguistics: item.linguistics || {{}}
            }};

            const ling = v.linguistics || {{}};
            const pos = ling.pos_counts || {{ nouns:0, verbs:0, adjectives:0, adverbs:0, pronouns:0, function_other:0 }};
            const wdist = ling.word_size_dist || {{ short_1_3:0, medium_4_6:0, long_7_9:0, very_long_10_plus:0 }};

            const grid = document.getElementById('nlpStatsGrid');
            grid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Net Active Speech WPM</div>
                    <div class="stat-value" style="color:var(--accent-green);">${{v.net_wpm || 0}} WPM</div>
                    <div class="stat-sub">Gross: ${{v.gross_wpm || 0}} WPM (+${{((v.net_wpm||0) - (v.gross_wpm||0)).toFixed(1)}} net boost)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Substance Ratio</div>
                    <div class="stat-value" style="color:var(--accent-purple);">${{((ling.substance_ratio||0)*100).toFixed(1)}}%</div>
                    <div class="stat-sub">Filler ratio: ${{((ling.filler_ratio||0)*100).toFixed(1)}}% (${{ling.filler_count||0}} fillers)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Vocabulary Diversity (TTR)</div>
                    <div class="stat-value" style="color:var(--accent-blue);">${{((ling.ttr_diversity||0)*100).toFixed(1)}}%</div>
                    <div class="stat-sub">${{ling.unique_words||0}} unique / ${{ling.total_words||0}} total words</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Average Word Length</div>
                    <div class="stat-value" style="color:var(--accent-amber);">${{ling.avg_word_length||0}} chars</div>
                    <div class="stat-sub">Pauses Excluded: ${{(v.pause_duration_sec||0).toFixed(1)}}s</div>
                </div>
            `;

            if (typeof Chart === 'undefined') return;

            const pools = item.topic_pools || [];
            if (topicChartInst) topicChartInst.destroy();
            topicChartInst = new Chart(document.getElementById('topicDoughnutChart').getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: pools.map(p => p.topic),
                    datasets: [{{
                        data: pools.map(p => p.clause_count || p.sentence_count || 0),
                        backgroundColor: ['#38bdf8', '#c084fc', '#4ade80', '#fbbf24', '#fb7185', '#a78bfa']
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 9 }} }} }} }}
                }}
            }});

            if (posChartInst) posChartInst.destroy();
            posChartInst = new Chart(document.getElementById('posBarChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: ['Nouns', 'Verbs', 'Adj', 'Adv', 'Pro', 'Func'],
                    datasets: [{{
                        data: [pos.nouns, pos.verbs, pos.adjectives, pos.adverbs, pos.pronouns, pos.function_other],
                        backgroundColor: ['#38bdf8', '#4ade80', '#c084fc', '#fbbf24', '#fb7185', '#94a3b8']
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            if (substanceChartInst) substanceChartInst.destroy();
            substanceChartInst = new Chart(document.getElementById('substanceDoughnutChart').getContext('2d'), {{
                type: 'doughnut',
                data: {{
                    labels: ['Substance', 'Fillers', 'Grammar'],
                    datasets: [{{
                        data: [(ling.total_words||0) * (ling.substance_ratio||0), ling.filler_count||0, (ling.total_words||0) * (1 - (ling.substance_ratio||0) - (ling.filler_ratio||0))],
                        backgroundColor: ['#4ade80', '#fb7185', '#94a3b8']
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 10 }} }} }} }}
                }}
            }});

            if (wordLengthChartInst) wordLengthChartInst.destroy();
            wordLengthChartInst = new Chart(document.getElementById('wordLengthChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: ['1-3', '4-6', '7-9', '10+'],
                    datasets: [{{
                        data: [wdist.short_1_3, wdist.medium_4_6, wdist.long_7_9, wdist.very_long_10_plus],
                        backgroundColor: ['#38bdf8', '#c084fc', '#4ade80', '#fbbf24']
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            if (wpmBoostChartInst) wpmBoostChartInst.destroy();
            wpmBoostChartInst = new Chart(document.getElementById('wpmBoostChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: ['Gross', 'Net Active'],
                    datasets: [{{
                        data: [v.gross_wpm||0, v.net_wpm||0],
                        backgroundColor: ['#94a3b8', '#4ade80']
                    }}]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});
        }}

        // Render Calligrapher's Pen Topic Density Ribbon Plot
        function renderTopicSpanScatterChart(item) {{
            if (typeof Chart === 'undefined') return;
            const canvas = document.getElementById('topicSpanScatterChart');
            if (!canvas) return;

            const tagged = item.tagged_clauses || item.tagged_sentences || [];
            if (tagged.length === 0) return;

            const buckets1s = item.timeseries_1s || [];
            const maxSec = buckets1s.length > 0 ? buckets1s[buckets1s.length - 1].s : 600;
            const pools = item.topic_pools || [];
            const mDataMap = item.multi_strength_spans || {{}};
            const colors = ['#38bdf8', '#c084fc', '#4ade80', '#fbbf24', '#fb7185', '#a78bfa'];
            const totClauses = Math.max(1, tagged.length);

            const datasets = [];
            pools.forEach((pool, pIdx) => {{
                const topicName = pool.topic;
                const pts = [];
                const sData = mDataMap[topicName] || {{}};
                const allSpans = [...(sData.tight_spans||[]), ...(sData.moderate_spans||[]), ...(sData.loose_spans||[])];

                tagged.forEach(s => {{
                    if (s.topics && s.topics.includes(topicName)) {{
                        const estSec = Math.round((s.idx / parseFloat(totClauses)) * maxSec);
                        
                        const parentSpan = allSpans.find(sp => s.idx >= sp.start_idx && s.idx <= sp.end_idx) || {{}};
                        const densVal = parentSpan.density_pct || 100.0;
                        const spanTime = parentSpan.start_time ? `Ribbon Span [${{parentSpan.start_time}} - ${{parentSpan.end_time}}]` : '';

                        pts.push({{
                            x: estSec,
                            y: pIdx,
                            text: s.text,
                            density: densVal,
                            spanTime: spanTime
                        }});
                    }}
                }});

                if (pts.length > 0) {{
                    datasets.push({{
                        label: topicName,
                        data: pts,
                        backgroundColor: colors[pIdx % colors.length],
                        borderColor: colors[pIdx % colors.length],
                        pointRadius: 4,
                        pointHoverRadius: 7
                    }});
                }}
            }});

            if (topicSpanScatterInst) topicSpanScatterInst.destroy();

            topicSpanScatterInst = new Chart(canvas.getContext('2d'), {{
                type: 'scatter',
                data: {{ datasets }},
                plugins: [calligraphersPenRibbonPlugin],
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: false,
                    customMultiSpans: mDataMap,
                    customPools: pools,
                    plugins: {{
                        legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 10 }} }} }},
                        tooltip: {{
                            callbacks: {{
                                label: (ctx) => {{
                                    const m = Math.floor(ctx.raw.x / 60);
                                    const s = ctx.raw.x % 60;
                                    const ts = `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}}`;
                                    const spanStr = ctx.raw.spanTime ? ` | ${{ctx.raw.spanTime}} (${{ctx.raw.density}}% Density)` : '';
                                    return `[${{ts}}] ${{ctx.dataset.label}}${{spanStr}}: "${{ctx.raw.text.substring(0, 45)}}..."`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{ display: true, text: 'Video Timeline Marker (Seconds)', color: '#94a3b8' }},
                            ticks: {{
                                color: '#94a3b8',
                                callback: (val) => {{
                                    const m = Math.floor(val / 60);
                                    const s = Math.floor(val % 60);
                                    return `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}}`;
                                }}
                            }},
                            grid: {{ color: '#334155' }}
                        }},
                        y: {{
                            title: {{ display: true, text: 'Calligrapher Ribbon Dynamic Topic Lanes', color: '#94a3b8' }},
                            ticks: {{
                                color: '#94a3b8',
                                stepSize: 1,
                                callback: (val) => pools[val] ? pools[val].topic.substring(0, 18) : ''
                            }},
                            grid: {{ color: '#334155' }}
                        }}
                    }}
                }}
            }});
        }}

        function renderMalleableTimelineChart(item) {{
            if (typeof Chart === 'undefined') return;
            const canvas = document.getElementById('timelineHeatmapChart');
            if (!canvas) return;

            const buckets1s = item.timeseries_1s || [];
            if (buckets1s.length === 0) return;

            const wSec = Math.max(1, currentWindowSec);
            const aggregated = [];

            for (let i = 0; i < buckets1s.length; i += wSec) {{
                const group = buckets1s.slice(i, i + wSec);
                const actualWinLen = group.length;
                const totW = group.reduce((acc, x) => acc + x.w, 0);
                const totSub = group.reduce((acc, x) => acc + x.sub, 0);
                const totChars = group.reduce((acc, x) => acc + x.c, 0);
                const totNV = group.reduce((acc, x) => acc + x.nv, 0);

                const wpm = Math.round((totW / parseFloat(actualWinLen)) * 60.0);
                const substanceRatio = totW > 0 ? Math.round((totSub / parseFloat(totW)) * 100.0) : 0;
                const avgWordLen = totW > 0 ? parseFloat((totChars / parseFloat(totW)).toFixed(1)) : 0;

                const m = Math.floor(group[0].s / 60);
                const s = group[0].s % 60;
                const tsStr = `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}}`;

                aggregated.push({{
                    timestamp: tsStr,
                    wpm: wpm,
                    substance: substanceRatio,
                    wordLen: avgWordLen,
                    nounsVerbs: totNV
                }});
            }}

            const labels = aggregated.map(a => a.timestamp);
            const datasets = [];

            if (metricToggles.wpm) {{
                datasets.push({{
                    label: 'Speaking Velocity (WPM)',
                    data: aggregated.map(a => a.wpm),
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    yAxisID: 'yWPM',
                    tension: 0.3,
                    fill: true
                }});
            }}

            if (metricToggles.substance) {{
                datasets.push({{
                    label: 'Substance Density (%)',
                    data: aggregated.map(a => a.substance),
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    yAxisID: 'yPct',
                    tension: 0.3,
                    fill: false
                }});
            }}

            if (metricToggles.wordLen) {{
                datasets.push({{
                    label: 'Word Size (Chars x10)',
                    data: aggregated.map(a => a.wordLen * 10),
                    borderColor: '#c084fc',
                    backgroundColor: 'rgba(192, 132, 252, 0.1)',
                    yAxisID: 'yPct',
                    tension: 0.3,
                    fill: false
                }});
            }}

            if (metricToggles.nounsVerbs) {{
                datasets.push({{
                    label: 'Nouns & Verbs Density',
                    data: aggregated.map(a => a.nounsVerbs),
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.1)',
                    yAxisID: 'yWPM',
                    tension: 0.3,
                    fill: false
                }});
            }}

            if (heatmapChartInst) heatmapChartInst.destroy();

            heatmapChartInst = new Chart(canvas.getContext('2d'), {{
                type: 'line',
                data: {{ labels, datasets }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 11 }} }} }},
                        tooltip: {{
                            callbacks: {{
                                title: (items) => `Timeline Marker: ${{items[0].label}} (${{currentWindowSec}}s Gradient Window)`
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }},
                            grid: {{ color: '#334155' }}
                        }},
                        yWPM: {{
                            type: 'linear',
                            position: 'left',
                            title: {{ display: true, text: 'WPM / Count', color: '#38bdf8' }},
                            ticks: {{ color: '#38bdf8' }},
                            grid: {{ color: '#334155' }}
                        }},
                        yPct: {{
                            type: 'linear',
                            position: 'right',
                            title: {{ display: true, text: 'Substance % / Size', color: '#4ade80' }},
                            ticks: {{ color: '#4ade80' }},
                            grid: {{ drawOnChartArea: false }}
                        }}
                    }}
                }}
            }});
        }}

        function copyMarkdown() {{
            const idx = hydratedVideos.findIndex(v => v.id === activeHydratedId);
            const item = hydratedVideos[idx >= 0 ? idx : 0];
            if (!item) return;
            let textToCopy = '';
            if (currentLayer === 2) {{
                const tagged = item.tagged_clauses || item.tagged_sentences || [];
                textToCopy = `# ${{item.title}}\\n**Channel:** ${{item.channel}} (${{item.handle}}) | **Duration:** ${{item.duration}}\\n**URL:** ${{item.url}}\\n\\n## Topic Tagged Clauses View\\n` + tagged.map(s => `[${{(s.topics||[]).join(', ')}}] ${{s.text}}`).join('\\n');
            }} else if (currentLayer === 0.5) {{
                const clauses = item.punct_clauses || item.punct_sentences || [];
                textToCopy = `# ${{item.title}}\\n**Channel:** ${{item.channel}} (${{item.handle}}) | **Duration:** ${{item.duration}}\\n**URL:** ${{item.url}}\\n\\n## Punctuation Clauses (. ! ? / Pauses)\\n` + clauses.join('\\n');
            }} else {{
                textToCopy = `# ${{item.title}}\\n**Channel:** ${{item.channel}} (${{item.handle}}) | **Duration:** ${{item.duration}}\\n**URL:** ${{item.url}}\\n\\n## Timestamped Raw Captions\\n` + item.formatted_md_lines.join('\\n');
            }}
            
            navigator.clipboard.writeText(textToCopy);
            
            const btn = document.getElementById('copyBtn');
            btn.innerText = '✓ Copied!';
            setTimeout(() => {{ btn.innerText = '📋 Copy View Text'; }}, 2000);
        }}

        function renderGranularityTable(list) {{
            const tbody = document.getElementById('granularityTableBody');
            tbody.innerHTML = '';
            list.forEach(g => {{
                const cCount = g.clauses || g.sentences || 0;
                const wpc = g.words_per_clause || g.words_per_sentence || 0;
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${{g.channel}}</strong></td>
                    <td>${{g.title}}</td>
                    <td>${{g.duration_formatted}}</td>
                    <td style="color:var(--accent-blue);">${{g.chars.toLocaleString()}}</td>
                    <td style="color:var(--accent-purple);">${{g.words.toLocaleString()}}</td>
                    <td style="color:var(--accent-green);">${{cCount.toLocaleString()}}</td>
                    <td><strong>${{g.wpm}} WPM</strong></td>
                    <td>${{wpc}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        document.getElementById('gSearchInput').addEventListener('input', (e) => {{
            const q = e.target.value.toLowerCase();
            const filtered = granularityData.filter(g => g.title.toLowerCase().includes(q) || g.channel.toLowerCase().includes(q));
            renderGranularityTable(filtered);
        }});

        function initGranularityCharts() {{
            if (typeof Chart === 'undefined') return;

            const sample = granularityData.slice(0, 15);

            new Chart(document.getElementById('velocityChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: sample.map(g => g.channel),
                    datasets: [
                        {{ label: 'Speaking Rate (Words / Min)', data: sample.map(g => g.wpm), backgroundColor: '#c084fc' }},
                        {{ label: 'Character Speed (Chars / Sec x10)', data: sample.map(g => g.cps * 10), backgroundColor: '#38bdf8' }}
                    ]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            new Chart(document.getElementById('volumeChart').getContext('2d'), {{
                type: 'bar',
                data: {{
                    labels: sample.map(g => g.channel),
                    datasets: [
                        {{ label: 'Total Words', data: sample.map(g => g.words), backgroundColor: '#38bdf8' }},
                        {{ label: 'Clauses (. ! ? / Pauses) x10', data: sample.map(g => (g.clauses || g.sentences || 0) * 10), backgroundColor: '#4ade80' }}
                    ]
                }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});
        }}

        function renderQueueTable() {{
            const tbody = document.getElementById('queueTableBody');
            tbody.innerHTML = '';
            queueSample.forEach(v => {{
                const tr = document.createElement('tr');
                const badge = v.is_free_covered ? `<span class="badge badge-free">🎁 100% Free</span>` : `<span class="badge badge-sub">Paid ($0.002)</span>`;
                tr.innerHTML = `
                    <td><strong>#${{v.sequence_step}}</strong></td>
                    <td><strong>${{v.title}}</strong></td>
                    <td>${{v.channel_name}}</td>
                    <td>${{v.duration_min}} min</td>
                    <td>${{v.cum_hours}} hrs</td>
                    <td>+$0.002 (Cum: $${{v.cum_cost_usd.toFixed(2)}})</td>
                    <td>${{badge}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        renderQueueTable();

        const channelsSortedByROI = [...channelsData].sort((a, b) => b.cost_efficiency_score - a.cost_efficiency_score);

        (function calcFreeCovered() {{
            let accum = 0;
            for (const c of channelsSortedByROI) {{
                if (accum + c.transcript_cost_usd <= FREE_TIER_CREDITS) {{
                    accum += c.transcript_cost_usd;
                    freeCoveredNames.add(c.name);
                }}
            }}
        }})();

        function updateBudgetSelection(grossBudget) {{
            let currentCost = 0;
            let totalHoursUnlocked = 0;
            let totalVideosUnlocked = 0;
            selectedChannelNames.clear();

            for (const c of channelsSortedByROI) {{
                if (currentCost + c.transcript_cost_usd <= grossBudget) {{
                    currentCost += c.transcript_cost_usd;
                    totalHoursUnlocked += c.total_hours;
                    totalVideosUnlocked += c.video_count;
                    selectedChannelNames.add(c.name);
                }}
            }}

            const freeApplied = Math.min(currentCost, FREE_TIER_CREDITS);
            const netOutofPocket = Math.max(0, currentCost - freeApplied);
            const netRatio = netOutofPocket > 0 ? (totalHoursUnlocked / netOutofPocket).toFixed(1) : "∞ (100% Free)";

            document.getElementById('resGrossBudget').innerText = `$${{grossBudget.toFixed(2)}}`;
            document.getElementById('resFreeApplied').innerText = `$${{freeApplied.toFixed(2)}} ($0 out-of-pocket)`;
            document.getElementById('resNetCost').innerText = `$${{netOutofPocket.toFixed(2)}}`;
            document.getElementById('resChannels').innerText = `${{selectedChannelNames.size}} / ${{channelsData.length}}`;
            document.getElementById('resHours').innerText = `${{totalHoursUnlocked.toLocaleString(undefined, {{maximumFractionDigits: 1}})}} hrs`;
            document.getElementById('resRatio').innerText = `${{netRatio}} hrs/$`;

            filterData();
            updateScatterChart();
        }}

        function renderTable(data) {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            data.forEach(c => {{
                const isSelected = selectedChannelNames.has(c.name);
                const isFreeCovered = freeCoveredNames.has(c.name);

                const tr = document.createElement('tr');
                if (isSelected) tr.classList.add('selected-row');

                const badgeClass = c.category === 'Subscribed' ? 'badge-sub' : 'badge-tangential';
                let statusBadge = '';
                if (isSelected) {{
                    statusBadge = isFreeCovered ? `<span class="badge badge-free">🎁 100% Free</span> ` : `<span class="badge badge-selected">✓ Selected</span> `;
                }}

                tr.innerHTML = `
                    <td>${{statusBadge}}<span class="badge ${{badgeClass}}">${{c.category}}</span></td>
                    <td><strong><a href="${{c.url}}" target="_blank" style="color:#f8fafc;text-decoration:none;">${{c.name}}</a></strong></td>
                    <td style="color:#94a3b8;">${{c.handle}}</td>
                    <td>${{c.video_count.toLocaleString()}}</td>
                    <td>${{c.playlists_count}}</td>
                    <td>${{c.avg_duration_min}} m</td>
                    <td>${{c.total_hours.toLocaleString()}} hrs</td>
                    <td style="color:#4ade80;">$${{c.transcript_cost_usd.toFixed(2)}}</td>
                    <td style="color:#38bdf8;"><strong>${{c.cost_efficiency_score}}</strong></td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        const budgetSlider = document.getElementById('budgetSlider');
        const budgetInput = document.getElementById('budgetInput');

        budgetSlider.addEventListener('input', (e) => {{
            const val = parseFloat(e.target.value);
            budgetInput.value = val;
            updateBudgetSelection(val);
        }});

        budgetInput.addEventListener('input', (e) => {{
            const val = parseFloat(e.target.value) || 0;
            budgetSlider.value = val;
            updateBudgetSelection(val);
        }});

        document.getElementById('searchInput').addEventListener('input', filterData);
        document.getElementById('categoryFilter').addEventListener('change', filterData);

        function filterData() {{
            const q = document.getElementById('searchInput').value.toLowerCase();
            const cat = document.getElementById('categoryFilter').value;
            const filtered = channelsData.filter(c => {{
                const matchesQ = c.name.toLowerCase().includes(q) || c.handle.toLowerCase().includes(q);
                let matchesCat = true;
                if (cat === 'SELECTED_ONLY') matchesCat = selectedChannelNames.has(c.name);
                else if (cat === 'FREE_COVERED') matchesCat = freeCoveredNames.has(c.name);
                else if (cat !== 'ALL') matchesCat = c.category === cat;

                return matchesQ && matchesCat;
            }});
            renderTable(filtered);
        }}

        if (typeof Chart !== 'undefined') {{
            const costCtx = document.getElementById('costGraphChart').getContext('2d');
            const costDatasets = Object.keys(graphData).map((name, idx) => {{
                const colors = ['#38bdf8', '#c084fc', '#4ade80', '#fbbf24', '#fb7185', '#a78bfa', '#34d399', '#f472b6'];
                const pts = graphData[name];
                return {{
                    label: name,
                    data: pts.map(p => ({{ x: p.video_num, y: p.cost }})),
                    borderColor: colors[idx % colors.length],
                    backgroundColor: colors[idx % colors.length],
                    fill: false,
                    tension: 0.1
                }};
            }});

            new Chart(costCtx, {{
                type: 'line',
                data: {{ datasets: costDatasets }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{
                        legend: {{ labels: {{ color: '#94a3b8' }} }}
                    }},
                    scales: {{
                        x: {{
                            type: 'linear',
                            title: {{ display: true, text: 'Sequential Videos Uploaded (N)', color: '#94a3b8' }},
                            ticks: {{ color: '#94a3b8' }},
                            grid: {{ color: '#334155' }}
                        }},
                        y: {{
                            title: {{ display: true, text: 'Cumulative Transcript Scraping Cost ($)', color: '#94a3b8' }},
                            ticks: {{ color: '#94a3b8' }},
                            grid: {{ color: '#334155' }}
                        }}
                    }}
                }}
            }});
        }}

        function initScatterChart() {{
            if (typeof Chart === 'undefined') return;
            const scatterCtx = document.getElementById('roiScatterChart').getContext('2d');
            scatterChartInstance = new Chart(scatterCtx, {{
                type: 'scatter',
                data: {{ datasets: [] }},
                options: {{
                    responsive: true,
                    animation: false,
                    plugins: {{
                        legend: {{ labels: {{ color: '#94a3b8' }} }},
                        tooltip: {{
                            callbacks: {{
                                label: (ctx) => `${{ctx.raw.name}}: ${{ctx.raw.x}} videos, avg ${{ctx.raw.y}} min ($${{ctx.raw.cost}})`
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{ display: true, text: 'Total Video Count (Cost Proxy)', color: '#94a3b8' }},
                            ticks: {{ color: '#94a3b8' }},
                            grid: {{ color: '#334155' }}
                        }},
                        y: {{
                            title: {{ display: true, text: 'Avg Video Duration (Minutes)', color: '#94a3b8' }},
                            ticks: {{ color: '#94a3b8' }},
                            grid: {{ color: '#334155' }}
                        }}
                    }}
                }}
            }});
            updateScatterChart();
        }}

        function updateScatterChart() {{
            if (!scatterChartInstance) return;
            const freePts = channelsData.filter(c => freeCoveredNames.has(c.name) && selectedChannelNames.has(c.name)).map(c => ({{ x: c.video_count, y: c.avg_duration_min, name: c.name, cost: c.transcript_cost_usd }}));
            const paidSelectedPts = channelsData.filter(c => !freeCoveredNames.has(c.name) && selectedChannelNames.has(c.name)).map(c => ({{ x: c.video_count, y: c.avg_duration_min, name: c.name, cost: c.transcript_cost_usd }}));
            const unselectedPts = channelsData.filter(c => !selectedChannelNames.has(c.name)).map(c => ({{ x: c.video_count, y: c.avg_duration_min, name: c.name, cost: c.transcript_cost_usd }}));

            scatterChartInstance.data.datasets = [
                {{
                    label: '🎁 100% Free Covered',
                    data: freePts,
                    backgroundColor: '#fbbf24',
                    pointRadius: 6
                }},
                {{
                    label: '✓ Paid Selected',
                    data: paidSelectedPts,
                    backgroundColor: '#4ade80',
                    pointRadius: 6
                }},
                {{
                    label: 'Unselected',
                    data: unselectedPts,
                    backgroundColor: '#475569',
                    pointRadius: 4
                }}
            ];
            scatterChartInstance.update();
        }}

        initScatterChart();
        updateBudgetSelection(20);
        sortViewerList('title_asc');
    </script>
</body>
</html>
"""

    with open(out_path, 'w') as f:
        f.write(html_content)

    print(f"Successfully generated dashboard with Drill-Down Channel Topic Chart at {out_path}")

if __name__ == '__main__':
    build_dashboard()
