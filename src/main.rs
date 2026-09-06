use clap::{Parser, Subcommand};
use indicatif::{ProgressBar, ProgressStyle};
use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::Instant;
use youtube_extractor::{
    build_transcript_and_timestamps, extract_video_id, fetch_transcript_segments,
    format_duration_seconds, serialize_clean_yaml, FormattedTranscript, RawSegment,
};

const DOWNLOADED_DIR: &str = "downloaded_transcripts";
const FORMATTED_DIR: &str = "formatted_transcripts";

#[derive(Parser, Debug)]
#[command(name = "youtube-extractor")]
#[command(author = "Austin Rognes")]
#[command(version = "0.1.0")]
#[command(about = "High-performance Rust YouTube Transcripts & Knowledge Extractor CLI", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Download and format a single YouTube video transcript
    Download {
        /// Video ID or full YouTube URL
        video: String,
        /// Channel name override
        #[arg(short, long, default_value = "Unknown Channel")]
        channel: String,
        /// Channel handle (e.g. @ChannelName)
        #[arg(long)]
        handle: Option<String>,
        /// Video title override (optional)
        #[arg(short, long)]
        title: Option<String>,
        /// Published date or time string
        #[arg(short, long)]
        published: Option<String>,
    },

    /// Batch download transcripts from a JSON queue with dynamic workers and ETA predictions
    Batch {
        /// Path to JSON queue file containing [{"videoId": "...", "title": "...", ...}]
        queue_file: PathBuf,
        /// Number of concurrent worker threads (defaults to system CPU count)
        #[arg(short, long)]
        workers: Option<usize>,
        /// Channel name override for all items in the queue (if not present in queue item)
        #[arg(short, long)]
        channel: Option<String>,
        /// Skip already downloaded/formatted transcripts
        #[arg(long, default_value_t = true)]
        skip_existing: bool,
    },

    /// Search across all formatted transcripts with timestamp cues and jump URLs
    Search {
        /// Search query or pattern
        query: String,
        /// Filter by channel name
        #[arg(short, long)]
        channel: Option<String>,
        /// Filter by content type (video or short)
        #[arg(short, long)]
        content_type: Option<String>,
        /// Maximum matches to display
        #[arg(short, long, default_value_t = 10)]
        limit: usize,
        /// Match exact word boundaries
        #[arg(long)]
        exact: bool,
        /// Treat query as a regular expression
        #[arg(long)]
        regex: bool,
    },

    /// Display library statistics, transcript counts, and channel summaries
    Status,
}

