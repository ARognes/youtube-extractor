#!/usr/bin/env python3
"""
analyze_speech_dynamics.py

Computes mathematical speech pacing, Words Per Minute (WPM), pause patterns,
and channel pacing profiles across all 1,740 formatted YAML transcripts,
saving results to `taxonomy/speech_dynamics.yaml`.
"""

import os
import yaml
from collections import defaultdict

try:
    from yaml import CSafeDumper as Dumper, CSafeLoader as Loader
except ImportError:
    from yaml import SafeDumper as Dumper, SafeLoader as Loader

FORMATTED_DIR = "formatted_transcripts"
OUTPUT_FILE = "taxonomy/speech_dynamics.yaml"


def parse_duration_str(dur_str):
    if not dur_str:
        return 0
    parts = [int(p) for p in str(dur_str).split(':') if p.isdigit()]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 1:
        return parts[0]
    return 0


def classify_pacing_tier(wpm):
    if wpm >= 175:
        return "Rapid / High-Energy"
    elif wpm >= 135:
        return "Conversational / Balanced"
    else:
        return "Deliberate / Contemplative"


def main():
    print("🎙️  Analyzing Speech Dynamics & Pacing across formatted transcripts...")
    files = sorted([f for f in os.listdir(FORMATTED_DIR) if f.endswith('.yaml')])

    channel_stats = defaultdict(lambda: {
        'video_count': 0,
        'total_words': 0,
        'total_seconds': 0,
        'pauses_over_5s': 0,
        'max_pause_sec': 0
    })

    video_metrics = []

    for idx, f in enumerate(files, 1):
        fpath = os.path.join(FORMATTED_DIR, f)
        with open(fpath, 'r', encoding='utf-8') as fp:
            doc = yaml.load(fp, Loader=Loader)

        v_id = doc.get('video_id', '')
        title = doc.get('title', '')
        channel = doc.get('channel', 'Unknown')
        v_type = doc.get('type', 'video')
        transcript = doc.get('transcript', '')
        timestamps = doc.get('timestamps', [])
        dur_str = doc.get('duration', '00:00')

        words = transcript.split()
        word_count = len(words)
        dur_sec = parse_duration_str(dur_str)

        # Calculate pauses and gaps from timestamps
        max_pause = 0
        pause_count_5s = 0
        if len(timestamps) >= 2:
            for i in range(len(timestamps) - 1):
                gap = timestamps[i+1][1] - timestamps[i][1]
                if gap > max_pause:
                    max_pause = gap
                if gap >= 5:
                    pause_count_5s += 1

        # Effective duration in seconds
        effective_sec = dur_sec
        if effective_sec <= 0 and timestamps:
            effective_sec = timestamps[-1][1]

        wpm = round((word_count / (effective_sec / 60.0)), 1) if effective_sec > 10 else 0

        # Filter out unrealistic outliers (e.g. 0-second placeholder metadata)
        if 20 <= wpm <= 350 and effective_sec >= 30:
            channel_stats[channel]['video_count'] += 1
            channel_stats[channel]['total_words'] += word_count
            channel_stats[channel]['total_seconds'] += effective_sec
            channel_stats[channel]['pauses_over_5s'] += pause_count_5s
            if max_pause > channel_stats[channel]['max_pause_sec']:
                channel_stats[channel]['max_pause_sec'] = max_pause

            video_metrics.append({
                'video_id': v_id,
                'title': title,
                'channel': channel,
                'type': v_type,
                'word_count': word_count,
                'duration_seconds': effective_sec,
                'duration': dur_str,
                'wpm': wpm,
                'pacing_tier': classify_pacing_tier(wpm),
                'max_pause_sec': max_pause,
                'pauses_over_5s': pause_count_5s
            })

    # Compile channel profiles
    channel_profiles = {}
    for ch, stats in channel_stats.items():
        if stats['total_seconds'] >= 120 and stats['video_count'] >= 2:
            avg_wpm = round(stats['total_words'] / (stats['total_seconds'] / 60.0), 1)
            total_hours = round(stats['total_seconds'] / 3600.0, 2)
            channel_profiles[ch] = {
                'video_count': stats['video_count'],
                'total_hours_spoken': total_hours,
                'total_words': stats['total_words'],
                'avg_wpm': avg_wpm,
                'pacing_tier': classify_pacing_tier(avg_wpm),
                'avg_pauses_per_video': round(stats['pauses_over_5s'] / stats['video_count'], 1),
                'max_pause_sec': stats['max_pause_sec']
            }

    # Sort channels by WPM
    sorted_channels_by_wpm = sorted(channel_profiles.items(), key=lambda x: x[1]['avg_wpm'], reverse=True)
    fastest_creators = dict(sorted_channels_by_wpm[:10])
    most_deliberate_creators = dict(sorted_channels_by_wpm[-10:])

    # Longest spoken lectures by word count
    longest_lectures = sorted(video_metrics, key=lambda x: x['word_count'], reverse=True)[:10]

    output_data = {
        'summary': {
            'total_videos_analyzed': len(video_metrics),
            'total_channels_profiled': len(channel_profiles),
            'global_avg_wpm': round(sum(v['wpm'] for v in video_metrics) / len(video_metrics), 1) if video_metrics else 0
        },
        'rankings': {
            'fastest_speaking_channels': {k: v['avg_wpm'] for k, v in fastest_creators.items()},
            'most_deliberate_channels': {k: v['avg_wpm'] for k, v in most_deliberate_creators.items()},
            'longest_lectures_by_words': [
                {
                    'video_id': v['video_id'],
                    'title': v['title'],
                    'channel': v['channel'],
                    'word_count': v['word_count'],
                    'duration': v['duration'],
                    'wpm': v['wpm']
                }
                for v in longest_lectures
            ]
        },
        'creator_profiles': channel_profiles
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    print(f"✍️  Writing {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        yaml.dump(output_data, out_f, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=120)

    print("\n✅ Speech Dynamics & Pacing Analysis Complete!")
    print(f"   - Global Average Pacing: {output_data['summary']['global_avg_wpm']} WPM")
    print(f"   - Channels Profiled: {len(channel_profiles)}")
    print("\n⚡ Top 5 Fastest Channels:")
    for ch, wpm in list(output_data['rankings']['fastest_speaking_channels'].items())[:5]:
        print(f"   - {ch:<25} {wpm} WPM")
    print("\n🧘 Top 5 Most Deliberate Channels:")
    for ch, wpm in list(output_data['rankings']['most_deliberate_channels'].items())[:5]:
        print(f"   - {ch:<25} {wpm} WPM")


if __name__ == '__main__':
    main()
