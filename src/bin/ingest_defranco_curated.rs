use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs::{self, File};
use std::io::Write;
use std::path::Path;
use std::process::Command;
use youtube_extractor::{
    build_transcript_and_timestamps, format_duration_seconds, serialize_clean_yaml,
    FormattedTranscript, RawSegment,
};

const QUEUE_FILE: &str = "/tmp/curated_defranco_100_queue.json";
const DOWNLOADED_DIR: &str = "downloaded_transcripts";
const FORMATTED_DIR: &str = "formatted_transcripts";

#[derive(Debug, Clone, Deserialize)]
struct QueueItem {
    #[serde(rename = "videoId")]
    video_id: String,
    title: String,
    duration: String,
    #[serde(default)]
    published: String,
    #[serde(default)]
    topics: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct ArchiveJson {
    video_id: String,
    title: String,
    channel: String,
    handle: String,
    url: String,
    duration: String,
    word_count: usize,
    published: String,
    raw_segments: Vec<RawSegment>,
    topics: Vec<String>,
}

fn fetch_transcript(video_id: &str) -> Option<Vec<RawSegment>> {
    // Call python helper script with timeout
    let script = format!(
        "from youtube_transcript_api import YouTubeTranscriptApi; import json, sys; res = YouTubeTranscriptApi().fetch('{}'); print(json.dumps([{{'text': s.text, 'start': s.start, 'duration': s.duration}} for s in res]))",
        video_id
    );

    let output = Command::new("python3")
        .arg("-c")
        .arg(&script)
        .output()
        .ok()?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        if let Ok(segs) = serde_json::from_str::<Vec<RawSegment>>(&stdout) {
            if !segs.is_empty() {
                return Some(segs);
            }
        }
    }
    None
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🦀 Running High-Performance Rust Ingestion Engine for Curated DeFranco Suite...\n");

    fs::create_dir_all(DOWNLOADED_DIR)?;
    fs::create_dir_all(FORMATTED_DIR)?;

    if !Path::new(QUEUE_FILE).exists() {
        eprintln!("Error: Queue file {} not found.", QUEUE_FILE);
        std::process::exit(1);
    }

    let queue_data = fs::read_to_string(QUEUE_FILE)?;
    let queue: Vec<QueueItem> = serde_json::from_str(&queue_data)?;

    println!("📋 Loaded {} curated candidates from queue.", queue.len());

    let mut existing_vids = HashSet::new();
    if let Ok(entries) = fs::read_dir(FORMATTED_DIR) {
        for entry in entries.filter_map(|e| e.ok()) {
            let path = entry.path();
            if path.extension().map_or(false, |ext| ext == "yaml") {
                if let Ok(content) = fs::read_to_string(&path) {
                    if content.contains("channel: Philip DeFranco")
                        || content.contains("channel: 'Philip DeFranco'")
                    {
                        if let Some(vid_line) = content.lines().find(|l| l.starts_with("video_id:")) {
                            let vid = vid_line.trim_start_matches("video_id:").trim();
                            existing_vids.insert(vid.to_string());
                        }
                    }
                }
            }
        }
    }

    println!("⚡ Already ingested Philip DeFranco videos: {}", existing_vids.len());

    let mut successful = 0usize;
    let mut skipped = 0usize;
    let mut failed = 0usize;

    for (idx, item) in queue.iter().enumerate() {
        let vid = &item.video_id;
        if existing_vids.contains(vid) {
            skipped += 1;
            continue;
        }

        print!(
            "[{}/{}] Ingesting: '{}' ({}) [Topics: {}]... ",
            idx + 1,
            queue.len(),
            item.title,
            item.duration,
            item.topics.join(", ")
        );
        std::io::stdout().flush().unwrap();

        match fetch_transcript(vid) {
            Some(segments) => {
                let (full_transcript, timestamps, max_sec) = build_transcript_and_timestamps(&segments);
                let duration_fmt = format_duration_seconds(max_sec);
                let word_count = full_transcript.split_whitespace().count();

                // 1. Write Archive JSON
                let archive = ArchiveJson {
                    video_id: vid.clone(),
                    title: item.title.clone(),
                    channel: "Philip DeFranco".to_string(),
                    handle: "@PhilipDeFranco".to_string(),
                    url: format!("https://www.youtube.com/watch?v={}", vid),
                    duration: duration_fmt.clone(),
                    word_count,
                    published: item.published.clone(),
                    raw_segments: segments,
                    topics: item.topics.clone(),
                };

                let json_path = format!("{}/step_manual_{}.json", DOWNLOADED_DIR, vid);
                let mut jf = File::create(&json_path)?;
                serde_json::to_writer_pretty(&mut jf, &archive)?;

                // 2. Write Clean Formatted YAML
                let formatted_doc = FormattedTranscript {
                    video_id: vid.clone(),
                    title: item.title.clone(),
                    channel: "Philip DeFranco".to_string(),
                    handle: Some("@PhilipDeFranco".to_string()),
                    url: format!("https://www.youtube.com/watch?v={}", vid),
                    duration: duration_fmt,
                    published: Some(item.published.clone()),
                    content_type: "video".to_string(),
                    transcript: full_transcript,
                    timestamps,
                };

                let clean_yaml = serialize_clean_yaml(&formatted_doc)?;
                let yaml_path = format!("{}/step_manual_{}.yaml", FORMATTED_DIR, vid);
                let mut yf = File::create(&yaml_path)?;
                yf.write_all(clean_yaml.as_bytes())?;

                successful += 1;
                existing_vids.insert(vid.clone());

                println!("✅ ({} words, {} cues)", word_count, formatted_doc.timestamps.len());
            }
            None => {
                println!("⚠️  Unavailable, skipped.");
                failed += 1;
            }
        }
    }

    println!(
        "\n🎉 Ingestion Finished! Successfully ingested: {}, Skipped: {}, Failed: {}",
        successful, skipped, failed
    );

    Ok(())
}
