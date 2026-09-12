pub mod heuristic;
use serde::{Deserialize, Serialize};

pub const TRANSCRIPT_API_KEY: &str = "sk_JaAysZu79sqC3_fBTneaD3FcFXuhiz1Br9a862wb8JM";
pub const SUPADATA_API_KEY: &str = "sd_32b8567c225df115f94f200dde8b8b61";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormattedTranscript {
    pub video_id: String,
    pub title: String,
    pub channel: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub handle: Option<String>,
    pub url: String,
    pub duration: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub published: Option<String>,
    #[serde(rename = "type")]
    pub content_type: String,
    pub transcript: String,
    pub timestamps: Vec<[usize; 2]>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RawSegment {
    #[serde(default)]
    pub text: String,
    #[serde(default)]
    pub start: f64,
    #[serde(default)]
    pub duration: f64,
}

#[derive(Debug, Deserialize)]
struct TranscriptApiResponse {
    #[serde(default)]
    transcript: Vec<RawSegment>,
}

#[derive(Debug, Deserialize)]
struct SupadataSegment {
    #[serde(default)]
    text: String,
    #[serde(default)]
    start: f64,
    #[serde(default)]
    duration: f64,
}

#[derive(Debug, Deserialize)]
struct SupadataResponse {
    #[serde(default)]
    content: Vec<SupadataSegment>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ChannelVideoItem {
    #[serde(rename = "videoId")]
    pub video_id: String,
    #[serde(default)]
    pub title: String,
    #[serde(default, rename = "channelTitle")]
    pub channel_title: Option<String>,
    #[serde(default, rename = "channelHandle")]
    pub channel_handle: Option<String>,
    #[serde(default, rename = "lengthText")]
    pub length_text: Option<String>,
    #[serde(default, rename = "publishedTimeText")]
    pub published_time_text: Option<String>,
    #[serde(default, rename = "viewCountText")]
    pub view_count_text: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ChannelVideosResponse {
    #[serde(default)]
    results: Vec<ChannelVideoItem>,
    #[serde(default)]
    continuation_token: Option<String>,
    #[serde(default)]
    has_more: bool,
}

#[derive(Debug, Deserialize)]
struct ResolveResponse {
    #[serde(default)]
    channel_id: Option<String>,
}

pub fn format_duration_seconds(seconds: u32) -> String {
    let hh = seconds / 3600;
    let mm = (seconds % 3600) / 60;
    let ss = seconds % 60;
    if hh > 0 {
        format!("{:02}:{:02}:{:02}", hh, mm, ss)
    } else {
        format!("{:02}:{:02}", mm, ss)
    }
}

pub fn parse_duration_to_seconds(len_str: &str) -> u32 {
    let parts: Vec<&str> = len_str.trim().split(':').collect();
    match parts.len() {
        3 => {
            let h: u32 = parts[0].parse().unwrap_or(0);
            let m: u32 = parts[1].parse().unwrap_or(0);
            let s: u32 = parts[2].parse().unwrap_or(0);
            h * 3600 + m * 60 + s
        }
        2 => {
            let m: u32 = parts[0].parse().unwrap_or(0);
            let s: u32 = parts[1].parse().unwrap_or(0);
            m * 60 + s
        }
        1 => parts[0].parse().unwrap_or(0),
        _ => 0,
    }
}

pub fn build_transcript_and_timestamps(segments: &[RawSegment]) -> (String, Vec<[usize; 2]>, u32) {
    let mut chunks = Vec::new();
    let mut pairs = Vec::new();
    let mut curr_char = 0usize;
    let mut max_sec = 0u32;

    for seg in segments {
        let text = seg.text.replace('\n', " ").trim().to_string();
        if text.is_empty() {
            continue;
        }
        let sec = seg.start.round() as u32;
        if sec > max_sec {
            max_sec = sec;
        }
        if !chunks.is_empty() {
            curr_char += 1; // space delimiter
        }
        pairs.push([curr_char, sec as usize]);
        curr_char += text.len();
        chunks.push(text);
    }

    let full_transcript = chunks.join(" ");
    (full_transcript, pairs, max_sec)
}

/// Custom YAML serializer that renders `timestamps: [[0, 0], [39, 2], ...]` as inline flow sequences.
pub fn serialize_clean_yaml(doc: &FormattedTranscript) -> Result<String, Box<dyn std::error::Error>> {
    let mut yaml_out = String::new();
    yaml_out.push_str(&format!("video_id: {}\n", doc.video_id));
    yaml_out.push_str(&format!("title: {}\n", serde_yaml::to_string(&doc.title)?.trim()));
    yaml_out.push_str(&format!("channel: {}\n", serde_yaml::to_string(&doc.channel)?.trim()));
    if let Some(ref h) = doc.handle {
        yaml_out.push_str(&format!("handle: {}\n", serde_yaml::to_string(h)?.trim()));
    }
    yaml_out.push_str(&format!("url: {}\n", doc.url));
    yaml_out.push_str(&format!("duration: '{}'\n", doc.duration));
    if let Some(ref p) = doc.published {
        yaml_out.push_str(&format!("published: '{}'\n", p));
    }
    yaml_out.push_str(&format!("type: {}\n", doc.content_type));
    yaml_out.push_str(&format!("transcript: {}\n", serde_yaml::to_string(&doc.transcript)?.trim()));
    yaml_out.push_str("timestamps: [");
    for (i, pair) in doc.timestamps.iter().enumerate() {
        if i > 0 {
            yaml_out.push_str(", ");
        }
        yaml_out.push_str(&format!("[{}, {}]", pair[0], pair[1]));
    }
    yaml_out.push_str("]\n");

    Ok(yaml_out)
}

/// Extract clean 11-char YouTube video ID from either a raw ID or full URL
pub fn extract_video_id(input: &str) -> Option<String> {
    let trimmed = input.trim();
    if trimmed.len() == 11 && !trimmed.contains('/') && !trimmed.contains('?') && !trimmed.contains('&') {
        return Some(trimmed.to_string());
    }

    if let Ok(re) = regex::Regex::new(r"(?:v=|\/embed\/|\/shorts\/|\/watch\/|youtu\.be\/|\/v\/)([a-zA-Z0-9_-]{11})") {
        if let Some(caps) = re.captures(trimmed) {
            if let Some(m) = caps.get(1) {
                return Some(m.as_str().to_string());
            }
        }
    }
    None
}

/// Fetch transcript segments using paid/authenticated APIs only (TranscriptAPI -> Supadata fallback).
/// Never scrapes locally to prevent IP rate-limiting / blocking. Hard-fails with None if all fail.
pub fn fetch_transcript_segments(client: &reqwest::blocking::Client, video_id: &str) -> Option<Vec<RawSegment>> {
    // 1. TranscriptAPI (primary)
    let url_primary = format!(
        "https://transcriptapi.com/api/v2/youtube/transcript?video_url={}&format=json",
        video_id
    );

    if let Ok(resp) = client
        .get(&url_primary)
        .header("Authorization", format!("Bearer {}", TRANSCRIPT_API_KEY))
        .send()
    {
        if resp.status().is_success() {
            if let Ok(data) = resp.json::<TranscriptApiResponse>() {
                if !data.transcript.is_empty() {
                    return Some(data.transcript);
                }
            }
        }
    }

    // 2. Supadata API (backup paid provider)
    let url_supadata = format!("https://api.supadata.ai/v1/youtube/transcript?videoId={}&text=false", video_id);
    if let Ok(resp) = client
        .get(&url_supadata)
        .header("x-api-key", SUPADATA_API_KEY)
        .send()
    {
        if resp.status().is_success() {
            if let Ok(data) = resp.json::<SupadataResponse>() {
                if !data.content.is_empty() {
                    let segs = data
                        .content
                        .into_iter()
                        .map(|s| RawSegment {
                            text: s.text,
                            start: s.start,
                            duration: s.duration,
                        })
                        .collect();
                    return Some(segs);
                }
            }
        }
    }

    // Hard fail: never fallback to local scraping
    None
}

/// Resolves a channel input (e.g. "@PhilipDeFranco" or "https://www.youtube.com/@PhilipDeFranco") to a YouTube channel ID
pub fn resolve_channel_id(client: &reqwest::blocking::Client, input: &str) -> Result<String, String> {
    let clean_input = input.trim();
    if clean_input.starts_with("UC") && clean_input.len() >= 24 && !clean_input.contains('/') {
        return Ok(clean_input.to_string());
    }

    let url = format!(
        "https://transcriptapi.com/api/v2/youtube/channel/resolve?input={}",
        urlencoding::encode(clean_input)
    );

    let resp = client
        .get(&url)
        .header("Authorization", format!("Bearer {}", TRANSCRIPT_API_KEY))
        .send()
        .map_err(|e| format!("Network error resolving channel: {}", e))?;

    if !resp.status().is_success() {
        return Err(format!("Failed to resolve channel '{}': HTTP {}", clean_input, resp.status()));
    }

    let res: ResolveResponse = resp
        .json()
        .map_err(|e| format!("Failed to parse resolve response: {}", e))?;

    res.channel_id
        .ok_or_else(|| format!("No channel ID resolved for '{}'", clean_input))
}

/// Fetches recent channel videos from TranscriptAPI up to max_candidates
pub fn fetch_channel_videos(
    client: &reqwest::blocking::Client,
    channel_id: &str,
    max_candidates: usize,
) -> Result<Vec<ChannelVideoItem>, String> {
    let mut all_videos = Vec::new();
    let mut continuation_token: Option<String> = None;

    while all_videos.len() < max_candidates {
        let url = match &continuation_token {
            Some(token) => format!(
                "https://transcriptapi.com/api/v2/youtube/channel/videos?continuation={}",
                urlencoding::encode(token)
            ),
            None => format!(
                "https://transcriptapi.com/api/v2/youtube/channel/videos?channel={}",
                channel_id
            ),
        };

        let resp = client
            .get(&url)
            .header("Authorization", format!("Bearer {}", TRANSCRIPT_API_KEY))
            .send()
            .map_err(|e| format!("Failed to fetch channel videos: {}", e))?;

        if !resp.status().is_success() {
            return Err(format!("TranscriptAPI returned HTTP {} for channel videos", resp.status()));
        }

        let page: ChannelVideosResponse = resp
            .json()
            .map_err(|e| format!("Failed to parse channel videos JSON: {}", e))?;

        if page.results.is_empty() {
            break;
        }

        for item in page.results {
            all_videos.push(item);
            if all_videos.len() >= max_candidates {
                break;
            }
        }

        if !page.has_more || page.continuation_token.is_none() {
            break;
        }
        continuation_token = page.continuation_token;
    }

    Ok(all_videos)
}
