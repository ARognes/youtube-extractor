#!/usr/bin/env python3
"""
build_channel_tag_silo.py

Compiles a 3-Tier Tagging Hierarchy from `formatted_transcripts/`:
1. First-Order Tags: Video-Bound (specific timestamps and video context)
2. Second-Order Tags: Channel-Bound (creator thematic pillars and vocabulary)
3. Third-Order Tags: Unbound / Global (universal conceptual nodes across all channels)

Knowledge Cores Supported:
- Cognitive Psychology & Contemplative Science (HealthyGamerGG, TheraminTrees)
- Software Engineering & Systems (ThePrimeagen, Web Dev Simplified, freeCodeCamp.org, A Life Engineered)

Exports:
- `tag_silo/<channel_slug>/videos/<video_id>.yaml` (Per-video tag records)
- `tag_silo/<channel_slug>/channel_taxonomy.yaml` (Second-order channel taxonomy)
- `tag_silo/<channel_slug>/inverted_tag_index.json` (Tag -> [video_ids, timestamps])
- `tag_silo/<channel_slug>/channel_tag_report.md` (Executive report)
- `tag_silo/third_order_unbound_tags.yaml` (Third-order global tags)
- `tag_silo/tag_hierarchy_manifest.json` (D3.js graph manifest for SvelteKit SPA)
"""

import os
import sys
import json
import yaml
import re
import argparse
from collections import defaultdict, Counter
from datetime import datetime

try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

class CleanDumper(SafeDumper):
    pass

def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

CleanDumper.add_representer(str, str_representer)

SCRATCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMATTED_DIR = os.path.join(SCRATCH_DIR, 'formatted_transcripts')
TAG_SILO_ROOT = os.path.join(SCRATCH_DIR, 'tag_silo')

THERAMINTREES_TITLES = {
    "jWLZfeKpIhg": "losing (part 1) | relationship autopsy & parental narcissism",
    "xFt_aeQw2GA": "concealing abuse | family denial & systemic protection",
    "6F58ZJt_qYU": "exposing abuse (part 2) | the fallout of truth-telling",
    "TsvJMlg_SaM": "exposing abuse (part 1) | breaking the silence",
    "c39F04inLJ0": "infantilisation | forced dependency & preventing adulthood",
    "oX3qM4VqbJo": "nobody's follower | reclaiming self-sovereignty & leaving groups",
    "sXcTIkuzQ3I": "save | deconstructing the messiah & rescue complex",
    "u91ctugBCsg": "compelled love / weaponised love | love as emotional debt",
    "zcRUj8H3rc4": "death of a narcissist | grief without reconciliation",
    "kMeehIpxH5k": "abuse in therapy | predatory dynamics & ethical boundaries",
    "vnSiJOOdo30": "what we look for | attraction, trauma bonding & compatibility",
    "qjZ3f-IXEXU": "bowing to narcissists | appeasement & institutional enabling",
    "PEexQAkhFpM": "resisting emotional blackmail | boundaries against fog",
    "K4YZoNxSZNU": "living with abusers | survival tactics in hostile environments",
    "mdDAHekq9yc": "giving up on fixing people | accepting unchangeable dynamics",
    "OsAaxOFOUl4": "moral values | developing autonomous ethical frameworks",
    "o1G4JFuLlO8": "rumination | cognitive loops, injustice & breaking mental replay",
    "YIQocoxv5tg": "copying enemies | adopting abusive tactics to survive",
    "sUazbGC_XI4": "double-binds | communicative traps & guaranteed failure",
    "Cx4GvzjRMx8": "tribalism | in-group dogmatism & cognitive isolation",
    "e-2WZsP6LA0": "false equivalence | neutralizing abuse through both-sides fallacy",
    "o6-Htscvf4k": "dogmatism & indoctrination | deconstructing authoritarian control",
    "XSShv4lhgKQ": "shame & guilt | weaponized conscience & reclaiming autonomy",
    "NkLM8HTYY1g": "destructive relationships | how people get trapped",
    "YqnCwp9Ia68": "imaginary flaws | projected defects & invalidation",
    "4D5tZoF8cC4": "impersonation & boundary defense | direct channel memo"
}

