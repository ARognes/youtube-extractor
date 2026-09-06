use rayon::prelude::*;
use regex::Regex;
use serde::Deserialize;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Deserialize)]
struct YamlTranscript {
    #[serde(default)]
    video_id: String,
    #[serde(default)]
    title: String,
    #[serde(default)]
    channel: String,
    #[serde(default)]
    url: String,
    #[serde(default)]
    duration: String,
    #[serde(default, rename = "type")]
    content_type: String,
    #[serde(default)]
    transcript: String,
    #[serde(default)]
    timestamps: Vec<[usize; 2]>,
}

struct SearchMatch {
    title: String,
    channel: String,
    duration: String,
    content_type: String,
    time_str: String,
    seconds: usize,
    jump_url: String,
    snippet: String,
}

fn format_seconds(seconds: usize) -> String {
    let hh = seconds / 3600;
    let mm = (seconds % 3600) / 60;
    let ss = seconds % 60;
    if hh > 0 {
        format!("{:02}:{:02}:{:02}", hh, mm, ss)
    } else {
        format!("{:02}:{:02}", mm, ss)
    }
}

fn find_timestamp_for_char(timestamps: &[[usize; 2]], char_idx: usize) -> usize {
    if timestamps.is_empty() {
        return 0;
    }
    let idx = timestamps.partition_point(|p| p[0] <= char_idx);
    if idx > 0 {
        timestamps[idx - 1][1]
    } else {
        timestamps[0][1]
    }
}

fn extract_snippet(text: &str, m_start: usize, m_end: usize, radius: usize) -> String {
    let s = m_start.saturating_sub(radius);
    let e = (m_end + radius).min(text.len());

    let prefix = if s > 0 { "..." } else { "" };
    let prefix_text = &text[s..m_start].replace('\n', " ");
    let matched_text = &text[m_start..m_end].replace('\n', " ");
    let suffix_text = &text[m_end..e].replace('\n', " ");
    let suffix = if e < text.len() { "..." } else { "" };

    format!("{}{}\x1b[1;33m{}\x1b[0m{}{}", prefix, prefix_text, matched_text, suffix_text, suffix)
}

fn print_usage() {
    println!("Usage: search_transcripts <query> [options]");
    println!("Options:");
    println!("  --channel <name>      Filter by channel name");
    println!("  --type <video|short>  Filter by content type");
    println!("  --limit <number>      Maximum matches to show (default: 10)");
    println!("  --exact               Match exact word boundaries");
    println!("  --regex               Treat query as regex");
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        print_usage();
        return Ok(());
    }

    let mut query = String::new();
    let mut channel_filter: Option<String> = None;
    let mut type_filter: Option<String> = None;
    let mut limit = 10usize;
    let mut exact = false;
    let mut is_regex = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-h" | "--help" => {
                print_usage();
                return Ok(());
            }
            "--channel" => {
                i += 1;
                if i < args.len() {
                    channel_filter = Some(args[i].to_lowercase());
                }
            }
            "--type" => {
                i += 1;
                if i < args.len() {
                    type_filter = Some(args[i].to_lowercase());
                }
            }
            "--limit" => {
                i += 1;
                if i < args.len() {
                    if let Ok(l) = args[i].parse::<usize>() {
                        limit = l;
                    }
                }
            }
            "--exact" => {
                exact = true;
            }
            "--regex" => {
                is_regex = true;
            }
            other => {
                if query.is_empty() {
                    query = other.to_string();
                }
            }
        }
        i += 1;
    }

    if query.is_empty() {
        eprintln!("Error: No search query provided.");
        print_usage();
        std::process::exit(1);
    }

    let formatted_dir = Path::new("formatted_transcripts");
    if !formatted_dir.exists() {
        eprintln!("Error: Directory 'formatted_transcripts' not found.");
        std::process::exit(1);
    }

    let pattern_str = if is_regex {
        query.clone()
    } else if exact {
        format!(r"\b{}\b", regex::escape(&query))
    } else {
        regex::escape(&query)
    };

    let search_rx = match Regex::new(&format!("(?i){}", pattern_str)) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("Invalid search pattern: {}", e);
            std::process::exit(1);
        }
    };

    let mut entries: Vec<PathBuf> = fs::read_dir(formatted_dir)?
        .filter_map(|res| res.ok())
        .map(|entry| entry.path())
        .filter(|p| p.extension().map_or(false, |ext| ext == "yaml"))
        .collect();
    entries.sort();

    println!(
        "\n\x1b[36m🔍 Searching for '{}' across {} formatted transcripts...\x1b[0m",
        query, entries.len()
    );

    let matches: Vec<SearchMatch> = entries
        .par_iter()
        .filter_map(|path| {
            let content = fs::read_to_string(path).ok()?;
            let doc: YamlTranscript = serde_yaml::from_str(&content).ok()?;

            if let Some(ref cf) = channel_filter {
                if !doc.channel.to_lowercase().contains(cf) {
                    return None;
                }
            }
            if let Some(ref tf) = type_filter {
                if !doc.content_type.to_lowercase().contains(tf) {
                    return None;
                }
            }

            if doc.transcript.is_empty() {
                return None;
            }

            if let Some(m) = search_rx.find(&doc.transcript) {
                let m_start = m.start();
                let m_end = m.end();
                let seconds = find_timestamp_for_char(&doc.timestamps, m_start);
                let time_str = format_seconds(seconds);
                let clean_url = doc.url.split('?').next().unwrap_or(&doc.url);
                let jump_url = format!("{}?v={}&t={}s", clean_url, doc.video_id, seconds);
                let snippet = extract_snippet(&doc.transcript, m_start, m_end, 85);

                Some(SearchMatch {
                    title: doc.title,
                    channel: doc.channel,
                    duration: doc.duration,
                    content_type: doc.content_type,
                    time_str,
                    seconds,
                    jump_url,
                    snippet,
                })
            } else {
                None
            }
        })
        .collect();

    println!(
        "\x1b[32m🎯 Found {} matches (showing up to {}):\x1b[0m\n",
        matches.len(),
        limit
    );

    if matches.is_empty() {
        println!("   No matching transcripts found. Try broadening your query or removing filters.");
        return Ok(());
    }

    for (idx, m) in matches.iter().take(limit).enumerate() {
        let type_badge = if m.content_type == "short" {
            "\x1b[1;35m[SHORT]\x1b[0m"
        } else {
            "\x1b[1;36m[VIDEO]\x1b[0m"
        };

        println!("{}. \x1b[1m{}\x1b[0m {}", idx + 1, m.title, type_badge);
        println!(
            "   \x1b[2mChannel:\x1b[0m {}  |  \x1b[2mDuration:\x1b[0m {}  |  \x1b[2mTimestamp:\x1b[0m \x1b[1;32m{}\x1b[0m ({}s)",
            m.channel, m.duration, m.time_str, m.seconds
        );
        println!("   \x1b[2mContext:\x1b[0m \"{}\"", m.snippet);
        if !m.jump_url.is_empty() {
            println!("   👉 \x1b[1;36mJump to video:\x1b[0m \x1b[4m{}\x1b[0m", m.jump_url);
        }
        println!();
    }

    Ok(())
}
