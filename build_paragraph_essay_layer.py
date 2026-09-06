import os, json, re

def format_time(sec):
    try:
        sec = float(sec)
        m, s = divmod(int(sec), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"
    except:
        return "00:00"

def parse_duration_to_seconds(dur_val):
    try:
        if isinstance(dur_val, (int, float)):
            return float(dur_val) * 60.0
        dur_str = str(dur_val).strip()
        if not dur_str or dur_str == 'N/A':
            return 600.0
        if ':' not in dur_str:
            try:
                return float(dur_str) * 60.0
            except:
                return 600.0
        parts = dur_str.split(':')
        if len(parts) == 2:
            return float(parts[0]) * 60.0 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
    except:
        pass
    return 600.0

def build_essay_paragraphs(pkt):
    raw_segments = pkt.get('raw_segments') or []
    transcript_text = pkt.get('transcript') or ''
    dur_sec = parse_duration_to_seconds(pkt.get('duration'))
    
    paragraphs = []
    discourse_markers = ('now', 'first', 'second', 'third', 'next', 'so, yeah', 'all right', 'finally', 'in conclusion', 'let\'s', 'here\'s how', 'the second problem', 'the third', 'another layer', 'for example', 'in this video', 'as you can see', 'let\'s begin', 'okay, so')

    # Path A: Raw segments with explicit timing offsets
    if raw_segments and isinstance(raw_segments, list) and len(raw_segments) > 10:
        current_para_texts = []
        para_start = 0.0
        
        for i, seg in enumerate(raw_segments):
            txt = seg.get('text', '').strip()
            if not txt:
                continue
                
            t_start = seg.get('offset', 0) / 1000.0 if seg.get('offset', 0) > 1000 else seg.get('offset', 0)
            if len(current_para_texts) == 0:
                para_start = t_start
                
            dur = seg.get('duration', 2.0)
            if dur > 100:
                dur = dur / 1000.0
                
            gap = 0.0
            if i > 0:
                prev_seg = raw_segments[i-1]
                prev_start = prev_seg.get('offset', 0) / 1000.0 if prev_seg.get('offset', 0) > 1000 else prev_seg.get('offset', 0)
                prev_dur = prev_seg.get('duration', 2.0)
                if prev_dur > 100: prev_dur /= 1000.0
                gap = max(0.0, t_start - (prev_start + prev_dur))
                
            current_para_texts.append(txt)
            combined_txt = ' '.join(current_para_texts)
            words = len(combined_txt.split())
            lower_txt = txt.lower()
            
            is_discourse = any(lower_txt.startswith(m) for m in discourse_markers)
            is_pause = gap >= 1.2
            is_target_len = words >= 70
            
            if (is_pause and words >= 35) or (is_discourse and words >= 40) or (words >= 130):
                para_end = t_start + dur
                elapsed = max(1.0, para_end - para_start)
                wps = round(words / elapsed, 1)
                cps = round(len(combined_txt) / elapsed, 1)
                
                paragraphs.append({
                    'start_ts': format_time(para_start),
                    'end_ts': format_time(para_end),
                    'word_count': words,
                    'char_count': len(combined_txt),
                    'wps': wps,
                    'cps': cps,
                    'text': combined_txt
                })
                current_para_texts = []
                
        if current_para_texts:
            combined_txt = ' '.join(current_para_texts)
            words = len(combined_txt.split())
            para_end = dur_sec
            elapsed = max(1.0, para_end - para_start)
            paragraphs.append({
                'start_ts': format_time(para_start),
                'end_ts': format_time(para_end),
                'word_count': words,
                'char_count': len(combined_txt),
                'wps': round(words / elapsed, 1),
                'cps': round(len(combined_txt) / elapsed, 1),
                'text': combined_txt
            })
        return paragraphs

    # Path B: Full transcript text sentence breakdown
    if transcript_text:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', transcript_text) if s.strip()]
        if not sentences:
            sentences = [transcript_text]
            
        sec_per_sentence = dur_sec / max(1, len(sentences))
        current_para_texts = []
        para_start = 0.0
        
        for i, sentence in enumerate(sentences):
            t_start = i * sec_per_sentence
            if len(current_para_texts) == 0:
                para_start = t_start
                
            current_para_texts.append(sentence)
            combined_txt = ' '.join(current_para_texts)
            words = len(combined_txt.split())
            lower_s = sentence.lower()
            
            is_discourse = any(lower_s.startswith(m) for m in discourse_markers)
            
            if (is_discourse and words >= 40) or (words >= 90):
                para_end = (i + 1) * sec_per_sentence
                elapsed = max(1.0, para_end - para_start)
                paragraphs.append({
                    'start_ts': format_time(para_start),
                    'end_ts': format_time(para_end),
                    'word_count': words,
                    'char_count': len(combined_txt),
                    'wps': round(words / elapsed, 1),
                    'cps': round(len(combined_txt) / elapsed, 1),
                    'text': combined_txt
                })
                current_para_texts = []
                
        if current_para_texts:
            combined_txt = ' '.join(current_para_texts)
            words = len(combined_txt.split())
            para_end = dur_sec
            elapsed = max(1.0, para_end - para_start)
            paragraphs.append({
                'start_ts': format_time(para_start),
                'end_ts': format_time(para_end),
                'word_count': words,
                'char_count': len(combined_txt),
                'wps': round(words / elapsed, 1),
                'cps': round(len(combined_txt) / elapsed, 1),
                'text': combined_txt
            })
        return paragraphs

    return []

def main():
    out_dir = '/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/downloaded_transcripts'
    cat_path = '/Users/austinrognes/.gemini/antigravity/brain/cb9f98a5-3825-4ba6-829d-56e835d72d8c/hydrated_paragraphs_essay_catalog.md'
    
    files = sorted([f for f in os.listdir(out_dir) if f.endswith('.json') and not f.startswith('step_0001_lemondefr') and not f.startswith('step_0002_lemondefr')])
    
    essay_items = []
    markdown_catalog_parts = []
    
    markdown_catalog_parts.append("# Hydrated YouTube Video Transcripts Catalog (Layer 2: Essay / Paragraph View)\n")
    markdown_catalog_parts.append("This document contains Layer 2 essay-style paragraph segmentations. Sentence pacing ratios (words/sec, chars/sec) and natural discourse pauses are used to stitch video transcripts together like a cohesive essay.\n\n---\n")

    for idx, f in enumerate(files, start=1):
        with open(os.path.join(out_dir, f), 'r') as pf:
            pkt = json.load(pf)
            title = pkt.get('title') or pkt.get('video_title') or f
            ch_name = pkt.get('channel') or pkt.get('channel_name') or 'N/A'
            ch_handle = pkt.get('handle') or pkt.get('channel_handle') or ''
            duration = pkt.get('duration') or pkt.get('duration_minutes') or 'N/A'
            url = pkt.get('video_url') or pkt.get('url') or f"https://www.youtube.com/watch?v={pkt.get('video_id','')}"
            v_id = pkt.get('video_id', '')
            
            paragraphs = build_essay_paragraphs(pkt)
            if not paragraphs:
                continue
                
            formatted_essay_lines = []
            for p_num, p in enumerate(paragraphs, start=1):
                header = f"[{p['start_ts']} - {p['end_ts']}] Paragraph #{p_num} ({p['word_count']} words | {p['wps']} words/sec | {p['cps']} chars/sec)"
                formatted_essay_lines.append(f"**{header}**\n{p['text']}\n")
                
            formatted_md = f"### [{idx}] {title}\n"
            formatted_md += f"**Channel:** {ch_name} ({ch_handle}) | **Duration:** {duration} | **Total Paragraphs:** {len(paragraphs)}\n"
            formatted_md += f"**URL:** [{url}]({url})\n\n"
            formatted_md += '\n'.join(formatted_essay_lines) + "\n---\n"
            
            markdown_catalog_parts.append(formatted_md)
            
            essay_items.append({
                'id': v_id,
                'title': title,
                'channel': ch_name,
                'handle': ch_handle,
                'duration': str(duration),
                'url': url,
                'paragraph_count': len(paragraphs),
                'paragraphs': paragraphs
            })

    # Save Layer 2 Markdown Catalog
    with open(cat_path, 'w') as mf:
        mf.write('\n'.join(markdown_catalog_parts))
        
    print(f"Generated Layer 2 Essay Catalog with {len(essay_items)} videos at {cat_path}")

    # Save Layer 2 JSON dataset
    with open('/Users/austinrognes/Documents/Projects/media-extractor/youtube-extractor/hydrated_essay_dataset.json', 'w') as jf:
        json.dump(essay_items, jf, indent=2)

if __name__ == '__main__':
    main()