# ==============================================================================
# Third-Order Global Unbound Tag Ontologies (Cross-Core Meta Taxonomy)
# ==============================================================================
THIRD_ORDER_UNBOUND_ONTOLOGY = {
    "T3_AUTONOMY_SOVEREIGNTY": {
        "name": "Autonomy & Cognitive Sovereignty",
        "core": "core_psychology",
        "category": "Foundational Epistemology",
        "description": "The fundamental capacity of an individual for self-governance, independent thought, and resistance to external psychological coercion.",
        "second_order_mapping": [
            "cognitive_autonomy_and_individuation",
            "relational_ethics_and_boundaries",
            "boundary_assertion_without_defense"
        ]
    },
    "T3_EMOTIONAL_METABOLISM": {
        "name": "Emotional Digestion & Somatic Metabolism",
        "core": "core_psychology",
        "category": "Somatic & Contemplative Science",
        "description": "The physiological processing of undigested affective distress (Samskaras) without cognitive rationalization or behavioral avoidance.",
        "second_order_mapping": [
            "samskara_emotional_memory",
            "somatic_emotional_digestion",
            "dissociation_and_derealization",
            "alexithymia_emotional_disconnect"
        ]
    },
    "T3_POWER_ASYMMETRY_MANIPULATION": {
        "name": "Power Asymmetry & Covert Exploitation",
        "core": "core_psychology",
        "category": "Interpersonal & Systemic Dynamics",
        "description": "Communicative and relational structures where authority or emotional leverage is abused to enforce dependency, compliance, or reality distortion.",
        "second_order_mapping": [
            "covert_psychological_manipulation",
            "double_bind_communicative_trap",
            "covert_narcissism_and_victimhood",
            "infantilisation_forced_dependency",
            "gaslighting_reality_denial",
            "fog_fear_obligation_guilt"
        ]
    },
    "T3_NEURODIVERGENCE_EXECUTIVE_FUNCTION": {
        "name": "Neurodivergence & Dopaminergic Regulation",
        "core": "cross_core",
        "category": "Neurobiology & Executive Function",
        "description": "Brain circuitry mechanics governing dopamine baselines, attention elasticity, task initiation friction, and burnout recovery.",
        "second_order_mapping": [
            "neurodivergence_and_adhd",
            "dopamine_baseline_and_receptors",
            "task_initiation_and_procrastination",
            "two_minute_frictionless_entry",
            "gifted_kid_burnout",
            "tutorial_hell_and_passive_consumption"
        ]
    },
    "T3_ATTACHMENT_RELATIONAL_BONDING": {
        "name": "Attachment Systems & Relational Projection",
        "core": "core_psychology",
        "category": "Developmental & Relational Psychology",
        "description": "Early mammalian attachment security, relational attunement, romantic pedestal projection, and the trauma of emotional abandonment.",
        "second_order_mapping": [
            "attachment_styles_anxious_avoidant",
            "limerence_and_pedestals",
            "unrequited_love_and_friendzone",
            "weaponised_and_compelled_love",
            "family_estrangement_and_grief"
        ]
    },
    "T3_SHAME_GUILT_EGO_PRESERVATION": {
        "name": "Ego Defense & Weaponized Conscience",
        "core": "cross_core",
        "category": "Identity & Moral Psychology",
        "description": "The deconstruction of false guilt, social compliance reflexes, ego identity (Ahamkara), and the recovery of authentic self-worth.",
        "second_order_mapping": [
            "ahamkara_ego_identity",
            "toxic_guilt_and_false_responsibility",
            "compulsive_people_pleasing_appeasement",
            "decoupling_worth_from_achievement",
            "imposter_syndrome",
            "lowballed_offer_fear",
            "terminal_senior_l5_plateau"
        ]
    },
    "T3_SYSTEM_ARCHITECTURE_PERFORMANCE": {
        "name": "Low-Level Systems & Runtime Performance",
        "core": "core_software_engineering",
        "category": "Systems & Computer Architecture",
        "description": "Memory models, hardware cache alignment, asynchronous execution primitives, and zero-cost abstraction design in modern systems programming.",
        "second_order_mapping": [
            "systems_programming_and_compilers",
            "runtime_internals_and_garbage_collection",
            "system_architecture_and_scale",
            "cache_locality_and_data_oriented_design",
            "zero_cost_abstractions",
            "type_system_soundness",
            "concurrency_primitives_and_locks",
            "mechanical_sympathy",
            "flamegraph_and_profiling_audit",
            "data_oriented_restructuring",
            "premature_abstraction_bloat",
            "garbage_collector_stop_the_world_latency"
        ]
    },
    "T3_DEVELOPER_ERGONOMICS_TOOLING": {
        "name": "Developer Ergonomics & Modal Workflow",
        "core": "core_software_engineering",
        "category": "Ergonomics & Productivity",
        "description": "Modal text manipulation (Vim/Neovim), Language Server Protocol (LSP) integrations, terminal multiplexing, and rapid tight feedback loops.",
        "second_order_mapping": [
            "editor_ergonomics_and_tooling",
            "modal_editing_velocity",
            "harpoon_buffer_navigation",
            "slow_developer_feedback_loops",
            "rebuilding_from_scratch_first_principles"
        ]
    },
    "T3_FULLSTACK_REACTIVITY_STATE": {
        "name": "Fullstack Reactivity & Component Architecture",
        "core": "core_software_engineering",
        "category": "Web Architecture & UX Engineering",
        "description": "Declarative component lifecycles, unidirectional state management, React Server Components (RSC), isomorphic rendering, and modern CSS layout algorithms.",
        "second_order_mapping": [
            "frontend_reactivity_and_frameworks",
            "modern_css_and_layouts",
            "typescript_and_type_safety",
            "backend_and_database_integration",
            "ai_application_engineering",
            "custom_hook_and_state_encapsulation",
            "server_components_and_isomorphic_rendering",
            "declarative_vs_imperative_ui",
            "form_validation_and_schema_parsing",
            "css_layout_algorithms",
            "unnecessary_re_renders",
            "prop_drilling_and_state_spaghetti",
            "compound_component_pattern",
            "rag_chunking_and_embedding_pipeline"
        ]
    },
    "T3_ENGINEERING_LEADERSHIP_LEVERAGE": {
        "name": "Staff+ Leadership, Promotion & Leverage",
        "core": "core_software_engineering",
        "category": "Organizational & Career Leverage",
        "description": "Staff/Principal engineering scope, executive stakeholder alignment, salary negotiation dynamics, and technical leverage.",
        "second_order_mapping": [
            "staff_plus_and_executive_leadership",
            "career_progression_and_promotion",
            "salary_negotiation_and_total_comp",
            "system_design_and_architecture_reviews",
            "workplace_politics_and_influence",
            "business_impact_over_code_output",
            "sponsorship_vs_mentorship",
            "the_l6_staff_archetype",
            "strategic_scope_expansion",
            "negotiation_anchoring_and_batna",
            "invisible_glue_work_undervaluation",
            "burnout_from_hero_mode",
            "one_page_brag_document",
            "skip_level_alignment_meeting",
            "competing_offer_leverage_play",
            "rfc_design_consensus_sprint"
        ]
    },
    "T3_ALGORITHMIC_COMPLEXITY_DATA_STRUCTURES": {
        "name": "Algorithmic Complexity & Foundations",
        "core": "core_software_engineering",
        "category": "Theoretical Computer Science",
        "description": "Asymptotic analysis, tree/graph traversal mechanics, dynamic programming subproblem caching, and distributed data structures.",
        "second_order_mapping": [
            "computer_science_fundamentals",
            "cloud_devops_and_infrastructure",
            "machine_learning_and_data_science",
            "cybersecurity_and_ethical_hacking",
            "asymptotic_algorithmic_complexity",
            "graph_and_tree_traversals",
            "containerization_and_orchestration",
            "transformer_attention_mechanisms",
            "relational_normalization_and_acid",
            "combinatorial_algorithm_exhaustion",
            "two_pointer_and_sliding_window",
            "memoization_and_tabulation",
            "dockerfile_multistage_build"
        ]
    }
}

