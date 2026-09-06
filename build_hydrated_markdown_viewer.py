import os, json, re

SWEET_SPOT_TOPIC_TAXONOMY = {
    # Hardware & Electronics Repair
    'Console Hardware & Components': ['switch', 'oled', 'console', 'nintendo', 'joycon', 'dock', 'screen', 'board', 'battery', 'ps5', 'xbox'],
    'Diagnostics & Liquid Repair': ['liquid', 'damage', 'faulty', 'repair', 'soldering', 'chip', 'port', 'diode', 'fuse', 'resistor', 'voltage', 'power', 'tampered', 'corrosion', 'fix'],
    'eBay Sourcing & Profit Margins': ['ebay', 'profit', 'loss', 'buy', 'sell', 'cost', 'price', 'pound', 'pounds', 'dollar', 'dollars', 'listing', 'margin', 'deal', 'bargain', 'value'],

    # AI, Computing & Software
    'AI, LLMs & Neural Models': ['ai', 'model', 'llm', 'gemini', 'gpt', 'learning', 'learn', 'rag', 'agent', 'tokens', 'embedding', 'weights', 'neural', 'prompt', 'prompts'],
    'Software Architecture & Code': ['code', 'coding', 'function', 'class', 'method', 'api', 'library', 'script', 'python', 'javascript', 'rust', 'c++', 'go', 'bug', 'debug', 'compiler', 'build', 'framework', 'syntax'],
    'Operating Systems & Dev Tools': ['linux', 'distro', 'ubuntu', 'kernel', 'terminal', 'shell', 'os', 'command', 'bash', 'editor', 'git', 'repo', 'system'],
    'Performance & Benchmarks': ['speed', 'performance', 'fast', 'slow', 'benchmark', 'optimize', 'optimization', 'latency', 'throughput', 'wpm', 'fps', 'ms', 'cache', 'boost', 'accelerate'],

    # Esports & Creator Content
    'VCT Match Strategy & Rounds': ['vct', 'krx', 'ge', 'match', 'round', 'clutch', 'kill', 'valorant', 'game', 'gaming', 'stage', 'team', 'tournament', 'bracket', 'map'],
    'Streamer Reactions & Commentary': ['streamer', 'react', 'reaction', 'clip', 'chat', 'twitch', 'youtube', 'viewers', 'commentary', 'creator', 'watch', 'laugh'],

    # Science, Neuroscience & Design
    'Neuroscience & Home Design': ['neuroscience', 'brain', 'home', 'space', 'feeling', 'design', 'architecture', 'environment', 'room', 'comfort', 'sensory', 'psychology'],
    'Productivity & Knowledge Work': ['learning', 'study', 'workflow', 'note', 'obsidian', 'second brain', 'reading', 'focus', 'memory', 'habit', 'routine', 'system']
}

MACRO_CATEGORIES = {
    'Hardware & Electronics Repair': ['Console Hardware & Components', 'Diagnostics & Liquid Repair', 'eBay Sourcing & Profit Margins'],
    'AI, Computing & Software': ['AI, LLMs & Neural Models', 'Software Architecture & Code', 'Operating Systems & Dev Tools', 'Performance & Benchmarks'],
    'Esports & Creator Content': ['VCT Match Strategy & Rounds', 'Streamer Reactions & Commentary'],
    'Science, Brain & Design': ['Neuroscience & Home Design', 'Productivity & Knowledge Work']
}

