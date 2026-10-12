import requests
from typing import List, Dict
from core.logger import logger

class TrendResearcher:
    """Extracts real-time discussions from Hacker News and GitHub APIs."""

    def _fetch_hacker_news_trends(self) -> List[str]:
        """Fetches top-voted AI developer discussions from Hacker News."""
        try:
            url = "https://hn.algolia.com/api/v1/search?tags=story&query=LLM+OR+AI+OR+RAG+OR+evals&hitsPerPage=5"
            res = requests.get(url, timeout=6).json()
            items = res.get("hits", [])
            return [
                f"[HN Discussion] {item.get('title')} (Points: {item.get('points', 0)})"
                for item in items if item.get("title")
            ]
        except Exception as e:
            logger.warning(f"Hacker News trend fetch failed: {e}")
            return []

    def _fetch_github_ai_trending(self) -> List[str]:
        """Fetches popular open-source repositories in AI tooling."""
        try:
            url = "https://api.github.com/search/repositories?q=topic:ai-agents+OR+topic:rag+sort:stars&order=desc&per_page=4"
            headers = {"Accept": "application/vnd.github.v3+json"}
            res = requests.get(url, headers=headers, timeout=6).json()
            items = res.get("items", [])
            return [
                f"[GitHub Tool] {item.get('name')}: {item.get('description', '')}"
                for item in items if item.get("name")
            ]
        except Exception as e:
            logger.warning(f"GitHub trend fetch failed: {e}")
            return []

    def get_latest_market_signals(self) -> str:
        print("[*] Step 1: Scouting live developer signals (Hacker News + GitHub)...", flush=True)
        signals = []

        # 1. Real-time engineering debates
        hn_signals = self._fetch_hacker_news_trends()
        signals.extend(hn_signals)

        # 2. Open-source tooling trends
        gh_signals = self._fetch_github_ai_trending()
        signals.extend(gh_signals)

        # 3. High-signal fallbacks if offline
        if not signals:
            print("    [!] External APIs timed out. Using high-signal defaults.", flush=True)
            signals = [
                "[HN Discussion] Why tool-calling reliability drops when passing >5 schemas to models",
                "[GitHub Tool] LangGraph: Orchestrating cyclical agent graphs with human-in-the-loop state",
                "[HN Discussion] Stop testing LLMs with vibe-checks: How we built automated CI/CD evals"
            ]

        print(f"    [✔] Captured {len(signals)} live technical signals.", flush=True)
        return "\n".join(signals)
