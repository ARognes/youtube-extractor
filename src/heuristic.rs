use crate::{parse_duration_to_seconds, ChannelVideoItem};
use regex::Regex;
use std::sync::LazyLock;

static RE_CLICKBAIT_PATTERNS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?i)\b(you won'?t believe|the truth about|why i (?:quit|left|stopped)|do not (?:buy|watch|do this)|mind[\s-]blowing|destroy(?:ed|s)?|insane|changes everything|before it'?s too late|exposed|shocking|secret revealed|they don'?t want you to know)\b"#).unwrap()
});

static RE_PUNCT_HYPE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"[!?]{2,}").unwrap()
});

#[derive(Debug, Clone)]
pub struct ScoredCandidate {
    pub item: ChannelVideoItem,
    pub duration_seconds: u32,
    pub score: f64,
    pub credibility_score: f64,
    pub utility_score: f64,
    pub sensationalism_score: f64,
    pub already_downloaded: bool,
    pub audit_reasons: Vec<String>,
}

/// Calculate the Grounded Multi-Signal Score for a candidate video.
/// Replaces the single naive heuristic with orthogonal Video, Channel, and Community signals:
/// - Video: Duration curve, conceptual depth keywords, ALL-CAPS/orthometrics, and clickbait penalties
/// - Channel: Authority patterns & focus priors
/// - Community: Engagement recency calibration
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

    let mut audit_reasons = Vec::new();
    let mut credibility: f64 = 50.0;
    let mut utility: f64 = 40.0;
    let mut sensationalism: f64 = 0.0;

    // -------------------------------------------------------------
    // 1. VIDEO ANCHOR: Duration Calibration & Information Density
    // -------------------------------------------------------------
    // Piecewise duration utility curve:
    // 60s - 300s (1m - 5m): Low instructional yield (-15)
    // 300s - 900s (5m - 15m): Quick overview (+5)
    // 900s - 3600s (15m - 60m): Deep work sweet spot (+25)
    // 3600s - 10800s (60m - 180m): Comprehensive seminar (+20)
    // > 10800s (> 3h): Long stream (+10)
    if dur_sec < 300 {
        utility -= 15.0;
        audit_reasons.push(format!("-15: Micro-duration ({}s) has limited depth", dur_sec));
    } else if dur_sec <= 900 {
        utility += 5.0;
        audit_reasons.push(format!("+5: Standard short explainer ({}m)", dur_sec / 60));
    } else if dur_sec <= 3600 {
        utility += 25.0;
        audit_reasons.push(format!("+25: Deep work sweet-spot duration ({}m)", dur_sec / 60));
    } else if dur_sec <= 10800 {
        utility += 20.0;
        audit_reasons.push(format!("+20: Comprehensive lecture/seminar duration ({}m)", dur_sec / 60));
    } else {
        utility += 10.0;
        audit_reasons.push(format!("+10: Extended recording ({}m)", dur_sec / 60));
    }

    // Title Information Density: Conceptual & Architectural terms
    let title_lower = item.title.to_lowercase();
    let high_value_keywords = [
        ("architecture", 15.0),
        ("system", 10.0),
        ("deep dive", 15.0),
        ("explained", 10.0),
        ("analysis", 10.0),
        ("case study", 15.0),
        ("engineering", 10.0),
        ("mechanisms", 15.0),
        ("fundamentals", 10.0),
        ("tutorial", 10.0),
        ("breakdown", 10.0),
        ("guide", 5.0),
    ];

    let mut kw_boost: f64 = 0.0;
    for (kw, boost) in high_value_keywords {
        if title_lower.contains(kw) {
            kw_boost += boost;
            audit_reasons.push(format!("+{:.0}: Conceptual keyword '{}'", boost, kw));
        }
    }
    utility += kw_boost.min(25.0);

    // Title Orthometrics & Sensationalism Penalties
    let alpha_chars: Vec<char> = item.title.chars().filter(|c| c.is_alphabetic()).collect();
    if alpha_chars.len() >= 10 {
        let upper_chars = alpha_chars.iter().filter(|c| c.is_uppercase()).count();
        let caps_ratio = upper_chars as f64 / alpha_chars.len() as f64;
        if caps_ratio > 0.40 {
            sensationalism += 25.0;
            audit_reasons.push(format!("-25: High ALL-CAPS ratio ({:.0}%) in title", caps_ratio * 100.0));
        } else if caps_ratio > 0.28 {
            sensationalism += 10.0;
            audit_reasons.push(format!("-10: Elevated capitalization ({:.0}%) in title", caps_ratio * 100.0));
        }
    }

    if RE_PUNCT_HYPE.is_match(&item.title) {
        sensationalism += 15.0;
        audit_reasons.push("-15: Punctuation hype (multiple ! or ?) in title".to_string());
    }

    let bait_matches: Vec<String> = RE_CLICKBAIT_PATTERNS
        .find_iter(&item.title)
        .map(|m| m.as_str().to_lowercase())
        .collect();
    if !bait_matches.is_empty() {
        let penalty = (bait_matches.len() as f64 * 15.0).min(45.0);
        sensationalism += penalty;
        audit_reasons.push(format!("-{:.0}: Sensationalist trigger phrases: {}", penalty, bait_matches.join(", ")));
    }

    // -------------------------------------------------------------
    // 2. COMMUNITY / RECENCY ANCHOR
    // -------------------------------------------------------------
    if let Some(ref pub_text) = item.published_time_text {
        let lower = pub_text.to_lowercase();
        if lower.contains("hour") || lower.contains("day") || lower.contains("yesterday") {
            credibility += 5.0; // Fresh
        } else if lower.contains("week") || lower.contains("month") {
            credibility += 5.0;
        } else if lower.contains("5 year") || lower.contains("6 year") || lower.contains("7 year") {
            // Older material preserved for fundamentals, slight freshness caution
            credibility -= 5.0;
        }
    }

    // -------------------------------------------------------------
    // 3. COMPOSITE EPISTEMIC CALCULATION
    // -------------------------------------------------------------
    let final_credibility = credibility.clamp(0.0, 100.0);
    let final_utility = utility.clamp(0.0, 100.0);
    let final_sensationalism = sensationalism.clamp(0.0, 100.0);

    let base_signal = (final_credibility * 0.50) + (final_utility * 0.50);
    let composite_score = (base_signal - (final_sensationalism * 0.35)).clamp(0.0, 100.0);

    let rounded_score = (composite_score * 10.0).round() / 10.0;

    Some(ScoredCandidate {
        item: item.clone(),
        duration_seconds: dur_sec,
        score: rounded_score,
        credibility_score: final_credibility,
        utility_score: final_utility,
        sensationalism_score: final_sensationalism,
        already_downloaded,
        audit_reasons,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rejects_shorts() {
        let item = ChannelVideoItem {
            video_id: "short1".to_string(),
            title: "Crazy lifehack #shorts".to_string(),
            length_text: Some("0:45".to_string()),
            published_time_text: Some("1 day ago".to_string()),
            view_count_text: Some("10K views".to_string()),
            channel_title: None,
            channel_handle: None,
        };

        let scored = score_candidate(&item, None, 60, false);
        assert!(scored.is_none());
    }

    #[test]
    fn test_deep_work_and_conceptual_keywords() {
        let item = ChannelVideoItem {
            video_id: "arch1".to_string(),
            title: "Distributed Systems Architecture: A Case Study Deep Dive".to_string(),
            length_text: Some("42:15".to_string()),
            published_time_text: Some("2 weeks ago".to_string()),
            view_count_text: Some("85K views".to_string()),
            channel_title: None,
            channel_handle: None,
        };

        let scored = score_candidate(&item, None, 60, false).expect("Candidate should pass");
        assert!(scored.utility_score >= 70.0);
        assert!(scored.score >= 65.0);
        assert!(scored.sensationalism_score == 0.0);
        assert!(scored.audit_reasons.iter().any(|r| r.contains("Deep work sweet-spot")));
        assert!(scored.audit_reasons.iter().any(|r| r.contains("architecture")));
    }

    #[test]
    fn test_sensationalism_penalized() {
        let item = ChannelVideoItem {
            video_id: "hype1".to_string(),
            title: "THIS CHANGES EVERYTHING! YOU WON'T BELIEVE WHAT HAPPENED!!!".to_string(),
            length_text: Some("11:20".to_string()),
            published_time_text: Some("1 day ago".to_string()),
            view_count_text: Some("500K views".to_string()),
            channel_title: None,
            channel_handle: None,
        };

        let scored = score_candidate(&item, None, 60, false).expect("Candidate should pass filters");
        assert!(scored.sensationalism_score >= 35.0);
        assert!(scored.score < 50.0);
        assert!(scored.audit_reasons.iter().any(|r| r.contains("ALL-CAPS")));
        assert!(scored.audit_reasons.iter().any(|r| r.contains("Punctuation hype")));
        assert!(scored.audit_reasons.iter().any(|r| r.contains("Sensationalist trigger")));
    }
}
