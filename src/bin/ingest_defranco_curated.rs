use regex::Regex;
use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::fs::{self, File};
use std::io::Write;
use std::path::Path;
use std::time::Duration;
use youtube_extractor::{build_transcript_and_timestamps, format_duration_seconds, serialize_clean_yaml, FormattedTranscript, RawSegment};

const API_KEY: &str = "sk_JaAysZu79sqC3_fBTneaD3FcFXuhiz1Br9a862wb8JM";
const DOWNLOADED_DIR: &str = "downloaded_transcripts";
const FORMATTED_DIR: &str = "formatted_transcripts";

#[derive(Debug, Deserialize)]
struct SearchResponse {
    content: Option<SearchContent>,
}

#[derive(Debug, Deserialize)]
struct SearchContent {
    results: Option<Vec<SearchResultVideo>>,
    continuation_token: Option<String>,
    has_more: Option<bool>,
}

#[derive(Debug, Clone, Deserialize)]
struct SearchResultVideo {
    #[serde(rename = "type")]
    item_type: Option<String>,
    #[serde(rename = "videoId")]
    video_id: Option<String>,
    title: Option<String>,
    #[serde(rename = "lengthText")]
    length_text: Option<String>,
    #[serde(rename = "viewCountText")]
    view_count_text: Option<String>,
    #[serde(rename = "publishedTimeText")]
    published_time_text: Option<String>,
    #[serde(rename = "hasCaptions")]
    has_captions: Option<bool>,
}

#[derive(Debug, Deserialize)]
struct TranscriptResponse {
    content: Option<TranscriptContent>,
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum TranscriptContent {
    Structured { transcript: Option<Vec<RawSegment>> },
    List(Vec<RawSegment>),
    StringPayload(String),
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

fn parse_duration_to_seconds(dur_str: &str) -> u32 {
    let parts: Vec<u32> = dur_str
        .split(':')
        .filter_map(|p| p.parse::<u32>().ok())
        .collect();
    match parts.len() {
        3 => parts[0] * 3600 + parts[1] * 60 + parts[2],
        2 => parts[0] * 60 + parts[1],
        1 => parts[0],
        _ => 0,
    }
}

fn call_mcp_search(
    client: &Client,
    query: Option<&str>,
    continuation: Option<&str>,
) -> Result<SearchContent, Box<dyn std::error::Error>> {
    let url = "https://transcriptapi.com/mcp";
    let mut args = serde_json::Map::new();
    if let Some(q) = query {
        args.insert("query".to_string(), serde_json::Value::String(q.to_string()));
        args.insert(
            "channel".to_string(),
            serde_json::Value::String("@PhilipDeFranco".to_string()),
        );
    }
    if let Some(c) = continuation {
        args.insert(
            "continuation".to_string(),
            serde_json::Value::String(c.to_string()),
        );
    }

    let payload = serde_json::json!({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_channel_videos",
            "arguments": args
        }
    });

    let resp = client
        .post(url)
        .header("Authorization", format!("Bearer {}", API_KEY))
        .header("Content-Type", "application/json")
        .header("Accept", "application/json, text/event-stream")
        .json(&payload)
        .send()?
        .text()?;

    for line in resp.lines() {
        let line = if line.starts_with("data: ") {
            &line[6..]
        } else {
            line
        };
        if line.trim().is_empty() {
            continue;
        }
        if let Ok(val) = serde_json::from_str::<serde_json::Value>(line) {
            if let Some(result) = val.get("result") {
                if let Ok(search_resp) = serde_json::from_value::<SearchResponse>(result.clone()) {
                    if let Some(c) = search_resp.content {
                        return Ok(c);
                    }
                }
            }
        }
    }

    Err("Failed to parse search response from MCP".into())
}

fn fetch_transcript(
    client: &Client,
    video_id: &str,
) -> Result<Vec<RawSegment>, Box<dyn std::error::Error>> {
    // 1. Direct REST endpoint on transcriptapi
    let rest_url = format!(
        "https://transcriptapi.com/api/v1/transcript?video_url={}&format=json&include_timestamp=true",
        video_id
    );

    let resp_res = client
        .get(&rest_url)
        .header("Authorization", format!("Bearer {}", API_KEY))
        .timeout(Duration::from_secs(15))
        .send();

    if let Ok(resp) = resp_res {
        if resp.status().is_success() {
            let body_str = resp.text()?;
            // Check if returned JSON with transcript
            if let Ok(val) = serde_json::from_str::<serde_json::Value>(&body_str) {
                if let Some(segs_val) = val.get("transcript").or_else(|| val.get("content")) {
                    if let Ok(segs) = serde_json::from_value::<Vec<RawSegment>>(segs_val.clone()) {
                        if !segs.is_empty() {
                            return Ok(segs);
                        }
                    }
                }
            }
        }
    }

    // 2. Fallback: MCP JSON-RPC call to get_youtube_transcript
    let mcp_url = "https://transcriptapi.com/mcp";
    let payload = serde_json::json!({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_youtube_transcript",
            "arguments": {
                "video_url": video_id,
                "format": "json",
                "include_timestamp": true
            }
        }
    });

