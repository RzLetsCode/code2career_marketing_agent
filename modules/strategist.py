import os
import json
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from openai import AzureOpenAI

from config.settings import settings
from core.logger import logger


class Slide(BaseModel):
    slide_num: int = Field(description="Sequential slide number (1 to 5)")
    tag: str = Field(description="Short technical category tag, e.g. 'STAGE 01 // INGESTION'")
    headline: str = Field(description="Punchy architectural headline (max 7 words)")
    content: str = Field(description="Granular engineering explanation for carousel & inspector (25-40 words)")
    voiceover: str = Field(
        default="",
        description="Natural spoken narration structured in two beats: Beat 1 states the naive bottleneck/problem; Beat 2 explains the exact architectural or mathematical fix."
    )
    # --- Designer / Playwright Compatibility Fields ---
    left_column_points: Optional[List[str]] = Field(default=None, description="Optional bullet points for left designer column")
    right_column_points: Optional[List[str]] = Field(default=None, description="Optional bullet points for right designer column")

    # --- Human-Like Storyboard Director Fields (Populated dynamically by Azure OpenAI) ---
    visual_archetype: str = Field(
        default="topology_flow",
        description="Must be one of: 'topology_flow' | 'vector_subspace' | 'probability_dist' | 'scaling_curve' | 'token_stream' | 'storage_tiers'"
    )
    visual_nodes: List[str] = Field(
        default_factory=lambda: ["API Gateway", "Worker Pool", "Vector DB", "LLM Sink"],
        description="4 specific technical component or tensor names from THIS slide's topic (max 16 chars each)"
    )
    metric_label: str = Field(
        default="P99 Latency",
        description="Specific engineering or mathematical metric being measured (e.g. 'P99 Latency', 'Cosine Sim', 'VRAM Usage', 'Throughput')"
    )
    metric_before: str = Field(
        default="840 ms (Bottleneck)",
        description="Realistic naive/broken metric value before optimization (Beat 1)"
    )
    metric_after: str = Field(
        default="18 ms (Optimized)",
        description="Realistic production metric value after applying the fix (Beat 2)"
    )
    math_formula: str = Field(
        default="Latency: O(N^2) -> O(log N)",
        description="Clean ASCII/Unicode mathematical equation or complexity formula governing this stage"
    )


class CarouselPost(BaseModel):
    topic: str = Field(description="High-converting, deeply technical engineering title")
    pillar: str = Field(description="Content pillar, e.g. 'Architecture Teardown', 'AI Math Explained', 'Production RAG'")
    trigger_keyword: str = Field(description="Single uppercase word for DM automation trigger, e.g. 'RAGSCALE'")
    caption: str = Field(description="Engaging LinkedIn/Instagram caption with architectural insights and hashtags")
    slides: List[Slide] = Field(description="Exactly 5 sequential technical slides")


