use crate::{parse_duration_to_seconds, ChannelVideoItem};

#[derive(Debug, Clone)]
pub struct ScoredCandidate {
    pub item: ChannelVideoItem,
    pub duration_seconds: u32,
    pub score: f64,
    pub already_downloaded: bool,
}

/// Calculate the Transcript Value Heuristic (TVH) score for a video candidate:
/// TVH = DurationWeight * RecencyWeight * TitleRelevanceMultiplier
pub fn score_candidate(
    item: &ChannelVideoItem,
    query_filter: Option<&str>,
    min_duration_sec: u32,
    already_downloaded: bool,
) -> Option<ScoredCandidate> {
    let len_str = item.length_text.as_deref().unwrap_or("0:00");
    let dur_sec = parse_duration_to_seconds(len_str);

    // Hard filter 1: Strictly reject anything shorter than min_duration_sec (default 60s)
    if dur_sec < min_duration_sec {
        return None;
    }

    // Hard filter 2: Reject obvious YouTube Shorts markers in title or duration
    if item.title.to_lowercase().contains("#shorts") || dur_sec < 60 {
        return None;
    }

    // Optional filter: query filter on title
    if let Some(q) = query_filter {
        if !item.title.to_lowercase().contains(&q.to_lowercase()) {
            return None;
        }
    }

    // 1. Duration Weighting (Sweet spot: 10m to 60m)
    // 60s - 300s (1m - 5m): 1.0 -> 5.0
    // 300s - 3600s (5m - 60m): 5.0 -> 10.0
    // > 3600s (> 60m): Logarithmic growth capped at 12.0
    let duration_weight = if dur_sec < 300 {
        1.0 + (dur_sec as f64 - 60.0) / 240.0 * 4.0
    } else if dur_sec <= 3600 {
        5.0 + ((dur_sec - 300) as f64 / 3300.0) * 5.0
    } else {
        10.0 + ((dur_sec - 3600) as f64 / 3600.0).ln_1p().min(2.0)
    };

    // 2. Recency Weighting
    let recency_weight = if let Some(ref pub_text) = item.published_time_text {
        let lower = pub_text.to_lowercase();
        if lower.contains("hour") || lower.contains("day") || lower.contains("yesterday") {
            1.5
        } else if lower.contains("week") {
            1.4
        } else if lower.contains("month") {
            1.2
        } else if lower.contains("1 year") {
            1.0
        } else {
            0.9
        }
    } else {
        1.0
    };

    // 3. Title Information Density Multiplier
    // High-value essay / conceptual indicators get a boost
    let title_lower = item.title.to_lowercase();
    let mut title_multiplier = 1.0;
    let high_value_keywords = [
        "explained", "deep dive", "how to", "why", "architecture", "history", "breakdown",
        "engineering", "system", "guide", "analysis", "case study", "tutorial", "economy", "ai",
    ];
    for kw in high_value_keywords {
        if title_lower.contains(kw) {
            title_multiplier += 0.1;
        }
    }

    let final_score = duration_weight * recency_weight * title_multiplier;

    Some(ScoredCandidate {
        item: item.clone(),
        duration_seconds: dur_sec,
        score: final_score,
        already_downloaded,
    })
}