# Organic Topic & Clause Graph Break Point Engine
def detect_organic_topic_break_points(tagged_clauses, multi_spans, timeseries_1s, max_sec):
    if not tagged_clauses: return [], []
    tot_clauses = max(1, len(tagged_clauses))
    
    raw_shifts = []
    prev_topic = None
    
    for idx, c in enumerate(tagged_clauses):
        topics = c.get('topics', [])
        curr_topic = topics[0] if topics else None
        
        if curr_topic and curr_topic != prev_topic and prev_topic is not None:
            sec = round((idx / float(tot_clauses)) * max_sec)
            m, s = divmod(sec, 60)
            raw_shifts.append({
                'idx': idx,
                'sec': sec,
                'timestamp': f'{m:02d}:{s:02d}',
                'from_topic': prev_topic,
                'to_topic': curr_topic,
                'reason': f'Topic Shift: [{prev_topic}] → [{curr_topic}]',
                'snippet': c['text'][:65].strip('.,!?') + '...'
            })
        if curr_topic:
            prev_topic = curr_topic
            
    l1_bps = []
    for bp in raw_shifts:
        if not l1_bps or (bp['sec'] - l1_bps[-1]['sec']) >= 45:
            l1_bps.append(bp)
            
    sections = []
    curr_start_sec = 0
    curr_start_time = '00:00'
    curr_snippet = tagged_clauses[0]['text'][:60].strip('.,!?') + '...' if tagged_clauses else 'Intro'
    curr_topic = tagged_clauses[0]['topics'][0] if (tagged_clauses and tagged_clauses[0].get('topics')) else 'General'
    
    for i, bp in enumerate(l1_bps):
        m_e, s_e = divmod(bp['sec'], 60)
        end_time = f'{m_e:02d}:{s_e:02d}'
        sections.append({
            'section_num': i + 1,
            'title': f'Section {i + 1}: {curr_snippet}',
            'dominant_topic': curr_topic,
            'start_sec': curr_start_sec,
            'end_sec': bp['sec'],
            'start_time': curr_start_time,
            'end_time': end_time,
            'break_reason': bp['reason']
        })
        curr_start_sec = bp['sec']
        curr_start_time = end_time
        curr_snippet = bp['snippet']
        curr_topic = bp['to_topic']
        
    if curr_start_sec < max_sec:
        m_e, s_e = divmod(max_sec, 60)
        sections.append({
            'section_num': len(sections) + 1,
            'title': f'Section {len(sections) + 1}: {curr_snippet}',
            'dominant_topic': curr_topic,
            'start_sec': curr_start_sec,
            'end_sec': max_sec,
            'start_time': curr_start_time,
            'end_time': f'{m_e:02d}:{s_e:02d}',
            'break_reason': 'Video Conclusion'
        })
        
    return l1_bps, sections

# Multi-Tier Span Strength Density Engine
def compute_multi_strength_topic_spans(tagged_clauses, max_sec):
    tot_clauses = max(1, len(tagged_clauses))
    topic_indices = {}
    for item in tagged_clauses:
        idx = item['idx']
        for t in item['topics']:
            if t not in topic_indices:
                topic_indices[t] = []
            topic_indices[t].append(idx)

    hierarchical_map = {}
    for t_name, indices in topic_indices.items():
        if not indices or len(indices) < 2:
            hierarchical_map[t_name] = {'tight_spans': [], 'moderate_spans': [], 'loose_spans': []}
            continue

        def group_by_gap(idxs, max_gap):
            raw = []
            curr = [idxs[0]]
            for i in range(1, len(idxs)):
                if idxs[i] - idxs[i-1] <= max_gap:
                    curr.append(idxs[i])
                else:
                    if len(curr) >= 2: raw.append(curr)
                    curr = [idxs[i]]
            if len(curr) >= 2: raw.append(curr)
            return raw

        tight_raw = group_by_gap(indices, 2)
        mod_raw = group_by_gap(indices, 5)
        loose_raw = group_by_gap(indices, 10)

        def build_span_objs(raw_groups, tier_name):
            res = []
            for s in raw_groups:
                start_i, end_i = s[0], s[-1]
                match_c = len(s)
                win_len = (end_i - start_i) + 1
                dens = round((match_c / float(win_len)) * 100.0, 1)
                start_sec = round((start_i / float(tot_clauses)) * max_sec)
                end_sec = round((end_i / float(tot_clauses)) * max_sec)
                m_s, s_s = divmod(start_sec, 60)
                m_e, s_e = divmod(end_sec, 60)

                if dens >= 70.0:
                    opacity_hex, shade_label = 'AA', 'Tight (High Density)'
                elif dens >= 40.0:
                    opacity_hex, shade_label = '44', 'Moderate Density'
                else:
                    opacity_hex, shade_label = '18', 'Loose / Soft Density'

                res.append({
                    'tier': tier_name,
                    'shade_label': shade_label,
                    'opacity_hex': opacity_hex,
                    'start_idx': start_i, 'end_idx': end_i,
                    'match_count': match_c, 'window_len': win_len,
                    'density_pct': dens,
                    'start_sec': start_sec, 'end_sec': end_sec,
                    'start_time': f'{m_s:02d}:{s_s:02d}', 'end_time': f'{m_e:02d}:{s_e:02d}'
                })
            return res

        hierarchical_map[t_name] = {
            'tight_spans': build_span_objs(tight_raw, 'Tight'),
            'moderate_spans': build_span_objs(mod_raw, 'Moderate'),
            'loose_spans': build_span_objs(loose_raw, 'Loose')
        }

    return hierarchical_map