class MarketingStrategist:
    """
    Formulates high-converting technical carousels AND acts as a Human-Like Technical Video Director,
    designing custom per-slide visual storyboards, component topologies, and before/after telemetry.
    """

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=getattr(
                settings,
                "azure_openai_api_version",
                os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            ),
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.deployment = (
            getattr(settings, "azure_openai_deployment_name", None)
            or getattr(settings, "azure_openai_deployment", None)
            or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
        )

    def formulate_carousel(self, market_signals: Any, past_topics: Optional[List[str]] = None) -> CarouselPost:
        logger.info(f"Strategist Brain ({self.deployment}): Formulating CRO carousel & bespoke Manim visual storyboard...")
        past_topics = past_topics or []
        history_block = "\n".join(f"- {t}" for t in past_topics[-25:]) if past_topics else "None"

        if isinstance(market_signals, (list, dict)):
            signals_block = json.dumps(market_signals, indent=2, ensure_ascii=False)
        else:
            signals_block = str(market_signals)

        system_prompt = """You are a Principal Enterprise AI Architect and Technical Animation Director (inspired by 3Blue1Brown and ByteByteGo).
Your job is to transform live developer engineering trends into a 5-slide deep-dive architectural teardown for Code2Career_AI.

CRITICAL RULES FOR HUMAN-LIKE VIDEO STORYBOARDING:
1. CHOOSE ARCHITECTURE- & MATH-RICH TOPICS: Prioritize topics involving concrete data flows, distributed systems, RAG bottlenecks, agent state machines, LLM inference mechanics, or AI mathematics.
2. TWO-BEAT CONVERSATIONAL VOICEOVER (`voiceover`):
   - Write each slide's `voiceover` (25 to 38 words) as a natural, insightful architect speaking to peers.
   - Structure every slide's voiceover in TWO distinct narrative beats:
     * First half (Beat 1): Explain what breaks in naive implementations (the bottleneck, mathematical explosion, or failure mode).
     * Second half (Beat 2): Explain the exact production mechanism or mathematical transformation that fixes it.
3. BESPOKE VISUAL ARCHETYPES (`visual_archetype`):
   - Never use the same `visual_archetype` on two consecutive slides! Pick the best match for each slide's exact mechanics from:
     * `topology_flow`: Distributed microservice/agent routing with live packets, bottleneck stall vs async bypass.
     * `vector_subspace`: 2D/3D geometric vector projection, cosine angle alignment, embedding drift, or subspace clustering.
     * `probability_dist`: Softmax attention weights, cross-encoder reranking histograms, or token sampling distributions morphing from noisy to sharp.
     * `scaling_curve`: Live coordinate axes comparing quadratic O(N^2) explosion against logarithmic/linear O(log N) optimization.
     * `token_stream`: Sliding context windows, KV-cache tensor blocks, chunk boundary overlap, or quantization bit-packing.
     * `storage_tiers`: Hot/Warm/Cold memory hierarchy (e.g. L1 Redis Semantic Cache -> HNSW Vector Index -> Cold Object Store).
4. CUSTOM TOPIC-SPECIFIC NODES & TELEMETRY:
   - `visual_nodes`: Provide 4 REAL, SPECIFIC component names from that slide (e.g., ["Query Parser", "Redis Stream", "HNSW Shard", "Cross-Encoder"] — NEVER generic labels like "Stage 1" or "Box 1"). Max 16 characters per label.
   - `metric_label`, `metric_before`, `metric_after`: Provide realistic quantitative telemetry showing the Beat 1 problem morphing into the Beat 2 fix (e.g. metric_label="P99 Latency", metric_before="1,420 ms (HTTP 429)", metric_after="24 ms (Async Queue)").
   - `math_formula`: Provide a clean Unicode mathematical equation or complexity relation (use Unicode symbols like θ, Σ, Δ, λ, ×, ÷, ², ≈, ->; do NOT use raw LaTeX backslashes).

Return strictly valid JSON matching this exact structure:
{
  "topic": "string",
  "pillar": "string",
  "trigger_keyword": "UPPERCASE_WORD",
  "caption": "string",
  "slides": [
    {
      "slide_num": 1,
      "tag": "STAGE 01 // ...",
      "headline": "string",
      "content": "string",
      "voiceover": "string",
      "visual_archetype": "topology_flow | vector_subspace | probability_dist | scaling_curve | token_stream | storage_tiers",
      "visual_nodes": ["Node1", "Node2", "Node3", "Node4"],
      "metric_label": "string",
      "metric_before": "string",
      "metric_after": "string",
      "math_formula": "string"
    }
  ]
}"""

        user_prompt = f"""LIVE ENGINEERING SIGNALS TODAY:
{signals_block}

ALREADY PUBLISHED TOPICS (DO NOT REPEAT):
{history_block}

Generate the 5-slide CarouselPost JSON object now."""

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.65,
        )

        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)
        carousel = CarouselPost(**data)
        logger.info(
            f"Generated CRO Topic: '{carousel.topic}' | Keyword Trigger: {carousel.trigger_keyword} | "
            f"Archetypes: {[s.visual_archetype for s in carousel.slides]}"
        )
        return carousel