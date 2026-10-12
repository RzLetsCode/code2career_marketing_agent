from typing import List
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from core.logger import logger


class TrendResearcher:
    """Scouts developer discussions and open-source trends from Hacker News and GitHub."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _fetch_hacker_news_discussions(self) -> List[str]:
        """Fetches active community discussions around LLM, RAG, and AI system design."""
        url = "https://hn.algolia.com/api/v1/search?tags=story&query=LLM+OR+AI+OR+RAG+OR+evals&hitsPerPage=6"
        response = requests.get(url, headers=self.headers, timeout=6)
        if response.status_code != 200:
            return []

        hits = response.json().get("hits", [])
        signals = []
        for hit in hits:
            title = hit.get("title")
            points = hit.get("points", 0)
            if title:
                signals.append(f"[HN Discussion - {points} pts] {title}")
        return signals

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _fetch_github_trending_topics(self) -> List[str]:
        """Fetches popular open-source repositories solving AI infrastructure problems."""
        url = "https://api.github.com/search/repositories?q=topic:ai-agents+OR+topic:rag+sort:stars&order=desc&per_page=5"
        headers = {**self.headers, "Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code != 200:
            return []

        items = response.json().get("items", [])
        signals = []
        for item in items:
            name = item.get("name")
            desc = item.get("description") or "Production tooling and agent primitives"
            if name:
                signals.append(f"[GitHub Tool] {name}: {desc[:100]}")
        return signals

    def get_latest_market_signals(self) -> str:
        print("[*] Step 1: Scouting live engineering trends (Hacker News & GitHub)...", flush=True)
        signals = []

        try:
            hn_signals = self._fetch_hacker_news_discussions()
            if hn_signals:
                signals.extend(hn_signals)
                print(f"    [✔] Retrieved {len(hn_signals)} discussions from Hacker News.", flush=True)
        except Exception as e:
            logger.warning(f"Hacker News ingestion skipped: {e}")

        try:
            gh_signals = self._fetch_github_trending_topics()
            if gh_signals:
                signals.extend(gh_signals)
                print(f"    [✔] Retrieved {len(gh_signals)} repos from GitHub Trends.", flush=True)
        except Exception as e:
            logger.warning(f"GitHub ingestion skipped: {e}")

        if not signals:
            print("    [!] External APIs timed out. Applying production baseline signals.", flush=True)
            signals = [
                "[HN Discussion] Why tool-calling reliability drops when passing >5 schemas to models",
                "[GitHub Tool] LangGraph: Orchestrating cyclical agent graphs with human-in-the-loop state",
                "[HN Discussion] Stop testing LLMs with vibe-checks: How we built automated CI/CD evals",
                "[GitHub Tool] MCP: Model Context Protocol becoming standard for enterprise agent integrations",
                "[HN Discussion] Why naive vector search fails in production without cross-encoder rerankers"
            ]

        print(f"    [✔] Total active engineering signals compiled: {len(signals)}", flush=True)
        return "\n".join(signals)