def analyze_and_tag_sweet_spot_topics(clauses, max_sec):
    tot_clauses = max(1, len(clauses))
    video_topic_counts = {}
    clause_tags_raw = []

    for c_idx, c_text in enumerate(clauses):
        c_lower = c_text.lower()
        matched = []
        for t_name, keywords in SWEET_SPOT_TOPIC_TAXONOMY.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', c_lower) for kw in keywords):
                matched.append(t_name)
                video_topic_counts[t_name] = video_topic_counts.get(t_name, 0) + 1
        clause_tags_raw.append(matched)

    active_topics = [t for t, count in sorted(video_topic_counts.items(), key=lambda x: x[1], reverse=True)[:5] if count >= 2]
    
    if len(active_topics) < 2 and video_topic_counts:
        active_topics = [t for t, count in sorted(video_topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]]

    tagged_clauses = []
    pool_counts = {}
    
    for c_idx, c_text in enumerate(clauses):
        filtered_t = [t for t in clause_tags_raw[c_idx] if t in active_topics]
        tagged_clauses.append({
            'idx': c_idx,
            'text': c_text,
            'topics': filtered_t
        })
        for t in filtered_t:
            if t not in pool_counts:
                pool_counts[t] = {'topic': t, 'clause_count': 0, 'word_count': 0, 'indices': []}
            pool_counts[t]['clause_count'] += 1
            pool_counts[t]['word_count'] += len(c_text.split())
            pool_counts[t]['indices'].append(c_idx)

    multi_spans = compute_multi_strength_topic_spans(tagged_clauses, max_sec)

    topic_pools = []
    for t, data in sorted(pool_counts.items(), key=lambda x: x[1]['clause_count'], reverse=True):
        data['pct'] = round((data['clause_count'] / tot_clauses) * 100.0, 1)
        s_data = multi_spans.get(t, {})
        tight_s = s_data.get('tight_spans', [])
        mod_s = s_data.get('moderate_spans', [])
        loose_s = s_data.get('loose_spans', [])
        
        data['tight_span_count'] = len(tight_s)
        data['moderate_span_count'] = len(mod_s)
        data['loose_span_count'] = len(loose_s)
        data['max_density_pct'] = max([s['density_pct'] for s in tight_s + mod_s + loose_s], default=0.0)
        topic_pools.append(data)

    return tagged_clauses, topic_pools, multi_spans

def segment_into_clauses(raw_text):
    clause_triggers = {
        'so', 'because', 'although', 'however', 'furthermore', 'anyway', 'otherwise',
        'instead', 'meanwhile', 'now', 'first', 'second', 'next', 'finally',
        'saying', 'well', 'right', 'look', 'listen', 'like', 'but', 'and'
    }
    
    tokens = raw_text.split()
    clauses = []
    curr_clause = []
    
    for i, tok in enumerate(tokens):
        curr_clause.append(tok)
        has_terminal_punct = bool(re.search(r'[.!?]$', tok))
        next_tok = tokens[i+1].lower().strip('.,!?\"\'') if i+1 < len(tokens) else ''
        
        if has_terminal_punct:
            clauses.append(' '.join(curr_clause))
            curr_clause = []
        elif len(curr_clause) >= 12 and next_tok in clause_triggers:
            clauses.append(' '.join(curr_clause))
            curr_clause = []
        elif len(curr_clause) >= 22:
            clauses.append(' '.join(curr_clause))
            curr_clause = []

    if curr_clause:
        clauses.append(' '.join(curr_clause))
        
    return clauses

