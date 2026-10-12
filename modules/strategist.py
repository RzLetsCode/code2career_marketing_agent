from typing import List
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import settings
from core.logger import logger

class Slide(BaseModel):
    slide_num: int
    tag: str = Field(description="Visual badge, e.g., 'THE TRAP', 'ARCHITECTURE', 'CODE PATTERN'")
    headline: str = Field(description="Bold punchy hook, max 6 words")
    content: str = Field(description="High-density explanation or architecture breakdown. Max 28 words.")

class CarouselPost(BaseModel):
    pillar: str = Field(description="Category: Architecture Teardown, Portfolio Rescue, or Roadmap")
    topic: str = Field(description="Catchy contrarian topic title")
    slides: List[Slide] = Field(description="List of 5 slides")
    caption: str = Field(description="Instagram caption with formatting, actionable insights, and DM hook")
    trigger_keyword: str = Field(description="Single-word DM trigger keyword, e.g., 'BLUEPRINT'")

class StrategistAgent:
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
            "You are a Chief Enterprise AI Architect running technical education for Code2Career_AI.\n"
            "Your audience consists of freshers, junior software engineers, and CS students desperate to break into AI engineering.\n"
            "They are stuck in 'tutorial hell' (basic LangChain wrapper PDFs) and getting rejected by recruiters.\n"
            "Your job is to produce educational content that bridges the gap between toy tutorials and enterprise production."
        )

        user_prompt = f"""
        LIVE MARKET SIGNALS FOUND FROM THE INTERNET:
        {market_signals}

        ALREADY PUBLISHED TOPICS (DO NOT REPEAT OR CLOSELY DUPLICATE):
        {past_topics[-15:]}

        FORMAT REQUIREMENTS:
        - Exactly 5 slides.
        - Slide 1: Bold, contrarian hook challenging a beginner belief.
        - Slide 2: The beginner trap/mistake that fails in production.
        - Slide 3: Enterprise engineering pattern, architecture, or code principle.
        - Slide 4: Concrete 3-step action roadmap.
        - Slide 5: CTA asking readers to comment a single keyword to get the free starter code template in DMs.
        - Text per slide: Short, high impact, under 28 words.
        """

        result = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        logger.info(f"Generated Carousel Topic: '{result.topic}' [{result.pillar}]")
        return result

# Export both names to prevent import mismatches
MarketingStrategist = StrategistAgent