    let resp = client
        .post(mcp_url)
        .header("Authorization", format!("Bearer {}", API_KEY))
        .header("Content-Type", "application/json")
        .header("Accept", "application/json, text/event-stream")
        .json(&payload)
        .send()?
        .text()?;

    for line in resp.lines() {
        let line = if line.starts_with("data: ") {
            &line[6..]
        } else {
            line
        };
        if line.trim().is_empty() {
            continue;
        }
        if let Ok(val) = serde_json::from_str::<serde_json::Value>(line) {
            if let Some(res) = val.get("result") {
                if let Ok(t_resp) = serde_json::from_value::<TranscriptResponse>(res.clone()) {
                    if let Some(content) = t_resp.content {
                        match content {
                            TranscriptContent::Structured { transcript } => {
                                if let Some(segs) = transcript {
                                    return Ok(segs);
                                }
                            }
                            TranscriptContent::List(segs) => return Ok(segs),
                            TranscriptContent::StringPayload(s) => {
                                if let Ok(segs) = serde_json::from_str::<Vec<RawSegment>>(&s) {
                                    return Ok(segs);
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Err(format!("Could not fetch transcript for {}", video_id).into())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🦀 Launching High-Performance Rust Ingestion Engine for Philip DeFranco Curated Suite...\n");

    fs::create_dir_all(DOWNLOADED_DIR)?;
    fs::create_dir_all(FORMATTED_DIR)?;

    let client = Client::builder()
        .timeout(Duration::from_secs(30))
        .build()?;

    // Identify already ingested videos to avoid redundant credits
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

    println!("⚡ Currently ingested Philip DeFranco videos in library: {}", existing_vids.len());

    // Pool of candidates: video_id -> (video_info, topics)
    let mut candidates: HashMap<String, (SearchResultVideo, Vec<String>)> = HashMap::new();

    let target_topics = [
        ("AI", 3),      // query, max pages
        ("Tech", 3),
        ("Economy", 3),
    ];

    println!("\n📡 Querying TranscriptAPI channel search with pagination...");

    for (topic, max_pages) in target_topics {
        println!("   🔍 Searching topic '{}' (up to {} pages)...", topic, max_pages);
        let mut continuation: Option<String> = None;

        for page in 1..=max_pages {
            let res = if page == 1 {
                call_mcp_search(&client, Some(topic), None)
            } else {
                match continuation {
                    Some(ref token) => call_mcp_search(&client, None, Some(token)),
                    None => break,
                }
            };

            match res {
                Ok(content) => {
                    let results = content.results.unwrap_or_default();
                    println!("      Page {}: found {} raw results", page, results.len());

                    for v in results {
                        if let Some(ref vid) = v.video_id {
                            if existing_vids.contains(vid) {
                                continue;
                            }
                            let dur_str = v.length_text.as_deref().unwrap_or("0:00");
                            let sec = parse_duration_to_seconds(dur_str);
                            if sec < 180 {
                                // Exclude shorts (< 3 min)
                                continue;
                            }

                            candidates
                                .entry(vid.clone())
                                .and_modify(|(_, topics)| {
                                    if !topics.contains(&topic.to_string()) {
                                        topics.push(topic.to_string());
                                    }
                                })
                                .or_insert((v.clone(), vec![topic.to_string()]));
                        }
                    }

                    continuation = content.continuation_token;
                    if continuation.is_none() || !content.has_more.unwrap_or(false) {
                        break;
                    }
                }
                Err(e) => {
                    println!("      Page {} search error: {}", page, e);
                    break;
                }
            }
        }
    }

    println!("\n🎯 Total unique high-signal candidate videos discovered: {}", candidates.len());

    // Target up to 100 videos
    let target_quota = 100.min(candidates.len());
    let mut candidate_list: Vec<_> = candidates.into_iter().collect();

    // Prioritize by multi-topic relevance and duration
    candidate_list.sort_by(|a, b| {
        let a_score = a.1 .1.len() * 1000 + parse_duration_to_seconds(a.1 .0.length_text.as_deref().unwrap_or("0:00")) as usize;
        let b_score = b.1 .1.len() * 1000 + parse_duration_to_seconds(b.1 .0.length_text.as_deref().unwrap_or("0:00")) as usize;
        b_score.cmp(&a_score)
    });

    println!("⚡ Target quota to ingest: {} curated long-form episodes.\n", target_quota);

    let mut successful_ingestions = 0;
    let mut credits_used = 0;

    for (idx, (vid, (meta, topics))) in candidate_list.iter().take(target_quota).enumerate() {
        let title = meta.title.as_deref().unwrap_or("Untitled");
        let dur = meta.length_text.as_deref().unwrap_or("00:00");
        let pub_text = meta.published_time_text.as_deref().unwrap_or("");

        println!(
            "[{}/{}] Ingesting: '{}' ({}, {}) [Topics: {}]...",
            idx + 1,
            target_quota,
            title,
            dur,
            pub_text,
            topics.join(", ")
        );

        match fetch_transcript(&client, vid) {
            Ok(segments) => {
                if segments.is_empty() {
                    println!("   ⚠️  Empty segments returned for {}, skipping.", vid);
                    continue;
                }

                credits_used += 1;
                let (full_transcript, timestamps, max_sec) = build_transcript_and_timestamps(&segments);
                let duration_fmt = format_duration_seconds(max_sec);

                // 1. Write Archive JSON
                let archive_pkt = ArchiveJson {
                    video_id: vid.clone(),
                    title: title.to_string(),
                    channel: "Philip DeFranco".to_string(),
                    handle: "@PhilipDeFranco".to_string(),
                    url: format!("https://www.youtube.com/watch?v={}", vid),
                    duration: duration_fmt.clone(),
                    word_count: full_transcript.split_whitespace().count(),
                    published: pub_text.to_string(),
                    raw_segments: segments,
                    topics: topics.clone(),
                };

                let json_path = format!("{}/step_manual_{}.json", DOWNLOADED_DIR, vid);
                let mut jf = File::create(&json_path)?;
                serde_json::to_writer_pretty(&mut jf, &archive_pkt)?;

                // 2. Write Clean Formatted YAML
                let formatted_doc = FormattedTranscript {
                    video_id: vid.clone(),
                    title: title.to_string(),
                    channel: "Philip DeFranco".to_string(),
                    handle: Some("@PhilipDeFranco".to_string()),
                    url: format!("https://www.youtube.com/watch?v={}", vid),
                    duration: duration_fmt,
                    published: Some(pub_text.to_string()),
                    content_type: "video".to_string(),
                    transcript: full_transcript,
                    timestamps,
                };

                let clean_yaml = serialize_clean_yaml(&formatted_doc)?;
                let yaml_path = format!("{}/step_manual_{}.yaml", FORMATTED_DIR, vid);
                let mut yf = File::create(&yaml_path)?;
                yf.write_all(clean_yaml.as_bytes())?;

                successful_ingestions += 1;
                println!(
                    "   ✅ Successfully saved (words: {}, timestamps: {}) -> {}",
                    formatted_doc.transcript.split_whitespace().count(),
                    formatted_doc.timestamps.len(),
                    yaml_path
                );
            }
            Err(e) => {
                println!("   ❌ Failed to fetch transcript for {}: {}", vid, e);
            }
        }
    }

    println!(
        "\n🎉 Completed Rust Ingestion Pipeline! Successfully ingested {} videos (credits used: {}).",
        successful_ingestions, credits_used
    );

    Ok(())
}
