from typing import List, Dict
#from duckduckgo_search import DDGS
from ddgs import DDGS
from tenacity import retry, stop_after_attempt, wait_fixed
from core.logger import logger

class TrendResearcher:
    """Scouts AI engineering trends with strict fail-fast timeouts."""

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _search_web(self, query: str, max_results: int = 2) -> List[Dict[str, str]]:
        results = []
        with DDGS(timeout=5) as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", "")
                })
        return results

    def get_latest_market_signals(self) -> str:
        print("[*] Step 1: Scouting internet trends (DuckDuckGo)...", flush=True)
        queries = [
            "AI Engineer roadmap 2026 junior developer",
            "production RAG vs toy demo LangGraph"
        ]

        signals = []
        for q in queries:
            try:
                print(f"    Searching: '{q}'...", flush=True)
                web_hits = self._search_web(q, max_results=2)
                if web_hits:
                    for hit in web_hits:
                        signals.append(f"- {hit['title']}: {hit['snippet']}")
            except Exception as e:
                logger.warning(f"Query '{q}' skipped: {e}")

        if not signals:
            print("    [!] Web query returned empty/timed out. Using baseline signals.", flush=True)
            signals = [
                "- LangGraph state machines replacing linear chains in production systems.",
                "- Why standard chunking fails without cross-encoder rerankers in enterprise RAG.",
                "- Transitioning from basic prompt engineering to LLM evaluation frameworks (Ragas)."
            ]

        print(f"    [✔] Captured {len(signals)} technical trend signals.", flush=True)
        return "\n".join(signals)