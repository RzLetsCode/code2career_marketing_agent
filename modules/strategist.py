from typing import List, Optional
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import settings
from core.logger import logger


class Slide(BaseModel):
    slide_num: int = Field(description="Slide index from 1 to 5")
    tag: str = Field(description="Uppercase badge, e.g., 'THE HARSH TRUTH', 'THE JUNIOR TRAP', 'ARCHITECTURE MATRIX', 'PRODUCTION BLUEPRINT', 'ACTION'")
    headline: str = Field(description="Bold hook, strictly 6 words maximum")
    content: str = Field(description="Direct, high-density takeaway. Max 26 words.")
    # Structured fields for Slide 3 high-save comparison matrix
    left_column_title: Optional[str] = Field(default=None, description="E.g., 'TOY TUTORIAL (REJECTED)'")
    left_column_points: Optional[List[str]] = Field(default=None, description="2 bullet points of failure/naive patterns")
    right_column_title: Optional[str] = Field(default=None, description="E.g., 'ENTERPRISE PATTERN (HIRED)'")
    right_column_points: Optional[List[str]] = Field(default=None, description="2 bullet points of production engineering")


class CarouselPost(BaseModel):
    pillar: str = Field(description="Category: Architecture Teardown, Portfolio Rescue, or Production Roadmap")
    topic: str = Field(description="Contrarian, clickable topic title")
    slides: List[Slide] = Field(description="Exact list of 5 slides")
    caption: str = Field(description="Instagram caption with formatting, actionable engineering breakdown, and DM keyword trigger")
    trigger_keyword: str = Field(description="Single uppercase trigger keyword, e.g., 'BLUEPRINT', 'STATEMACHINE', 'EVALS', 'MCP'")


class StrategistAgent:
    """Formulates high-converting educational carousels using Azure OpenAI."""

    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure_openai_deployment_name,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            temperature=0.7
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=3, max=15))
    def formulate_carousel(self, market_signals: str, past_topics: List[str]) -> CarouselPost:
        logger.info("Strategist Brain: Formulating high-converting educational carousel...")
        structured_llm = self.llm.with_structured_output(CarouselPost)

        system_prompt = (
            "You are the Lead Enterprise AI Architect and Chief Educator at Code2Career_AI.\n"
            "Your audience consists of CS students, junior developers, and early-career software engineers "
            "trapped in tutorial hell (building naive LangChain PDF wrappers) and failing senior technical interviews.\n\n"
            "GROWTH & ALGORITHM RETENTION RULES:\n"
            "- Slide 1: Bold contrarian hook exposing an industry misconception or broken beginner habit.\n"
            "- Slide 2: The beginner trap/mistake that fails in enterprise production (silent hallucinations, token blowups, fragile prompt logic).\n"
            "- Slide 3: MUST BE A COMPARISON MATRIX. You MUST populate left_column_title, left_column_points (2 items), "
            "right_column_title, and right_column_points (2 items) to create a high-save contrast between toy demos and enterprise architecture.\n"
            "- Slide 4: A concrete 3-step action roadmap to implement the fix.\n"
            "- Slide 5: High-converting CTA asking users to comment the 1-word trigger keyword to receive the free architecture starter repo and Notion checklist in DMs.\n"
            "- Slide text must be concise, technical, and strictly under 26 words per slide."
        )

        user_prompt = f"""
LIVE DEVELOPER MARKET SIGNALS (Hacker News & GitHub):
{market_signals}

RECENTLY PUBLISHED TOPICS (DO NOT REPEAT OR CLOSELY DUPLICATE):
{past_topics[-15:]}

Generate a viral, technically rigorous 5-slide carousel post.
"""

        result = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        logger.info(f"Generated Carousel Topic: '{result.topic}' [{result.pillar}] | Trigger: {result.trigger_keyword}")
        return result


MarketingStrategist = StrategistAgent