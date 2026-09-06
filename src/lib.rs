use serde::{Deserialize, Serialize};

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
    
    // Format transcript scalar cleanly
    yaml_out.push_str(&format!("transcript: {}\n", serde_yaml::to_string(&doc.transcript)?.trim()));
    
    // Format timestamps as clean flow sequence
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

/// Fetch transcript segments using native fallback or Python helper
pub fn fetch_transcript_segments(video_id: &str) -> Option<Vec<RawSegment>> {
    // 1. Try python youtube_transcript_api helper
    let script = format!(
        "from youtube_transcript_api import YouTubeTranscriptApi; import json; res = YouTubeTranscriptApi().fetch('{}'); print(json.dumps([{{'text': s.text, 'start': s.start, 'duration': s.duration}} for s in res]))",
        video_id
    );

    if let Ok(output) = std::process::Command::new("python3").arg("-c").arg(&script).output() {
        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            if let Ok(segs) = serde_json::from_str::<Vec<RawSegment>>(&stdout) {
                if !segs.is_empty() {
                    return Some(segs);
                }
            }
        }
    }

    None
}
