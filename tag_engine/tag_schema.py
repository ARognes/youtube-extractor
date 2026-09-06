"""
tag_schema.py

Data structures and validation models for the 3-Tier Tagging Architecture:
1. First-Order Tags: Video-Bound (specific to individual video instances)
2. Second-Order Tags: Channel-Bound (thematic pillars & signature creator vocabulary)
3. Third-Order Tags: Unbound / Global (universal conceptual nodes with no channel bounds)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class FirstOrderTag:
    """Video-bound tag tied to a specific video ID and timestamp segment."""
    tag: str
    video_id: str
    dimension: str              # concept, pain_point, protocol, modality
    timestamps: List[str]       # ["04:15", "12:30"]
    context_snippet: str

@dataclass
class SecondOrderTag:
    """Channel-bound tag defining a creator's core domain pillar or style."""
    tag: str
    channel: str
    dimension: str              # domain, concept, pain_point, protocol, modality
    occurrences: int
    prevalence_pct: float
    top_co_occurring: List[str]

@dataclass
class ThirdOrderTag:
    """Universal, unbound tag connecting concepts across all channels and topics."""
    tag: str
    name: str
    category: str               # ontology_category (e.g. Cognitive Mechanism, Interpersonal Dynamic)
    description: str
    second_order_links: List[str]   # Associated channel-bound tags
    first_order_count: int          # Total video hits across entire corpus

@dataclass
class VideoTagRecord:
    """Per-video tagging record in tag_silo/<channel>/videos/<video_id>.yaml"""
    video_id: str
    title: str
    channel: str
    url: str
    duration: str
    word_count: int
    first_order_tags: List[Dict[str, Any]]
    second_order_tags: List[str]
    third_order_tags: List[str]
    key_phrases: List[str]
    summary_hook: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ChannelTaxonomy:
    """Channel-bound tag taxonomy (Second-Order)."""
    channel: str
    total_videos_analyzed: int
    total_spoken_words: int
    second_order_tags: Dict[str, Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