def get_best_complete_text_and_segments(pkt):
    raw_segs = pkt.get('raw_segments', [])
    transcript_text = pkt.get('transcript', '').strip()
    
    words_from_segs = []
    if raw_segs and isinstance(raw_segs, list):
        for seg in raw_segs:
            txt = seg.get('text', '').strip()
            if not txt: continue
            t_start = seg.get('offset', 0) / 1000.0 if seg.get('offset', 0) > 1000 else seg.get('offset', 0)
            t_dur = seg.get('duration', 0) / 1000.0 if seg.get('duration', 0) > 1000 else seg.get('duration', 0)
            tokens = txt.split()
            tok_count = max(1, len(tokens))
            step_dt = max(0.1, t_dur / tok_count)
            for idx, tok in enumerate(tokens):
                words_from_segs.append({'word': tok, 'ts': t_start + (idx * step_dt)})

    seg_full_line = ' '.join(w['word'] for w in words_from_segs)

    if len(transcript_text) > len(seg_full_line) * 1.2:
        best_line = transcript_text
        tokens = transcript_text.split()
        dur_est = float(pkt.get('duration_seconds', 0) or 1800.0)
        dt_per_word = max(0.1, dur_est / max(1, len(tokens)))
        final_words_ts = [{'word': tok, 'ts': idx * dt_per_word} for idx, tok in enumerate(tokens)]
    else:
        best_line = seg_full_line if seg_full_line else transcript_text
        final_words_ts = words_from_segs if words_from_segs else [{'word': tok, 'ts': idx * 0.5} for idx, tok in enumerate(transcript_text.split())]

    punct_clauses = segment_into_clauses(best_line)
    max_sec = int(final_words_ts[-1]['ts']) + 1 if final_words_ts else 600

    tagged_clauses, topic_pools, multi_strength_spans = analyze_and_tag_sweet_spot_topics(punct_clauses, max_sec)
    organic_break_points, organic_sections = detect_organic_topic_break_points(tagged_clauses, multi_strength_spans, [], max_sec)

    fillers_set = {'uh', 'um', 'like', 'you know', 'mean', 'so', 'actually', 'basically', 'right', 'well'}
    buckets_1s_raw = [{'sec': s, 'words': []} for s in range(max_sec)]

    for w_obj in final_words_ts:
        s_idx = min(max_sec - 1, max(0, int(w_obj['ts'])))
        buckets_1s_raw[s_idx]['words'].append(w_obj['word'])

    timeseries_1s = []
    for b in buckets_1s_raw:
        words = b['words']
        w_count = len(words)
        substance_w = [w for w in words if len(w) >= 4 and w.lower().strip('.,!?') not in fillers_set]
        char_count = sum(len(w) for w in words)
        nouns = len([w for w in words if len(w) >= 5 and w.lower().endswith(('tion', 'ment', 'ity', 'ness', 'ance', 'er', 'or', 's'))])
        verbs = len([w for w in words if w.lower().endswith(('ing', 'ed', 'ate', 'ize', 'ify'))])

        timeseries_1s.append({
            's': b['sec'],
            'w': w_count,
            'sub': len(substance_w),
            'c': char_count,
            'nv': nouns + verbs
        })

    formatted_md_lines = []
    if final_words_ts:
        curr_chunk = []
        c_start_ts = final_words_ts[0]['ts']
        for i, w_obj in enumerate(final_words_ts):
            if len(curr_chunk) == 0: c_start_ts = w_obj['ts']
            curr_chunk.append(w_obj['word'])
            if len(curr_chunk) >= 8 or i == len(final_words_ts) - 1:
                m, s = divmod(int(c_start_ts), 60)
                formatted_md_lines.append(f"{m:02d}:{s:02d} {' '.join(curr_chunk)}")
                curr_chunk = []

    return best_line, punct_clauses, tagged_clauses, topic_pools, multi_strength_spans, organic_break_points, organic_sections, timeseries_1s, formatted_md_lines

