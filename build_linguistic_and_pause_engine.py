import os, json, re

fillers = {'like', 'um', 'uh', 'you know', 'basically', 'literally', 'stuff', 'kind of', 'sort of', 'i mean', 'right', 'anyways', 'yeah', 'so', 'bro', 'man'}
pronouns = {'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'ours', 'theirs', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose'}
conjunctions = {'and', 'but', 'or', 'so', 'for', 'nor', 'yet', 'because', 'although', 'since', 'unless', 'while', 'whereas', 'if'}
prepositions = {'in', 'on', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'of', 'over', 'under'}
articles_aux = {'a', 'an', 'the', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'should', 'would', 'may', 'might', 'must', 'will', 'shall'}

common_verbs = {'get', 'make', 'go', 'know', 'take', 'see', 'come', 'think', 'look', 'want', 'give', 'use', 'find', 'tell', 'ask', 'work', 'seem', 'feel', 'try', 'leave', 'call', 'need', 'feel', 'become', 'put', 'mean', 'keep', 'let', 'begin', 'help', 'talk', 'turn', 'start', 'show', 'hear', 'play', 'run', 'move', 'like', 'live', 'believe', 'hold', 'bring', 'happen', 'write', 'provide', 'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak', 'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer', 'remember', 'love', 'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send', 'expect', 'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'raise', 'pass', 'sell', 'decide', 'return', 'explain', 'hope', 'develop', 'carry', 'break', 'receive', 'agree', 'support', 'hit', 'produce', 'eat', 'cover', 'catch', 'draw', 'choose'}
common_adverbs = {'very', 'really', 'just', 'too', 'also', 'now', 'always', 'here', 'there', 'where', 'when', 'why', 'how', 'then', 'so', 'out', 'up', 'only', 'well', 'quite', 'almost', 'even', 'still', 'already', 'again', 'ever', 'never', 'today', 'more', 'most', 'often', 'sometimes', 'usually', 'finally', 'actually', 'probably', 'maybe', 'together', 'away', 'back', 'fast', 'slowly', 'quickly', 'clearly', 'simply', 'completely', 'totally', 'especially', 'literally', 'basically', 'obviously'}
common_adj = {'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old', 'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same', 'able', 'best', 'better', 'worse', 'worst', 'real', 'true', 'full', 'easy', 'hard', 'clear', 'simple', 'clean', 'huge', 'tiny', 'strong', 'weak', 'free', 'sure', 'fine', 'cool', 'nice', 'bad', 'wrong', 'smart', 'dumb', 'crazy', 'main', 'deep'}

def format_time(sec):
    sec = max(0.0, float(sec))
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def analyze_linguistics(text):
    tokens = re.findall(r'\b[a-zA-Z\']+\b', text.lower())
    if not tokens:
        return {
            'total_words': 0, 'unique_words': 0, 'ttr_diversity': 0.0, 'avg_word_length': 0.0,
            'word_size_dist': {'short_1_3': 0, 'medium_4_6': 0, 'long_7_9': 0, 'very_long_10_plus': 0},
            'filler_count': 0, 'filler_ratio': 0.0, 'substance_ratio': 0.0,
            'pos_counts': {'nouns': 0, 'verbs': 0, 'adjectives': 0, 'adverbs': 0, 'pronouns': 0, 'function_other': 0}
        }
        
    total_words = len(tokens)
    unique_words = len(set(tokens))
    ttr = round(unique_words / total_words, 3)
    avg_word_length = round(sum(len(w) for w in tokens) / total_words, 2)
    
    short_words = sum(1 for w in tokens if len(w) <= 3)
    medium_words = sum(1 for w in tokens if 4 <= len(w) <= 6)
    long_words = sum(1 for w in tokens if 7 <= len(w) <= 9)
    very_long_words = sum(1 for w in tokens if len(w) >= 10)
    
    filler_count = sum(1 for w in tokens if w in fillers)
    filler_ratio = round(filler_count / total_words, 3)
    
    noun_count, verb_count, adj_count, adv_count, pronoun_count, other_count = 0, 0, 0, 0, 0, 0
    for w in tokens:
        if w in pronouns: pronoun_count += 1
        elif w in conjunctions or w in prepositions or w in articles_aux: other_count += 1
        elif w in common_verbs or w.endswith(('ing', 'ed')): verb_count += 1
        elif w in common_adverbs or w.endswith('ly'): adv_count += 1
        elif w in common_adj or w.endswith(('able', 'ible', 'al', 'ous', 'ful', 'less', 'ive')): adj_count += 1
        else: noun_count += 1
            
    content_words = noun_count + verb_count + adj_count + adv_count
    substance_ratio = round(content_words / total_words, 3)
    
    return {
        'total_words': total_words,
        'unique_words': unique_words,
        'ttr_diversity': ttr,
        'avg_word_length': avg_word_length,
        'word_size_dist': {
            'short_1_3': short_words,
            'medium_4_6': medium_words,
            'long_7_9': long_words,
            'very_long_10_plus': very_long_words
        },
        'filler_count': filler_count,
        'filler_ratio': filler_ratio,
        'substance_ratio': substance_ratio,
        'pos_counts': {
            'nouns': noun_count,
            'verbs': verb_count,
            'adjectives': adj_count,
            'adverbs': adv_count,
            'pronouns': pronoun_count,
            'function_other': other_count
        }
    }

def process_pause_punctuated_paragraphs(raw_segments, transcript_text):
    if not raw_segments or not isinstance(raw_segments, list) or len(raw_segments) < 5:
        # Fallback for plain transcript text
        paragraphs = []
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', transcript_text) if s.strip()]
        if not sentences: sentences = [transcript_text]
        curr = []
        for s in sentences:
            curr.append(s)
            txt = ' '.join(curr)
            if len(txt.split()) >= 90:
                paragraphs.append({'start_ts': '00:00', 'end_ts': '00:00', 'words': len(txt.split()), 'text': txt})
                curr = []
        if curr:
            txt = ' '.join(curr)
            paragraphs.append({'start_ts': '00:00', 'end_ts': '00:00', 'words': len(txt.split()), 'text': txt})
        return paragraphs, 600.0, 600.0

    paragraphs = []
    current_tokens = []
    net_speech_sec = 0.0
    para_start_time = 0.0
    
    for i, seg in enumerate(raw_segments):
        txt = seg.get('text', '').strip()
        if not txt: continue
        
        t_start = seg.get('offset', 0) / 1000.0 if seg.get('offset', 0) > 1000 else seg.get('offset', 0)
        dur = seg.get('duration', 2.0)
        if dur > 100: dur /= 1000.0
        
        net_speech_sec += dur
        if len(current_tokens) == 0:
            para_start_time = t_start
            
        gap = 0.0
        if i > 0:
            prev_seg = raw_segments[i-1]
            prev_start = prev_seg.get('offset', 0) / 1000.0 if prev_seg.get('offset', 0) > 1000 else prev_seg.get('offset', 0)
            prev_dur = prev_seg.get('duration', 2.0)
            if prev_dur > 100: prev_dur /= 1000.0
            gap = max(0.0, t_start - (prev_start + prev_dur))
            
        words_in_current = len(re.findall(r'\b\w+\b', ' '.join(t[0] for t in current_tokens)))
        
        if (gap >= 1.4 and words_in_current >= 30) or words_in_current >= 130:
            para_end_time = t_start
            p_text = build_para_str(current_tokens)
            w_cnt = len(re.findall(r'\b\w+\b', p_text))
            paragraphs.append({
                'start_ts': format_time(para_start_time),
                'end_ts': format_time(para_end_time),
                'words': w_cnt,
                'text': p_text
            })
            current_tokens = [(txt, 0.0)]
            para_start_time = t_start
        else:
            current_tokens.append((txt, gap))

    if current_tokens:
        last_t = raw_segments[-1].get('offset', 0) / 1000.0 if raw_segments[-1].get('offset', 0) > 1000 else raw_segments[-1].get('offset', 0)
        p_text = build_para_str(current_tokens)
        w_cnt = len(re.findall(r'\b\w+\b', p_text))
        paragraphs.append({
            'start_ts': format_time(para_start_time),
            'end_ts': format_time(last_t + 2.0),
            'words': w_cnt,
            'text': p_text
        })
        
    gross_dur_sec = max(1.0, raw_segments[-1].get('offset', 0)/1000.0 if raw_segments[-1].get('offset', 0)>1000 else raw_segments[-1].get('offset', 0))
    return paragraphs, net_speech_sec, gross_dur_sec

def build_para_str(tokens):
    res = []
    for idx, (txt, gap) in enumerate(tokens):
        if idx > 0 and 0.5 <= gap < 1.4 and not res[-1].endswith((';', '.', '!', '?')):
            res.append(';')
        res.append(txt)
    return ' '.join(res).replace(' ;', ';')

def main():
    out_dir = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    cat_path_layer3 = '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/hydrated_pause_punctuated_essay_catalog.md'
    
    files = sorted([f for f in os.listdir(out_dir) if f.endswith('.json') and not f.startswith('step_0001_lemondefr') and not f.startswith('step_0002_lemondefr')])
    
    video_analytics = []
    layer3_md_parts = ["# Hydrated YouTube Video Transcripts (Layer 3: Pause-Punctuated Essay View)\n\nThis catalog incorporates **In-Line Pause Semicolons (;)** for micro-pauses ($0.5s \\le \\Delta t < 1.4s$) and **Paragraph Breaks** for macro-pauses ($\Delta t \\ge 1.4s$). Speech speed is calculated as **Net Active Speech WPM** (excluding silence gaps).\n\n---\n"]

    for idx, f in enumerate(files, start=1):
        with open(os.path.join(out_dir, f), 'r') as pf:
            pkt = json.load(pf)
            title = pkt.get('title') or pkt.get('video_title') or f
            ch_name = pkt.get('channel') or pkt.get('channel_name') or 'N/A'
            ch_handle = pkt.get('handle') or pkt.get('channel_handle') or ''
            duration = pkt.get('duration') or pkt.get('duration_minutes') or 'N/A'
            url = pkt.get('video_url') or pkt.get('url') or f"https://www.youtube.com/watch?v={pkt.get('video_id','')}"
            v_id = pkt.get('video_id', '')
            
            transcript_txt = pkt.get('transcript', '')
            raw_segs = pkt.get('raw_segments', [])
            
            # Linguistic Analysis
            ling = analyze_linguistics(transcript_txt)
            
            # Pause Punctuation Analysis
            layer3_paras, net_sec, gross_sec = process_pause_punctuated_paragraphs(raw_segs, transcript_txt)
            
            gross_wpm = round((ling['total_words'] / max(1.0, gross_sec)) * 60.0, 1)
            net_wpm = round((ling['total_words'] / max(1.0, net_sec)) * 60.0, 1)
            pause_sec = max(0.0, gross_sec - net_sec)
            
            # Format Layer 3 MD
            formatted_l3_paras = []
            for p_num, p in enumerate(layer3_paras, start=1):
                hdr = f"[{p['start_ts']} - {p['end_ts']}] Paragraph #{p_num} ({p['words']} words)"
                formatted_l3_paras.append(f"**{hdr}**\n{p['text']}")
                
            md3 = f"### [{idx}] {title}\n"
            md3 += f"**Channel:** {ch_name} ({ch_handle}) | **Duration:** {duration} | **Gross WPM:** {gross_wpm} | **Net Active WPM:** {net_wpm} (+{round(net_wpm-gross_wpm,1)} boost)\n"
            md3 += f"**Substance Ratio:** {ling['substance_ratio']*100:.1f}% | **Filler Ratio:** {ling['filler_ratio']*100:.1f}% | **TTR Diversity:** {ling['ttr_diversity']*100:.1f}%\n"
            md3 += f"**URL:** [{url}]({url})\n\n" + '\n\n'.join(formatted_l3_paras) + "\n\n---\n"
            layer3_md_parts.append(md3)
            
            video_analytics.append({
                'id': v_id,
                'title': title,
                'channel': ch_name,
                'handle': ch_handle,
                'duration': str(duration),
                'url': url,
                'gross_duration_sec': gross_sec,
                'net_speech_sec': net_sec,
                'pause_duration_sec': pause_sec,
                'gross_wpm': gross_wpm,
                'net_wpm': net_wpm,
                'linguistics': ling,
                'layer3_paragraphs': layer3_paras
            })

    # Save Layer 3 Markdown Catalog
    with open(cat_path_layer3, 'w') as mf3:
        mf3.write('\n'.join(layer3_md_parts))

    # Save Video Linguistic Analytics Dataset
    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/video_linguistic_analytics_dataset.json', 'w') as jf:
        json.dump(video_analytics, jf, indent=2)

    print(f"Successfully processed Video-by-Video Linguistic & Pause Analytics for {len(video_analytics)} videos!")

if __name__ == '__main__':
    main()