#[derive(Debug, Clone, Deserialize)]
struct QueueItem {
    #[serde(alias = "videoId", alias = "id")]
    video_id: String,
    #[serde(default)]
    title: Option<String>,
    #[serde(default)]
    channel: Option<String>,
    #[serde(default)]
    duration: Option<String>,
    #[serde(default)]
    published: Option<String>,
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

#[derive(Debug, Deserialize)]
struct YamlHeaderOnly {
    #[serde(default)]
    video_id: String,
    #[serde(default)]
    title: String,
    #[serde(default)]
    channel: String,
    #[serde(default)]
    duration: String,
    #[serde(default, rename = "type")]
    content_type: String,
    #[serde(default)]
    transcript: String,
    #[serde(default)]
    timestamps: Vec<[usize; 2]>,
}

fn ingest_video(
    video_id: &str,
    title: &str,
    channel: &str,
    handle: Option<&str>,
    published: Option<&str>,
    topics: &[String],
) -> Result<usize, String> {
    fs::create_dir_all(DOWNLOADED_DIR).map_err(|e| e.to_string())?;
    fs::create_dir_all(FORMATTED_DIR).map_err(|e| e.to_string())?;

    let segments = fetch_transcript_segments(video_id)
        .ok_or_else(|| format!("Transcript unavailable for video {}", video_id))?;

    let (full_transcript, timestamps, max_sec) = build_transcript_and_timestamps(&segments);
    let duration_fmt = format_duration_seconds(max_sec);
    let word_count = full_transcript.split_whitespace().count();

    // 1. Write Archive JSON
    let archive = ArchiveJson {
        video_id: video_id.to_string(),
        title: title.to_string(),
        channel: channel.to_string(),
        handle: handle.unwrap_or("").to_string(),
        url: format!("https://www.youtube.com/watch?v={}", video_id),
        duration: duration_fmt.clone(),
        word_count,
        published: published.unwrap_or("").to_string(),
        raw_segments: segments,
        topics: topics.to_vec(),
    };

    let json_path = format!("{}/step_manual_{}.json", DOWNLOADED_DIR, video_id);
    let jf = File::create(&json_path).map_err(|e| e.to_string())?;
    serde_json::to_writer_pretty(jf, &archive).map_err(|e| e.to_string())?;

    // 2. Write Formatted YAML
    let formatted_doc = FormattedTranscript {
        video_id: video_id.to_string(),
        title: title.to_string(),
        channel: channel.to_string(),
        handle: handle.map(|s| s.to_string()),
        url: format!("https://www.youtube.com/watch?v={}", video_id),
        duration: duration_fmt,
        published: published.map(|s| s.to_string()),
        content_type: "video".to_string(),
        transcript: full_transcript,
        timestamps,
    };

    let clean_yaml = serialize_clean_yaml(&formatted_doc).map_err(|e| e.to_string())?;
    let yaml_path = format!("{}/step_manual_{}.yaml", FORMATTED_DIR, video_id);
    let mut yf = File::create(&yaml_path).map_err(|e| e.to_string())?;
    yf.write_all(clean_yaml.as_bytes()).map_err(|e| e.to_string())?;

    Ok(word_count)
}

fn run_single_download(
    raw_video: &str,
    channel: &str,
    handle: Option<&str>,
    title: Option<&str>,
    published: Option<&str>,
) -> Result<(), Box<dyn std::error::Error>> {
    let vid = extract_video_id(raw_video)
        .ok_or_else(|| format!("Invalid YouTube video ID or URL: {}", raw_video))?;

    let final_title = title.unwrap_or(&vid);
    println!("⬇️  Downloading transcript for: [{}] '{}'...", vid, final_title);

    let start = Instant::now();
    match ingest_video(&vid, final_title, channel, handle, published, &[]) {
        Ok(words) => {
            println!(
                "✅ Successfully ingested in {:.2}s! ({} words written to formatted_transcripts/step_manual_{}.yaml)",
                start.elapsed().as_secs_f64(),
                words,
                vid
            );
        }
        Err(e) => {
            eprintln!("❌ Download failed: {}", e);
        }
    }

    Ok(())
}

fn run_batch_download(
    queue_file: &Path,
    workers_opt: Option<usize>,
    channel_override: Option<&str>,
    skip_existing: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    let num_workers = workers_opt.unwrap_or_else(|| {
        let cpus = num_cpus();
        cpus.clamp(2, 16)
    });

    println!("⚡ Initializing worker pool with {} threads...", num_workers);
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(num_workers)
        .build()?;

    let queue_str = fs::read_to_string(queue_file)
        .map_err(|e| format!("Failed to read queue file {:?}: {}", queue_file, e))?;
    let queue: Vec<QueueItem> = serde_json::from_str(&queue_str)?;

    println!("📋 Loaded {} candidates from {:?}", queue.len(), queue_file);

    // Scan existing videos to support skip_existing
    let mut existing_vids = HashSet::new();
    if skip_existing {
        if let Ok(entries) = fs::read_dir(FORMATTED_DIR) {
            for entry in entries.filter_map(|e| e.ok()) {
                let p = entry.path();
                if p.extension().map_or(false, |ext| ext == "yaml") {
                    let fname = p.file_stem().and_then(|s| s.to_str()).unwrap_or("");
                    if let Some(vid) = fname.strip_prefix("step_manual_").or_else(|| fname.strip_prefix("step_")) {
                        let clean_vid = if vid.len() > 11 && vid.chars().nth(4) == Some('_') {
                            &vid[5..]
                        } else {
                            vid
                        };
                        existing_vids.insert(clean_vid.to_string());
                    }
                }
            }
        }
    }

    let to_process: Vec<QueueItem> = queue
        .into_iter()
        .filter(|item| !skip_existing || !existing_vids.contains(&item.video_id))
        .collect();

    let total = to_process.len();
    if total == 0 {
        println!("✨ All videos in queue already ingested! Nothing to do.");
        return Ok(());
    }

    println!(
        "🚀 Starting batch download for {} videos (Workers: {}, Skipped existing: {})...",
        total,
        num_workers,
        existing_vids.len()
    );

    let pb = ProgressBar::new(total as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template(
                "{spinner:.green} [{elapsed_precise}] [{bar:30.cyan/blue}] {pos}/{len} ({percent}%) | {per_sec} | ETA: {eta} | {msg}",
            )?
            .progress_chars("━╸─"),
    );

    let success_count = Arc::new(AtomicUsize::new(0));
    let fail_count = Arc::new(AtomicUsize::new(0));
    let total_words = Arc::new(AtomicUsize::new(0));

    pool.install(|| {
        to_process.par_iter().for_each(|item| {
            let vid = &item.video_id;
            let ch = channel_override
                .or(item.channel.as_deref())
                .unwrap_or("Unknown Channel");
            let title = item.title.as_deref().unwrap_or(vid);
            let pub_date = item.published.as_deref();

            pb.set_message(format!("{}: {}", vid, title.chars().take(20).collect::<String>()));

            match ingest_video(vid, title, ch, None, pub_date, &item.topics) {
                Ok(w) => {
                    success_count.fetch_add(1, Ordering::Relaxed);
                    total_words.fetch_add(w, Ordering::Relaxed);
                }
                Err(_) => {
                    fail_count.fetch_add(1, Ordering::Relaxed);
                }
            }
            pb.inc(1);
        });
    });

    pb.finish_with_message("Batch Ingestion Complete!");

    let succ = success_count.load(Ordering::SeqCst);
    let fail = fail_count.load(Ordering::SeqCst);
    let words = total_words.load(Ordering::SeqCst);

    println!("\n=======================================================");
    println!("🎉 Batch Summary:");
    println!(" - Ingested successfully: {}", succ);
    println!(" - Failed / unavailable:  {}", fail);
    println!(" - Total words ingested:  {}", words);
    println!("=======================================================");

    Ok(())
}

fn num_cpus() -> usize {
    std::thread::available_parallelism()
        .map(|n| n.get())
        .unwrap_or(4)
}

fn run_search(
    query: &str,
    channel_filter: Option<&str>,
    type_filter: Option<&str>,
    limit: usize,
    exact: bool,
    is_regex: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    let re = if is_regex {
        Regex::new(query)?
    } else if exact {
        Regex::new(&format!(r"(?i)\b{}\b", regex::escape(query)))?
    } else {
        Regex::new(&format!(r"(?i){}", regex::escape(query)))?
    };

    let files: Vec<PathBuf> = fs::read_dir(FORMATTED_DIR)?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map_or(false, |ext| ext == "yaml"))
        .collect();