# ==============================================================================
# Second-Order Channel Lexicons (Channel-Isolated Thematic Taxonomies)
# ==============================================================================
SECOND_ORDER_LEXICONS = {
    "healthygamergg": {
        "core": "core_psychology",
        "color": "#10b981",
        "domains": {
            "clinical_psychiatry": ["psychiatry", "psychiatrist", "diagnosis", "dsm", "antidepressant", "medication", "clinical", "disorder", "therapy", "therapist", "did", "derealization", "bipolar", "schizoid"],
            "eastern_contemplative_psychology": ["sanskrit", "ayurveda", "vedanta", "monk", "monastery", "samkhya", "karma", "dharma", "yoga", "meditation", "pranayama", "chakra", "ashram", "guru", "mindfulness", "hinduism", "buddhism"],
            "neurobiology_and_neurotransmitters": ["dopamine", "prefrontal cortex", "amygdala", "serotonin", "neurotransmitter", "receptor", "baseline", "circuit", "limbic", "neurological", "downregulation", "biology", "brain"],
            "relational_and_attachment_psychology": ["attachment", "attachment style", "dating", "relationship", "intimacy", "breakup", "limerence", "friendzone", "confession", "marriage", "partner", "love", "crush"],
            "addiction_and_behavioral_medicine": ["addiction", "gaming addiction", "relapse", "tolerance", "craving", "withdrawal", "compulsion", "detox", "sobriety", "porn", "video games", "screens"],
            "developmental_and_childhood_trauma": ["childhood", "traumatic childhood", "parents", "mother", "father", "neglect", "emotional abuse", "upbringing", "developmental", "inner child"]
        },
        "concepts": {
            "samskara_emotional_memory": ["samskara", "emotional scar", "undigested emotion", "emotional memory", "unprocessed emotion", "trauma memory", "past experience"],
            "sakshi_witness_consciousness": ["sakshi", "witness", "neutral observer", "observer stance", "observing self", "awareness itself", "unattached awareness", "watching your thoughts"],
            "ahamkara_ego_identity": ["ahamkara", "ego", "identity", "self-image", "pride", "ego defense", "reputation", "who you think you are"],
            "attachment_styles_anxious_avoidant": ["attachment style", "anxious attachment", "avoidant attachment", "secure attachment", "disorganized attachment", "fearful avoidant"],
            "dopamine_baseline_and_receptors": ["dopamine baseline", "dopamine detox", "tonic dopamine", "phasic dopamine", "dopaminergic", "pleasure pain balance", "reward pathway"],
            "neurodivergence_and_adhd": ["adhd", "attention deficit", "neurodivergent", "executive function", "hyperfocus", "dopamine deficiency", "stimulation seeking", "inattentive"],
            "alexithymia_emotional_disconnect": ["alexithymia", "identifying feelings", "naming emotions", "emotional blindness", "disconnect from feelings", "can't feel"],
            "limerence_and_pedestals": ["limerence", "obsessive crush", "pedestal", "idealization", "romantic obsession", "infatuation", "love addiction"],
            "dissociation_and_derealization": ["derealization", "depersonalization", "dissociation", "dissociative", "out of body", "foggy", "not real"],
            "defensive_intellectualization": ["intellectualizing", "intellectualization", "analyzing feelings", "thinking about feelings", "living in the head", "rationalizing"]
        },
        "pain_points": {
            "task_initiation_and_procrastination": ["can't start", "procrastination", "procrastinating", "putting it off", "paralyzed", "stuck in bed", "avoiding work", "avoidance", "lazy", "task paralysis"],
            "gifted_kid_burnout": ["gifted burnout", "fell behind", "used to be smart", "burned out", "failed potential", "lazy genius", "fear of effort", "effortless"],
            "unrequited_love_and_friendzone": ["unrequited", "confess your love", "can't stop thinking about her", "obsessed with him", "friendzone", "rejection", "rejected"],
            "existential_anhedonia_and_numbness": ["numb", "empty", "nothing brings joy", "anhedonia", "apathetic", "why bother", "lost meaning", "hollow", "flat"],
            "imposter_syndrome": ["imposter syndrome", "fraud", "exposed", "not qualified", "faking it", "luck", "worthless"],
            "compulsive_people_pleasing": ["people pleaser", "saying no", "guilty saying no", "approval seeker", "pleasing everyone", "conflict avoidant"],
            "chronic_loneliness_and_isolation": ["lonely", "no friends", "isolated", "can't connect", "alienated", "nobody understands", "isolation"],
            "parental_conflict_and_guilt": ["fix your traumatic", "parents", "mom and dad", "family conflict", "parental approval", "strict parents"]
        },
        "actionable_protocols": {
            "two_minute_frictionless_entry": ["two minute", "2 minute", "lower the friction", "start small", "micro step", "just open the book", "frictionless"],
            "somatic_emotional_digestion": ["digest the emotion", "sit with the feeling", "feel the sensation", "metabolize", "body sensation", "belly", "chest", "throat", "allow the feeling"],
            "dopamine_fast_sensory_reset": ["dopamine fast", "dopamine detox", "24 hour fast", "boredom is the cure", "remove screens", "sensory deprivation"],
            "pranayama_and_breathwork": ["pranayama", "nadi shodhana", "alternate nostril", "breath of fire", "box breathing", "inhalation", "exhalation", "breathing exercise"],
            "decoupling_worth_from_achievement": ["separate self worth", "worth from achievement", "not your grades", "outcome independent", "ego detachment", "unconditional worth"],
            "boundary_assertion_without_defense": ["set boundaries", "hold a boundary", "say no", "assertive", "stop overcorrecting"]
        },
        "modalities": {
            "live_client_interview": ["interview", "viewer", "talking with", "client", "let's welcome", "how are you doing", "thanks for coming on", "lucas", "coaching"],
            "case_study_trial_breakdown": ["trial", "case study", "breakdown by expert", "lindsay clancy", "forensic", "court", "psychiatric breakdown"],
            "clinical_lecture": ["in this video", "today we are going to understand", "psychiatry explains", "let's look at the brain", "neurologically", "dr. k", "healthy gamer"],
            "q_and_a_unpacking": ["chat says", "viewer writes", "reddit", "question from", "post on the subreddit", "community"]
        }
    },
    "theramintrees": {
        "core": "core_psychology",
        "color": "#f59e0b",
        "domains": {
            "systemic_family_therapy": ["family", "parent", "mother", "father", "childhood", "household", "sibling", "upbringing", "dynasty", "семей", "родител", "майка", "баща"],
            "covert_psychological_manipulation": ["manipulation", "manipulative", "covert", "control", "abusive", "predatory", "leverage", "tactics", "exploit", "манипул", "злоупотреб", "насил"],
            "dogmatic_indoctrination_and_cults": ["dogma", "indoctrination", "religion", "religious", "cult", "authoritarian", "ideology", "scripture", "belief system", "orthodoxy", "догм", "религи"],
            "cognitive_autonomy_and_individuation": ["autonomy", "sovereignty", "boundaries", "self-determination", "independent thought", "liberty", "agency", "автономи", "границ", "свобод"],
            "relational_ethics_and_boundaries": ["ethics", "moral", "reciprocity", "consent", "honesty", "exploitation", "fairness", "етик", "морал"]
        },
        "concepts": {
            "double_bind_communicative_trap": ["double-bind", "double bind", "no-win", "damned if you do", "contradictory demand", "catch-22", "impossible standard", "двойн"],
            "covert_narcissism_and_victimhood": ["covert narcissism", "narcissistic", "fragile narcissism", "victim playing", "self-absorbed", "martyr complex", "нарцис"],
            "fog_fear_obligation_guilt": ["emotional blackmail", "fog", "fear obligation guilt", "obligation", "guilt tripping", "emotional extortion", "изнудван", "дълг"],
            "infantilisation_forced_dependency": ["infantilisation", "infantilize", "infantile", "treating as a child", "forced dependency", "crippling independence", "инфантилиза"],
            "gaslighting_reality_denial": ["gaslighting", "gaslight", "reality denial", "question your sanity", "invented flaws", "rewriting history", "въображаем"],
            "weaponised_and_compelled_love": ["weaponised love", "compelled love", "love as debt", "conditional affection", "love bombing", "насилствена обич"],
            "false_equivalence_fallacy": ["false equivalence", "both sides", "neutralizing abuse", "equating victim with abuser", "фалшива еквивалентност"],
            "tribalism_and_in_group_isolation": ["tribalism", "in-group", "out-group", "echo chamber", "dogmatic isolation", "shunning", "трайб"]
        },
        "pain_points": {
            "toxic_guilt_and_false_responsibility": ["toxic guilt", "false guilt", "weaponized conscience", "guilty for existing", "guilty for boundaries", "irrational responsibility", "вина", "виновен"],
            "compulsive_people_pleasing_appeasement": ["people pleasing", "appeasement", "fawning", "placating", "walking on eggshells", "keeping the peace", "покланяне"],
            "family_estrangement_and_grief": ["estrangement", "cutting contact", "no contact", "leaving family", "bereavement", "death of a parent", "скръб", "смърт"],
            "cognitive_rumination_mental_loops": ["rumination", "ruminating", "mental loop", "replay", "obsessive replay", "unanswered grievance", "руминация", "мисловно предъвкване"],
            "loss_of_sovereignty_and_agency": ["trapped", "powerless", "helpless", "controlled", "micromanaged", "безпомощ"],
            "parental_invalidation_and_erasure": ["invalidation", "unheard", "dismissed", "denial", "scapegoat", "прикриване"]
        },
        "actionable_protocols": {
            "grey_rock_method_unreactivity": ["grey rock", "unreactive", "flatlining", "boring", "starve for fuel", "minimal response", "neutrality", "неутрал"],
            "anti_jade_boundaries": ["anti-jade", "do not justify", "don't defend", "no explanation", "declarative boundary", "firm refusal", "не се оправдавай"],
            "informational_starvation": ["informational diet", "withhold personal details", "share nothing vulnerable", "privacy protection", "информацион"],
            "giving_up_on_fixing_people": ["giving up on fixing", "accepting reality", "stop rehabilitating", "cannot change them", "abandon rescue fantasy", "откажи се"],
            "buffer_response_delay": ["let me check", "time buffer", "pause before answering", "refuse on-the-spot compliance", "време"]
        },
        "modalities": {
            "scripted_video_essay": ["video essay", "narrative", "in this essay", "let us examine", "scripted analysis", "есе"],
            "relationship_autopsy": ["relationship autopsy", "retrospective", "case study", "in part one", "in part two", "losing", "аутопсия"],
            "philosophical_deconstruction": ["deconstruction", "critique", "examining the dogma", "structural breakdown", "logical fallacy", "деконструкция"],
            "channel_editorial_memo": ["channel note", "memo", "update", "direct message to viewers", "alert"]
        }
    },
    "theprimeagen": {
        "core": "core_software_engineering",
        "color": "#ef4444",
        "domains": {
            "systems_programming_and_compilers": ["rust", "zig", "odin", "c++", "c language", "compiler", "llvm", "assembly", "memory safety", "borrow checker", "pointers", "segmentation fault", "libc"],
            "editor_ergonomics_and_tooling": ["neovim", "vim", "tmux", "terminal", "alacritty", "kitty", "lsp", "treesitter", "harpoon", "keybindings", "modal editing", "lua", "init.lua", "remap"],
            "runtime_internals_and_garbage_collection": ["v8", "javascript engine", "garbage collection", "jit", "heap", "stack", "call stack", "event loop", "node.js", "bun", "deno", "libuv"],
            "system_architecture_and_scale": ["distributed systems", "microservices", "monolith", "latency", "throughput", "concurrency", "threads", "async", "tokio", "database indexing", "redis"],
            "developer_culture_and_critique": ["code review", "software engineering", "tech lead", "junior vs senior", "netflix", "interview", "algorithm", "leet code", "clean code", "senior engineer"]
        },
        "concepts": {
            "cache_locality_and_data_oriented_design": ["cache locality", "cache line", "cpu cache", "l1 cache", "data-oriented", "dod", "memory layout", "struct of arrays", "array of structs", "branch prediction", "instruction cache"],
            "modal_editing_velocity": ["modal editing", "vim motions", "motion", "normal mode", "insert mode", "harpoon", "buffer", "telescope", "navigation", "keystroke"],
            "zero_cost_abstractions": ["zero cost", "zero-cost", "abstraction", "compile time", "monomorphization", "macros", "inlining", "codegen", "generics"],
            "type_system_soundness": ["type system", "strong typing", "type safety", "generics", "trait", "interface", "runtime safety", "undefined behavior", "soundness"],
            "concurrency_primitives_and_locks": ["mutex", "atomic", "rwlock", "deadlock", "race condition", "threads", "channel", "mpsc", "actor model", "thread safe"],
            "mechanical_sympathy": ["mechanical sympathy", "hardware", "cpu instructions", "simd", "registers", "syscall", "io bound", "cpu bound", "context switch"]
        },
        "pain_points": {
            "premature_abstraction_bloat": ["clean code", "over engineering", "abstraction", "oop", "design pattern", "inheritance", "solid principles", "bloat", "unnecessary complexity", "class hierarchy"],
            "garbage_collector_stop_the_world_latency": ["garbage collector", "gc pause", "stop the world", "memory leak", "memory pressure", "allocations", "churn", "gc pressure"],
            "slow_developer_feedback_loops": ["slow test", "slow build", "compile times", "ci cd lag", "sluggish ide", "lsp lag", "slow pipeline"],
            "framework_churn_fatigue": ["framework fatigue", "new js framework", "flavor of the month", "trend chasing", "deprecated", "churn"],
            "interview_leetcode_disconnect": ["leetcode", "coding interview", "whiteboarding", "reverse binary tree", "useless questions", "grind"]
        },
        "actionable_protocols": {
            "flamegraph_and_profiling_audit": ["flamegraph", "profiler", "perf", "valgrind", "benchmark", "criterion", "hyperfine", "profiling", "cpu profile"],
            "harpoon_buffer_navigation": ["harpoon", "jump buffer", "file navigation", "quickfix list", "fast editing", "fuzzy find"],
            "data_oriented_restructuring": ["soa", "data layout", "flattening data", "continuous memory", "linear scan", "cache friendly"],
            "rebuilding_from_scratch_first_principles": ["build from scratch", "first principles", "own engine", "handmade", "raw primitives", "from the ground up"]
        },
        "modalities": {
            "live_code_roast_critique": ["reaction", "roast", "reviewing", "drama", "reddit", "tier list", "prime reacts"],
            "deep_dive_benchmark_build": ["building", "coding", "live stream", "full tutorial", "from scratch", "deep dive", "implementing"],
            "engineering_philosophical_rant": ["hot take", "truth about", "why i left", "stop using", "the problem with", "rant"]
        }
    },
    "web_dev_simplified": {
        "core": "core_software_engineering",
        "color": "#3b82f6",
        "domains": {
            "frontend_reactivity_and_frameworks": ["react", "next.js", "vue", "svelte", "solidjs", "jsx", "tsx", "component", "virtual dom", "re-render", "props", "hook"],
            "modern_css_and_layouts": ["css", "flexbox", "grid", "container queries", "tailwind", "responsive design", "animations", "subgrid", "aspect-ratio", "variables", "css module"],
            "typescript_and_type_safety": ["typescript", "generics", "type inference", "union type", "zod", "utility types", "strict mode", "ts-node", "interface vs type"],
            "backend_and_database_integration": ["node", "express", "prisma", "drizzle", "postgresql", "mongodb", "sql", "api routes", "serverless", "rest", "trpc", "authentication"],
            "ai_application_engineering": ["rag", "ai agent", "langchain", "embeddings", "vector database", "openai", "claude", "prompt engineering", "llm", "semantic search"]
        },
        "concepts": {
            "custom_hook_and_state_encapsulation": ["custom hook", "useeffect", "usestate", "usememo", "usecallback", "usereducer", "context api", "derived state", "state management"],
            "server_components_and_isomorphic_rendering": ["rsc", "server components", "client components", "ssr", "ssg", "hydration", "streaming ssr", "suspense", "server actions"],
            "declarative_vs_imperative_ui": ["declarative", "imperative", "data flow", "unidirectional", "props", "event handler", "state driven"],
            "form_validation_and_schema_parsing": ["zod", "form validation", "react hook form", "controlled input", "uncontrolled input", "form action", "parse"],
            "css_layout_algorithms": ["flexbox", "css grid", "auto-fit", "auto-fill", "minmax", "clamp", "media query", "fr unit"]
        },
        "pain_points": {
            "unnecessary_re_renders": ["re-render", "infinite loop", "stale closure", "dependency array", "memory leak", "performance lag", "unnecessary render"],
            "prop_drilling_and_state_spaghetti": ["prop drilling", "global state mess", "over-complicating state", "redundant state", "context hell"],
            "css_specificity_and_cascade_wars": ["css specificity", "important tag", "broken layout", "z-index issues", "overflow hidden", "cascade"],
            "ai_hallucination_and_unsafe_execution": ["hallucination", "unsafe agent", "rag context overflow", "vector search inaccuracy", "injection"]
        },
        "actionable_protocols": {
            "compound_component_pattern": ["compound component", "slot pattern", "render props", "polymorphic component", "component composition"],
            "use_sync_external_store_migration": ["usesyncexternalstore", "subscribe", "store selector", "state management", "external store"],
            "clamp_fluid_responsive_system": ["clamp", "fluid typography", "fluid spacing", "responsive typography", "clamp formula"],
            "rag_chunking_and_embedding_pipeline": ["rag pipeline", "vector store", "chunking", "semantic search", "retrieval", "pinecone", "chromadb"]
        },
        "modalities": {
            "practical_project_build": ["how to build", "full course", "project", "step by step", "crash course", "from scratch", "clone"],
            "pattern_vs_antipattern_comparison": ["stop doing this", "do this instead", "cleanest way", "mistakes", "wrong way", "vs", "better way"],
            "feature_deep_dive": ["deep dive", "explained in 10 minutes", "everything you need to know", "cheat sheet", "guide"]
        }
    },
    "freecodecamp": {
        "core": "core_software_engineering",
        "color": "#06b6d4",
        "domains": {
            "computer_science_fundamentals": ["data structures", "algorithms", "big o", "graph theory", "trees", "sorting", "binary search", "dynamic programming", "recursion", "complexity"],
            "cloud_devops_and_infrastructure": ["docker", "kubernetes", "aws", "gcp", "azure", "linux", "bash", "networking", "ci/cd", "terraform", "nginx", "dns", "ip address"],
            "machine_learning_and_data_science": ["machine learning", "deep learning", "neural network", "transformer", "pytorch", "tensorflow", "python", "pandas", "numpy", "matplotlib", "scikit-learn"],
            "mobile_and_cross_platform_dev": ["flutter", "react native", "swift", "kotlin", "android", "ios", "dart", "xcode"],
            "cybersecurity_and_ethical_hacking": ["cybersecurity", "ethical hacking", "penetration testing", "cryptography", "burp suite", "wireshark", "security", "vulnerability", "sql injection"]
        },
        "concepts": {
            "asymptotic_algorithmic_complexity": ["time complexity", "space complexity", "big o notation", "o(n)", "o(log n)", "o(n^2)", "constant time", "linear time", "polynomial"],
            "graph_and_tree_traversals": ["bfs", "dfs", "breadth first", "depth first", "binary tree", "dijkstra", "a* algorithm", "adjacency list", "binary search tree", "avl tree"],
            "containerization_and_orchestration": ["container", "dockerfile", "image", "volume", "pod", "kubernetes cluster", "service mesh", "orchestration", "ingress"],
            "transformer_attention_mechanisms": ["attention is all you need", "self-attention", "transformer architecture", "tokens", "embedding layer", "multi-head attention", "encoder decoder"],
            "relational_normalization_and_acid": ["acid properties", "normalization", "sql schema", "foreign key", "primary key", "transactions", "index", "b-tree"]
        },
        "pain_points": {
            "tutorial_hell_and_passive_consumption": ["tutorial hell", "passive learning", "getting stuck", "can't code without tutorial", "imposter", "lost in code"],
            "combinatorial_algorithm_exhaustion": ["recursion stack overflow", "exponential time", "brute force failure", "edge case bugs", "time limit exceeded", "tle"],
            "infrastructure_misconfiguration": ["permission denied", "port conflict", "cors error", "environment variable leak", "downtime", "crash loop"]
        },
        "actionable_protocols": {
            "two_pointer_and_sliding_window": ["two pointer", "sliding window", "two pointers", "pointer technique", "array subarray", "window start"],
            "memoization_and_tabulation": ["dynamic programming", "memoization", "tabulation", "top down", "bottom up", "subproblems", "memo"],
            "dockerfile_multistage_build": ["multistage build", "minimal image", "alpine base", "layer caching", "multi-stage"],
            "semantic_chunking_tokenization": ["tokenization", "bpe", "wordpiece", "sliding window chunks", "token limit"]
        },
        "modalities": {
            "mega_crash_course": ["crash course", "full course", "complete course", "mastery course", "10 hour", "bootcamp", "handbook"],
            "visual_algorithm_walkthrough": ["visually", "visual guide", "animated", "step by step visual", "diagrams", "animation"],
            "paper_and_architecture_breakdown": ["paper that created", "breakdown", "research paper", "whitepaper", "explained", "anatomy of"]
        }
    },
    "a_life_engineered": {
        "core": "core_software_engineering",
        "color": "#8b5cf6",
        "domains": {
            "staff_plus_and_executive_leadership": ["staff engineer", "principal engineer", "director", "vp of engineering", "executive", "tech lead", "engineering management", "leadership", "cto", "ex-amazon vp"],
            "career_progression_and_promotion": ["promotion", "promo packet", "leveling", "l5 to l6", "l6 to l7", "senior engineer", "career ladder", "evaluations", "perf review", "calibration"],
            "salary_negotiation_and_total_comp": ["salary", "compensation", "equity", "rsu", "negotiation", "counter offer", "total comp", "signing bonus", "base salary", "stock options"],
            "system_design_and_architecture_reviews": ["system design", "design document", "rfc", "architecture review", "scalability tradeoffs", "tech debt", "reliability", "sla", "availability"],
            "workplace_politics_and_influence": ["stakeholder management", "office politics", "influence without authority", "managing up", "executive presence", "sponsors", "alignment"]
        },
        "concepts": {
            "business_impact_over_code_output": ["business impact", "revenue", "roi", "moving the needle", "bottom line", "outcomes over output", "high leverage", "strategic value"],
            "sponsorship_vs_mentorship": ["sponsor", "sponsorship", "advocate", "closed doors", "decision makers", "mentor vs sponsor", "career champion"],
            "the_l6_staff_archetype": ["archetype", "depth specialist", "systems architect", "problem solver", "glue engineer", "force multiplier", "multiplier"],
            "strategic_scope_expansion": ["scope expansion", "cross team", "org level", "multi team initiative", "unblocking teams", "organizational impact"],
            "negotiation_anchoring_and_batna": ["batna", "anchoring", "leverage", "competing offers", "multiple offers", "walk away price", "market rate"]
        },
        "pain_points": {
            "terminal_senior_l5_plateau": ["stuck at senior", "terminal level", "plateau", "can't reach staff", "hard to promote", "glass ceiling", "ceiling"],
            "invisible_glue_work_undervaluation": ["glue work", "unrecognized effort", "shadow work", "no promo credit", "thankless tasks", "glue"],
            "burnout_from_hero_mode": ["hero syndrome", "doing everything yourself", "single point of failure", "overworked", "delegation failure", "bottleneck"],
            "lowballed_offer_fear": ["lowball", "exploding offer", "afraid to ask", "imposter in negotiation", "leaving money on the table", "undervalued"]
        },
        "actionable_protocols": {
            "one_page_brag_document": ["brag doc", "brag document", "promo doc", "impact tracker", "weekly wins", "evidence log", "brag sheet"],
            "skip_level_alignment_meeting": ["skip level", "manager's manager", "director 1 on 1", "strategic alignment", "visibility", "skip 1:1"],
            "competing_offer_leverage_play": ["counter offer", "competing offer", "negotiate politely", "recruiter email template", "bracketed ask", "countering"],
            "rfc_design_consensus_sprint": ["rfc", "write a design doc", "consensus building", "architecture proposal", "pre-wire stakeholders", "design review"]
        },
        "modalities": {
            "executive_interview_mentorship": ["conversation", "interview", "vp", "director", "with ethan evans", "guest", "extended conversation"],
            "career_strategy_masterclass": ["how to get promoted", "how to negotiate", "how to become staff", "career advice", "guide", "framework"],
            "qa_salary_breakdown": ["salary breakdown", "critique", "live coaching", "q&a", "viewer question", "case study"]
        }
    }
}