# Build Channel Aggregate Database Engine
def generate_channel_aggregate_database(hydrated_items):
    channel_db = {}
    for v in hydrated_items:
        ch = v.get('channel', 'Unknown')
        if ch not in channel_db:
            channel_db[ch] = {
                'channel_name': ch,
                'handle': v.get('handle', ''),
                'video_count': 0,
                'total_words': 0,
                'total_clauses': 0,
                'topic_counts': {},
                'videos': []
            }
        
        entry = channel_db[ch]
        entry['video_count'] += 1
        words = len(v.get('continuous_full_line', '').split())
        entry['total_words'] += words
        entry['total_clauses'] += len(v.get('punct_clauses', v.get('punct_sentences', [])))
        entry['videos'].append({
            'id': v.get('id'),
            'title': v.get('title'),
            'duration': str(v.get('duration', '')),
            'url': v.get('url'),
            'words': words
        })
        
        for pool in v.get('topic_pools', []):
            t_name = pool['topic']
            c_cnt = pool.get('clause_count', pool.get('sentence_count', 0))
            entry['topic_counts'][t_name] = entry['topic_counts'].get(t_name, 0) + c_cnt

    return channel_db

# Build Global Topic & Category Taxonomy Engine
def generate_global_topic_taxonomy(hydrated_items):
    global_topic_db = {}
    for v in hydrated_items:
        ch = v.get('channel', 'Unknown')
        for pool in v.get('topic_pools', []):
            t_name = pool['topic']
            c_cnt = pool.get('clause_count', pool.get('sentence_count', 0))
            if t_name not in global_topic_db:
                cat_name = 'General / Uncategorized'
                for c_name, t_list in MACRO_CATEGORIES.items():
                    if t_name in t_list:
                        cat_name = c_name
                        break
                global_topic_db[t_name] = {
                    'topic': t_name,
                    'category': cat_name,
                    'total_clauses': 0,
                    'total_words': 0,
                    'channels_covered': set(),
                    'videos_covered': 0
                }
            
            g_entry = global_topic_db[t_name]
            g_entry['total_clauses'] += c_cnt
            g_entry['total_words'] += pool['word_count']
            g_entry['channels_covered'].add(ch)
            g_entry['videos_covered'] += 1

    for t_name, data in global_topic_db.items():
        data['channels_covered'] = list(data['channels_covered'])
        data['channel_count'] = len(data['channels_covered'])

    return global_topic_db

def generate_granularity_analytics_dataset(hydrated_items):
    granularity_list = []
    for v in hydrated_items:
        full_text = v.get('continuous_full_line', '')
        words_arr = full_text.split()
        char_count = len(full_text)
        word_count = len(words_arr)
        clauses_arr = v.get('punct_clauses', v.get('punct_sentences', []))
        clause_count = max(1, len(clauses_arr))
        
        dur_val = v.get('duration', '00:00')
        dur_str = str(dur_val)
        dur_sec = 1800
        if ':' in dur_str:
            parts = dur_str.split(':')
            if len(parts) == 3: dur_sec = int(float(parts[0]))*3600 + int(float(parts[1]))*60 + int(float(parts[2]))
            elif len(parts) == 2: dur_sec = int(float(parts[0]))*60 + int(float(parts[1]))
        else:
            try:
                dur_sec = int(float(dur_str) * 60)
            except Exception:
                dur_sec = 1800

        wpm = round((word_count / float(max(1, dur_sec))) * 60.0, 1)
        cps = round(char_count / float(max(1, dur_sec)), 1)
        words_per_clause = round(word_count / float(clause_count), 1)

        granularity_list.append({
            'id': v['id'],
            'title': v['title'],
            'channel': v['channel'],
            'duration_formatted': dur_str if ':' in dur_str else f"{dur_val} min",
            'chars': char_count,
            'words': word_count,
            'clauses': clause_count,
            'wpm': wpm,
            'cps': cps,
            'words_per_clause': words_per_clause
        })
    return granularity_list