    println!("🔍 Searching across {} transcript files for '{}'...", files.len(), query);
    let start_time = Instant::now();

    let matches: Vec<(String, String, String, usize, String, String)> = files
        .par_iter()
        .filter_map(|path| {
            let content = fs::read_to_string(path).ok()?;
            let doc: YamlHeaderOnly = serde_yaml::from_str(&content).ok()?;

            if let Some(cf) = channel_filter {
                if !doc.channel.to_lowercase().contains(&cf.to_lowercase()) {
                    return None;
                }
            }
            if let Some(tf) = type_filter {
                if !doc.content_type.to_lowercase().contains(&tf.to_lowercase()) {
                    return None;
                }
            }

            if let Some(m) = re.find(&doc.transcript) {
                let char_idx = m.start();
                let sec = find_timestamp_for_char(&doc.timestamps, char_idx);
                let jump_url = format!("https://www.youtube.com/watch?v={}&t={}s", doc.video_id, sec);
                let snippet = extract_snippet(&doc.transcript, m.start(), m.end(), 60);

                Some((doc.title, doc.channel, doc.duration, sec, jump_url, snippet))
            } else {
                None
            }
        })
        .collect();

    println!("⚡ Search completed in {:.2}ms! Found {} matches:\n", start_time.elapsed().as_secs_f64() * 1000.0, matches.len());

