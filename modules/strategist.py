from typing import List
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import settings
from core.logger import logger


class Slide(BaseModel):
    slide_num: int = Field(description="Slide number (1 to 5)")
    tag: str = Field(description="Uppercase badge, e.g., 'THE TRAP', 'ARCHITECTURE', 'ENTERPRISE PATTERN', 'ROADMAP', 'ACTION'")
    headline: str = Field(description="Punchy, bold hook. Maximum 6 words.")
    content: str = Field(description="High-density explanation, architecture insight, or blueprint. Maximum 28 words.")


class CarouselPost(BaseModel):
    pillar: str = Field(description="Category: Architecture Teardown, Portfolio Rescue, or Production Roadmap")
    topic: str = Field(description="Contrarian topic title targeting AI engineers")
    slides: List[Slide] = Field(description="Exact sequence of 5 slides")
    caption: str = Field(description="Instagram caption formatted with bullet points, value teardown, and DM call-to-action")
    trigger_keyword: str = Field(description="Single uppercase keyword for comments/DMs, e.g., 'BLUEPRINT', 'STATEMACHINE', 'EVALS'")


class StrategistAgent:
    """Formulates high-engagement educational carousel strategies using Azure OpenAI."""

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
            "Your audience: CS students, junior software developers, and aspiring AI engineers stuck in 'tutorial hell' "
            "(building basic LangChain PDF chat wrappers) and getting ignored by recruiters.\n\n"
            "CONTENT FORMULAS (Select the best fit for today's market signal):\n"
            "1. THE 'STOP DOING THIS' TEARDOWN: Debunk an entry-level practice that fails in production (e.g., naive vector search, prompt-based validation).\n"
            "2. TOY DEMO VS. PRODUCTION ARCHITECTURE: Contrast basic linear code with enterprise architecture (e.g., chains vs. LangGraph state machines, simple chunking vs. hybrid search + rerankers).\n"
            "3. THE ZERO-BS INTERVIEW BLUEPRINT: What hiring managers look for in production AI GitHub repos (eval benchmarks, observability, token cost controls).\n"
            "4. HIGH-LEVERAGE PRODUCTION ROADMAP: 3 production-grade systems to master instead of 10 shallow demo libraries.\n\n"
            "STRICT CONSTRAINTS:\n"
            "- Exactly 5 slides.\n"
            "- Slide 1: Bold contrarian hook challenging a beginner belief.\n"
            "- Slide 2: The beginner trap/mistake that breaks in enterprise scale.\n"
            "- Slide 3: The production architecture pattern or engineering fix.\n"
            "- Slide 4: A concrete 3-step action plan or implementation roadmap.\n"
            "- Slide 5: CTA asking readers to comment the trigger keyword to get the free architecture guide/code template in DMs.\n"
            "- Slide content must be technical, dense, and strictly under 28 words per slide."
        )

        user_prompt = f"""
LIVE MARKET SIGNALS FOUND:
{market_signals}

RECENTLY PUBLISHED TOPICS (DO NOT DUPLICATE OR CLOSELY REPEAT):
{past_topics[-15:]}

Generate a viral, highly technical carousel post tailored for @code2career_ai.
"""

        result = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        logger.info(f"Generated Carousel Topic: '{result.topic}' [{result.pillar}]")
        return result


# Export both names to prevent import mismatches
MarketingStrategist = StrategistAgent