def main():
    out_dir = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    viewer_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/hydrated_viewer_dataset.json'
    ch_db_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/channel_aggregate_database.json'
    global_topic_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/global_topic_taxonomy.json'
    granularity_path = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/text_granularity_analytics_dataset.json'
    cat_path_continuous = '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/hydrated_continuous_text_stream_catalog.md'
    
    files = sorted([f for f in os.listdir(out_dir) if f.endswith('.json') and not f.startswith('step_0001_lemondefr') and not f.startswith('step_0002_lemondefr')])
    
    viewer_map = {}
    continuous_catalog_parts = ["# Hydrated YouTube Video Transcripts (Organic Topic Shift Break Points)\n\nBreak Points and Organic Sections breakdown by clauses.\n\n---\n"]

    fixed_count = 0
    for idx, f in enumerate(files, start=1):
        with open(os.path.join(out_dir, f), 'r') as pf:
            pkt = json.load(pf)
            title = pkt.get('title') or pkt.get('video_title') or f
            
            # STRICT FILTER: Skip synthetic queue placeholder files ("Essential Video #XX")
            if 'Essential Video' in title:
                continue

            ch_name = pkt.get('channel') or pkt.get('channel_name') or 'N/A'
            ch_handle = pkt.get('handle') or pkt.get('channel_handle') or ''
            duration = str(pkt.get('duration') or pkt.get('duration_minutes') or 'N/A')
            url = pkt.get('video_url') or pkt.get('url') or f"https://www.youtube.com/watch?v={pkt.get('video_id','')}"
            v_id = pkt.get('video_id') or pkt.get('id') or f
            
            best_line, punct_clauses, tagged_clauses, topic_pools, m_spans, o_bps, o_sections, ts_1s, formatted_md_lines = get_best_complete_text_and_segments(pkt)
            
            if not best_line or len(best_line.split()) < 10: continue
            fixed_count += 1
            
            md = f"### [{idx}] {title}\n"
            md += f"**Channel:** {ch_name} ({ch_handle}) | **Duration:** {duration} | **Word Count:** {len(best_line.split()):,} words | **Organic Sections:** {len(o_sections)}\n"
            md += f"**URL:** [{url}]({url})\n\n"
            md += f"#### Organic Topic Shift Sections\n"
            for sec in o_sections:
                md += f"- **[{sec['start_time']} - {sec['end_time']}] {sec['title']}** (Dominant: {sec['dominant_topic']})\n"
            md += "\n```text\n" + '\n'.join([f"[{', '.join(c['topics'])}] {c['text']}" if c['topics'] else c['text'] for c in tagged_clauses]) + "\n```\n\n---\n"
            continuous_catalog_parts.append(md)
            
            viewer_map[v_id] = {
                'id': v_id,
                'title': title,
                'channel': ch_name,
                'handle': ch_handle,
                'duration': duration,
                'url': url,
                'continuous_full_line': best_line[:500] + '...' if len(best_line) > 500 else best_line,
                'punct_clauses': punct_clauses[:5],
                'punct_sentences': punct_clauses[:5],
                'tagged_clauses': tagged_clauses[:5],
                'tagged_sentences': tagged_clauses[:5],
                'topic_pools': topic_pools,
                'multi_strength_spans': m_spans,
                'organic_break_points': o_bps,
                'organic_sections': o_sections,
                'timeseries_1s': ts_1s,
                'formatted_md_lines': formatted_md_lines[:10],
                'video_summary': pkt.get('video_summary')
            }

    hydrated_list = list(viewer_map.values())

    # Generate Channel Aggregate Database
    channel_db = generate_channel_aggregate_database(hydrated_list)
    with open(ch_db_path, 'w') as f:
        json.dump(channel_db, f, indent=2)

    # Generate Global Topic & Category Taxonomy
    global_topic_db = generate_global_topic_taxonomy(hydrated_list)
    with open(global_topic_path, 'w') as f:
        json.dump(global_topic_db, f, indent=2)

    # Generate Granularity Analytics
    granularity_list = generate_granularity_analytics_dataset(hydrated_list)
    with open(granularity_path, 'w') as f:
        json.dump(granularity_list, f, indent=2)

    with open(cat_path_continuous, 'w') as mf:
        mf.write('\n'.join(continuous_catalog_parts))

    with open(viewer_path, 'w') as jf:
        json.dump(hydrated_list, jf, indent=2)

    print(f"Successfully filtered out placeholders! Clean Real YouTube Videos: {fixed_count} across {len(channel_db)} creators!")

if __name__ == '__main__':
    main()