    for (i, (title, channel, duration, sec, jump_url, snippet)) in matches.iter().take(limit).enumerate() {
        let hh = sec / 3600;
        let mm = (sec % 3600) / 60;
        let ss = sec % 60;
        let time_fmt = if hh > 0 {
            format!("{:02}:{:02}:{:02}", hh, mm, ss)
        } else {
            format!("{:02}:{:02}", mm, ss)
        };

        println!("{}. \x1b[1;36m{}\x1b[0m (\x1b[1;35m{}\x1b[0m, {})", i + 1, title, channel, duration);
        println!("   ⏱️  {}  🔗 \x1b[4;34m{}\x1b[0m", time_fmt, jump_url);
        println!("   💬 \"{}\"\n", snippet);
    }

    Ok(())
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

fn run_status() -> Result<(), Box<dyn std::error::Error>> {
    println!("\n=======================================================");
    println!("📊 YOUTUBE KNOWLEDGE EXTRACTOR - REPOSITORY STATUS");
    println!("=======================================================");

    let formatted_files: Vec<PathBuf> = fs::read_dir(FORMATTED_DIR)?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map_or(false, |ext| ext == "yaml"))
        .collect();

    let mut total_words = 0usize;
    let mut channel_counts = std::collections::HashMap::new();

    for path in &formatted_files {
        if let Ok(content) = fs::read_to_string(path) {
            for line in content.lines() {
                if line.starts_with("channel:") {
                    let ch = line.trim_start_matches("channel:").trim().trim_matches('\'').trim_matches('"');
                    *channel_counts.entry(ch.to_string()).or_insert(0usize) += 1;
                }
            }
            if let Some(pos) = content.find("transcript:") {
                let tr = &content[pos + 11..];
                let end_pos = tr.find("\ntimestamps:").unwrap_or(tr.len());
                total_words += tr[..end_pos].split_whitespace().count();
            }
        }
    }

    println!("📚 Formatted Transcripts:  {}", formatted_files.len());
    println!("📝 Total Spoken Words:      {}", total_words);
    println!("🎙️  Unique Channels:         {}", channel_counts.len());

    let mut sorted_channels: Vec<(String, usize)> = channel_counts.into_iter().collect();
    sorted_channels.sort_by(|a, b| b.1.cmp(&a.1));

    println!("\n🏆 Top Channels by Video Count:");
    for (ch, count) in sorted_channels.iter().take(10) {
        println!(" - {:35} {:4} videos", ch, count);
    }
    println!("=======================================================\n");

    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Download {
            video,
            channel,
            handle,
            title,
            published,
        } => {
            run_single_download(&video, &channel, handle.as_deref(), title.as_deref(), published.as_deref())?;
        }
        Commands::Batch {
            queue_file,
            workers,
            channel,
            skip_existing,
        } => {
            run_batch_download(&queue_file, workers, channel.as_deref(), skip_existing)?;
        }
        Commands::Search {
            query,
            channel,
            content_type,
            limit,
            exact,
            regex,
        } => {
            run_search(&query, channel.as_deref(), content_type.as_deref(), limit, exact, regex)?;
        }
        Commands::Status => {
            run_status()?;
        }
    }

    Ok(())
}