def format_timestamp(seconds):
    try:
        s = int(round(float(seconds)))
        m, sec = divmod(s, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"
    except:
        return "00:00"

def parse_seconds_from_duration(dur_str):
    if not dur_str or dur_str == 'N/A':
        return 600.0
    dur_str = str(dur_str).strip()
    if 'min' in dur_str:
        try:
            return float(dur_str.replace('min', '').strip()) * 60.0
        except:
            pass
    parts = [int(p) for p in dur_str.split(':') if p.isdigit()]
    if len(parts) == 3:
        return float(parts[0] * 3600 + parts[1] * 60 + parts[2])
    elif len(parts) == 2:
        return float(parts[0] * 60 + parts[1])
    return 600.0

def extract_timestamps_and_segments(transcript_text, duration_sec):
    segments = []
    sec_matches = list(re.finditer(r'\[(\d+(?:\.\d+)?)s?\]', transcript_text))
    if len(sec_matches) > 5:
        for i, match in enumerate(sec_matches):
            t_sec = float(match.group(1))
            start_idx = match.end()
            end_idx = sec_matches[i+1].start() if i + 1 < len(sec_matches) else len(transcript_text)
            chunk = transcript_text[start_idx:end_idx].strip()
            if chunk:
                segments.append({
                    "seconds": t_sec,
                    "timestamp": format_timestamp(t_sec),
                    "text": chunk
                })
        return segments

    time_matches = list(re.finditer(r'\[(?:(\d+):)?(\d+):(\d+)\]', transcript_text))
    if len(time_matches) > 5:
        for i, match in enumerate(time_matches):
            h = int(match.group(1)) if match.group(1) else 0
            m = int(match.group(2))
            s = int(match.group(3))
            t_sec = float(h * 3600 + m * 60 + s)
            start_idx = match.end()
            end_idx = time_matches[i+1].start() if i + 1 < len(time_matches) else len(transcript_text)
            chunk = transcript_text[start_idx:end_idx].strip()
            if chunk:
                segments.append({
                    "seconds": t_sec,
                    "timestamp": format_timestamp(t_sec),
                    "text": chunk
                })
        return segments

    clean_text = re.sub(r'\[.*?\]', '', transcript_text).strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if len(s.strip()) > 15]
    if not sentences:
        sentences = [clean_text]
    sec_step = duration_sec / max(1, len(sentences))
    for i, sent in enumerate(sentences):
        t_sec = i * sec_step
        segments.append({
            "seconds": t_sec,
            "timestamp": format_timestamp(t_sec),
            "text": sent
        })
    return segments

def extract_key_phrases(transcript_text, top_n=6):
    clean = re.sub(r'\[.*?\]', ' ', transcript_text.lower())
    clean = re.sub(r'[^a-z0-9\s-]', ' ', clean)
    words = [w for w in clean.split() if len(w) > 3 and w not in {
        'that', 'this', 'with', 'from', 'have', 'were', 'which', 'about', 'there',
        'what', 'when', 'where', 'your', 'they', 'them', 'their', 'because', 'would',
        'could', 'should', 'people', 'going', 'really', 'think', 'know', 'like', 'just',
        'well', 'then', 'into', 'some', 'other', 'than', 'want', 'look', 'make', 'even',
        'music', 'snorts', 'here', 'right', 'also', 'something', 'doing'
    }]
    
    bigrams = []
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        if w1 != w2:
            bigrams.append(f"{w1} {w2}")
            
    counts = Counter(bigrams)
    return [phrase for phrase, _ in counts.most_common(top_n)]

def analyze_video_3tier(video_data, channel_slug, lexicon):
    transcript = video_data.get('transcript_text', '')
    title = video_data.get('title', '')
    dur_sec = parse_seconds_from_duration(video_data.get('duration'))
    combined_text = (title + " " + transcript).lower()

    segments = extract_timestamps_and_segments(transcript, dur_sec)

    matched_second_order = []
    first_order_tags = []
    matched_third_order = set()

    # Match Second-Order Tags
    for dim_name in ["domains", "concepts", "pain_points", "actionable_protocols", "modalities"]:
        dim_dict = lexicon.get(dim_name, {})
        for tag_name, keywords in dim_dict.items():
            hit = False
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', title.lower()):
                    matched_second_order.append(tag_name)
                    hit = True
                    break
            if hit:
                continue
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', combined_text):
                    matched_second_order.append(tag_name)
                    break

    # Contextual defaults if empty
    if not matched_second_order:
        default_map = {
            "healthygamergg": "clinical_lecture",
            "theramintrees": "scripted_video_essay",
            "theprimeagen": "engineering_philosophical_rant",
            "web_dev_simplified": "practical_project_build",
            "freecodecamp": "mega_crash_course",
            "a_life_engineered": "career_strategy_masterclass"
        }
        matched_second_order.append(default_map.get(channel_slug, "technical_analysis"))

    # Match First-Order Tags (Video-bound with timestamps)
    for seg in segments:
        seg_lower = seg["text"].lower()
        for t2 in matched_second_order:
            kw_list = []
            for d in ["concepts", "pain_points", "actionable_protocols"]:
                if t2 in lexicon.get(d, {}):
                    kw_list = lexicon[d][t2]
                    break
            if any(re.search(r'\b' + re.escape(kw) + r'\b', seg_lower) for kw in kw_list):
                snippet = seg["text"][:140] + ("..." if len(seg["text"]) > 140 else "")
                first_order_tags.append({
                    "tag": f"vtag_{t2}",
                    "bound_second_order": t2,
                    "timestamp": seg["timestamp"],
                    "seconds": round(seg["seconds"], 1),
                    "context": snippet
                })

    # Deduplicate first order tags per minute
    deduped_first_order = []
    seen = set()
    for fo in first_order_tags:
        k = (int(fo["seconds"] // 60), fo["bound_second_order"])
        if k not in seen:
            seen.add(k)
            deduped_first_order.append(fo)
        if len(deduped_first_order) >= 15:
            break

    # Resolve Third-Order Unbound Tags
    second_set = set(matched_second_order)
    for t3_id, t3_meta in THIRD_ORDER_UNBOUND_ONTOLOGY.items():
        if any(s2 in second_set for s2 in t3_meta["second_order_mapping"]):
            matched_third_order.add(t3_id)

    key_phrases = extract_key_phrases(transcript, top_n=6)
    summary_hook = f"Explores {', '.join(matched_second_order[:3])}."

    return {
        "video_id": video_data.get("video_id"),
        "title": title,
        "channel": video_data.get("channel"),
        "url": video_data.get("url"),
        "duration": video_data.get("duration"),
        "word_count": video_data.get("word_count"),
        "first_order_tags": deduped_first_order,
        "second_order_tags": sorted(list(set(matched_second_order))),
        "third_order_tags": sorted(list(matched_third_order)),
        "key_phrases": key_phrases,
        "summary_hook": summary_hook
    }

def process_channels():
    os.makedirs(TAG_SILO_ROOT, exist_ok=True)
    target_channels = [
        ("healthygamergg", ["healthygamergg"]),
        ("theramintrees", ["theramintrees"]),
        ("theprimeagen", ["theprimeagen"]),
        ("web_dev_simplified", ["web dev simplified"]),
        ("freecodecamp", ["freecodecamp.org", "freecodecamp"]),
        ("a_life_engineered", ["a life engineered"])
    ]

    all_channel_records = {}
    manifest_nodes = []
    manifest_links = []

    # 1. Add Third-Order Unbound Nodes to Graph
    for t3_id, t3_meta in THIRD_ORDER_UNBOUND_ONTOLOGY.items():
        manifest_nodes.append({
            "id": t3_id,
            "label": t3_meta["name"],
            "order": 3,
            "core": t3_meta.get("core", "cross_core"),
            "category": t3_meta["category"],
            "description": t3_meta["description"],
            "radius": 24,
            "color": "#a855f7" # Purple core
        })

    # Single-pass scan over all formatted transcripts
    print("⚡ Performing single-pass transcript scan across formatted_transcripts...", flush=True)
    channel_video_buckets = defaultdict(list)
    all_files = sorted([f for f in os.listdir(FORMATTED_DIR) if f.endswith('.yaml')])

    for fn in all_files:
        fp = os.path.join(FORMATTED_DIR, fn)
        with open(fp, 'r', encoding='utf-8') as yf:
            header_lines = [yf.readline() for _ in range(12)]
            header_str = ''.join(header_lines).lower()
            
            matched_slug = None
            for slug, qkeys in target_channels:
                if any(qk in header_str for qk in qkeys):
                    matched_slug = slug
                    break
            if not matched_slug:
                continue

            yf.seek(0)
            data = yaml.load(yf, Loader=SafeLoader)
            ch = (data.get('channel') or '').strip().lower()
            
            # verify matching
            valid = False
            for slug, qkeys in target_channels:
                if slug == matched_slug and any(qk in ch for qk in qkeys):
                    valid = True
                    break
            if not valid:
                continue

            vid_id = data.get('video_id', '')
            title = data.get('title', '')
            if matched_slug == 'theramintrees' and vid_id in THERAMINTREES_TITLES:
                title = THERAMINTREES_TITLES[vid_id]
            elif 'TheraminTrees Video Essay' in title and vid_id in THERAMINTREES_TITLES:
                title = THERAMINTREES_TITLES[vid_id]

            tr = data.get('transcript') or ''
            if isinstance(tr, str) and tr.startswith('{"content":'):
                try:
                    inner = json.loads(tr)
                    tr_text = inner.get('content', '')
                except:
                    tr_text = tr
            else:
                tr_text = str(tr)

            channel_video_buckets[matched_slug].append({
                "video_id": vid_id,
                "title": title,
                "channel": data.get('channel'),
                "url": data.get('url') or f"https://www.youtube.com/watch?v={vid_id}",
                "duration": data.get('duration', 'N/A'),
                "word_count": len(tr_text.split()),
                "transcript_text": tr_text
            })

    total_all_videos = 0
    total_all_words = 0

    for channel_slug, _ in target_channels:
        matched_videos = channel_video_buckets.get(channel_slug, [])
        print(f"\n=======================================================", flush=True)
        print(f"🚀 Processing 3-Tier Tag Silo for: '{channel_slug.upper()}' ({len(matched_videos)} videos)", flush=True)
        print(f"=======================================================", flush=True)

        channel_dir = os.path.join(TAG_SILO_ROOT, channel_slug)
        videos_dir = os.path.join(channel_dir, 'videos')
        os.makedirs(videos_dir, exist_ok=True)

        lexicon = SECOND_ORDER_LEXICONS.get(channel_slug, {})
        channel_color = lexicon.get("color", "#64748b")
        channel_core = lexicon.get("core", "core_general")

        tag_counts = defaultdict(int)
        inverted_index = defaultdict(list)
        total_words = 0
        channel_records = []

        for vdata in matched_videos:
            rec = analyze_video_3tier(vdata, channel_slug, lexicon)
            channel_records.append(rec)
            total_words += rec["word_count"]

            # Save per-video YAML record
            v_yaml_path = os.path.join(videos_dir, f"{rec['video_id']}.yaml")
            with open(v_yaml_path, 'w', encoding='utf-8') as vf:
                yaml.dump(rec, vf, Dumper=CleanDumper, sort_keys=False, allow_unicode=True)

            # Inverted Index & Counts
            for t2 in rec["second_order_tags"]:
                tag_counts[t2] += 1
                ts_list = [fo["timestamp"] for fo in rec["first_order_tags"] if fo["bound_second_order"] == t2]
                inverted_index[t2].append({
                    "video_id": rec["video_id"],
                    "title": rec["title"],
                    "timestamps": ts_list
                })

        all_channel_records[channel_slug] = channel_records
        total_all_videos += len(matched_videos)
        total_all_words += total_words

        # Second-Order Channel Taxonomy
        taxonomy = {
            "channel": channel_slug,
            "core": channel_core,
            "order": 2,
            "scope": "channel_bound",
            "total_videos_analyzed": len(matched_videos),
            "total_spoken_words": total_words,
            "compiled_at": datetime.now().isoformat(),
            "second_order_tags": {}
        }

        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            prevalence = round((count / max(1, len(matched_videos))) * 100, 1)
            taxonomy["second_order_tags"][tag] = {
                "tag": tag,
                "channel": channel_slug,
                "video_occurrences": count,
                "prevalence_pct": prevalence
            }

            # Add Second-Order Node to Manifest
            t2_node_id = f"{channel_slug}:{tag}"
            manifest_nodes.append({
                "id": t2_node_id,
                "label": tag.replace("_", " ").title(),
                "order": 2,
                "channel": channel_slug,
                "core": channel_core,
                "occurrences": count,
                "prevalence": prevalence,
                "radius": max(10, min(22, count // 2 + 6)),
                "color": channel_color
            })

            # Link Second-Order to Third-Order
            for t3_id, t3_meta in THIRD_ORDER_UNBOUND_ONTOLOGY.items():
                if tag in t3_meta["second_order_mapping"]:
                    manifest_links.append({
                        "source": t3_id,
                        "target": t2_node_id,
                        "type": "unbound_to_channel",
                        "value": 2
                    })

        tax_path = os.path.join(channel_dir, 'channel_taxonomy.yaml')
        with open(tax_path, 'w', encoding='utf-8') as tf:
            yaml.dump(taxonomy, tf, Dumper=CleanDumper, sort_keys=False, allow_unicode=True)

        inv_path = os.path.join(channel_dir, 'inverted_tag_index.json')
        with open(inv_path, 'w', encoding='utf-8') as jf:
            json.dump({
                "channel": channel_slug,
                "core": channel_core,
                "total_tags": len(inverted_index),
                "index": inverted_index
            }, jf, indent=2)

        # Sample First-Order Video Nodes into Graph (Top 12 per channel for crisp rendering)
        sample_vids = sorted(channel_records, key=lambda x: -x["word_count"])[:12]
        for v in sample_vids:
            v_node_id = f"vid:{v['video_id']}"
            manifest_nodes.append({
                "id": v_node_id,
                "label": v["title"][:28] + "...",
                "full_title": v["title"],
                "order": 1,
                "channel": channel_slug,
                "core": channel_core,
                "duration": v["duration"],
                "url": v["url"],
                "radius": 6,
                "color": "#38bdf8"
            })
            for t2 in v["second_order_tags"][:3]:
                manifest_links.append({
                    "source": f"{channel_slug}:{t2}",
                    "target": v_node_id,
                    "type": "channel_to_video",
                    "value": 1
                })

    # 3. Export Third-Order Unbound Tags YAML
    t3_export_path = os.path.join(TAG_SILO_ROOT, 'third_order_unbound_tags.yaml')
    with open(t3_export_path, 'w', encoding='utf-8') as yf:
        yaml.dump({
            "order": 3,
            "scope": "global_unbound",
            "compiled_at": datetime.now().isoformat(),
            "total_unbound_tags": len(THIRD_ORDER_UNBOUND_ONTOLOGY),
            "unbound_tags": THIRD_ORDER_UNBOUND_ONTOLOGY
        }, yf, Dumper=CleanDumper, sort_keys=False, allow_unicode=True)

    # 4. Export Combined Tag Hierarchy Graph Manifest for SvelteKit D3 SPA
    manifest_data = {
        "compiled_at": datetime.now().isoformat(),
        "summary": {
            "total_cores": 2,
            "third_order_count": len(THIRD_ORDER_UNBOUND_ONTOLOGY),
            "channels_indexed": len(target_channels),
            "total_videos_analyzed": total_all_videos,
            "total_words_analyzed": total_all_words,
            "total_nodes": len(manifest_nodes),
            "total_links": len(manifest_links)
        },
        "third_order_ontology": THIRD_ORDER_UNBOUND_ONTOLOGY,
        "nodes": manifest_nodes,
        "links": manifest_links
    }

    manifest_path = os.path.join(TAG_SILO_ROOT, 'tag_hierarchy_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as jf:
        json.dump(manifest_data, jf, indent=2)

    # Also sync directly to visualizer/src/lib/ and visualizer/static/
    vis_lib_path = os.path.join(SCRATCH_DIR, 'visualizer', 'src', 'lib', 'tag_hierarchy_manifest.json')
    vis_static_path = os.path.join(SCRATCH_DIR, 'visualizer', 'static', 'tag_hierarchy_manifest.json')
    if os.path.exists(os.path.dirname(vis_lib_path)):
        with open(vis_lib_path, 'w', encoding='utf-8') as jf:
            json.dump(manifest_data, jf, indent=2)
    if os.path.exists(os.path.dirname(vis_static_path)):
        with open(vis_static_path, 'w', encoding='utf-8') as jf:
            json.dump(manifest_data, jf, indent=2)

    print(f"\n✅ 3-Tier Tagging Hierarchy compiled successfully across all Knowledge Cores!")
    print(f" - Analyzed {total_all_videos} videos across {len(target_channels)} channels ({total_all_words:,} words)")
    print(f" - Third-Order Global Tags: {t3_export_path}")
    print(f" - D3 Graph Manifest for SPA: {manifest_path} ({len(manifest_nodes)} nodes, {len(manifest_links)} links)")

if __name__ == '__main__':
    process_channels()
