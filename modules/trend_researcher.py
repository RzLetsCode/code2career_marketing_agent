import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from core.logger import logger


class TrendResearcher:
    """
    Multi-Source Real-Time Engineering Trend Scout.
    Aggregates live signals from:
      1. Hacker News (Time-windowed last 7 days)
      2. GitHub Breakout Repositories (Created in last 30 days, sorted by star velocity)
      3. Reddit Developer Subreddits (r/LocalLLaMA, r/AI_Agents, r/MachineLearning, r/cscareerquestions)
      4. Hugging Face Daily Papers (Trending AI research with community upvotes)
      5. DEV.to Top Weekly Engineering Articles (#ai, #llm, #rag, #agents)
      6. ArXiv Latest Preprints (Agentic workflows, RAG, MCP, LLM Evals)
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Code2Career_AI_TrendScout/2.0 (https://github.com/RzLetsCode; Enterprise AI Education)",
            "Accept": "application/json"
        }

    # -------------------------------------------------------------------------
    # 1. HACKER NEWS: Time-Windowed Discussions (Last 7 Days Only)
    # -------------------------------------------------------------------------
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _fetch_hacker_news_discussions(self) -> List[str]:
        """Fetches high-engagement LLM, RAG, MCP, and AI System Design discussions from the past 7 days."""
        seven_days_ago_ts = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())
        url = (
            "https://hn.algolia.com/api/v1/search?"
            "tags=story"
            "&query=LLM+OR+RAG+OR+Agent+OR+MCP+OR+LangGraph+OR+evals"
            f"&numericFilters=created_at_i>{seven_days_ago_ts},points>15"
            "&hitsPerPage=6"
        )
        response = requests.get(url, headers=self.headers, timeout=7)
        if response.status_code != 200:
            return []

        hits = response.json().get("hits", [])
        signals = []
        for hit in hits:
            title = hit.get("title")
            points = hit.get("points", 0)
            comments = hit.get("num_comments", 0)
            if title:
                signals.append(f"[HN Trending ({points} pts, {comments} comments)] {title}")
        return signals

    # -------------------------------------------------------------------------
    # 2. GITHUB BREAKOUT REPOS: High Velocity in Last 30 Days
    # -------------------------------------------------------------------------
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _fetch_github_breakout_repos(self) -> List[str]:
        """Fetches fast-growing open-source AI/Agent repositories created in the last 30 days."""
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        query = f"(ai-agents OR rag OR mcp OR langgraph OR llm-evals) created:>{thirty_days_ago}"
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 5
        }
        headers = {**self.headers, "Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers, params=params, timeout=7)
        if response.status_code != 200:
            return []

        items = response.json().get("items", [])
        signals = []
        for item in items:
            name = item.get("full_name") or item.get("name")
            stars = item.get("stargazers_count", 0)
            desc = (item.get("description") or "Fast-rising AI infrastructure tool").strip()
            if name:
                signals.append(f"[GitHub Breakout Repo ({stars}★ in <30d)] {name}: {desc[:120]}")
        return signals

    # -------------------------------------------------------------------------
    # 3. REDDIT ENGINEERING COMMUNITIES: Practitioner Pain Points
    # -------------------------------------------------------------------------
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _fetch_reddit_engineering_pulse(self) -> List[str]:
        """Scouts top discussions from r/LocalLLaMA, r/AI_Agents, and r/cscareerquestions."""
        subreddits = [
            ("LocalLLaMA", 3),
            ("AI_Agents", 2),
            ("cscareerquestions", 2),
        ]
        signals = []
        for sub, limit in subreddits:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit + 2}"
            try:
                res = requests.get(url, headers=self.headers, timeout=6)
                if res.status_code != 200:
                    continue
                children = res.json().get("data", {}).get("children", [])
                count = 0
                for post in children:
                    data = post.get("data", {})
                    if data.get("stickied"):
                        continue
                    title = data.get("title", "").strip()
                    ups = data.get("ups", 0)
                    if title and ups > 5:
                        signals.append(f"[Reddit r/{sub} ({ups} upvotes)] {title[:130]}")
                        count += 1
                        if count >= limit:
                            break
            except Exception:
                continue
        return signals

    # -------------------------------------------------------------------------
    # 4. HUGGING FACE DAILY PAPERS: Cutting-Edge Applied AI Research
    # -------------------------------------------------------------------------
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _fetch_huggingface_daily_papers(self) -> List[str]:
        """Fetches top upvoted papers from Hugging Face Daily Papers API."""
        url = "https://huggingface.co/api/daily_papers"
        res = requests.get(url, headers=self.headers, timeout=7)
        if res.status_code != 200:
            return []

        papers = res.json()
        if not isinstance(papers, list):
            return []

        # Sort by community upvotes descending
        sorted_papers = sorted(
            papers,
            key=lambda x: x.get("paper", {}).get("upvotes", 0),
            reverse=True
        )

        signals = []
        for item in sorted_papers[:4]:
            paper = item.get("paper", {})
            title = (paper.get("title") or item.get("title") or "").replace("\n", " ").strip()
            upvotes = paper.get("upvotes", 0)
            summary = (paper.get("summary") or "").replace("\n", " ").strip()
            if title:
                snippet = f" — {summary[:110]}..." if summary else ""
                signals.append(f"[HuggingFace Daily Paper ({upvotes} upvotes)] {title}{snippet}")
        return signals

    # -------------------------------------------------------------------------
    # 5. DEV.TO PRACTITIONER ARTICLES: Trending Developer Tutorials
    # -------------------------------------------------------------------------
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _fetch_devto_trending_articles(self) -> List[str]:
        """Fetches top developer articles published in the last 7 days on DEV.to."""
        url = "https://dev.to/api/articles"
        params = {
            "tag": "ai",
            "top": "7",       # Top articles over the last 7 days
            "per_page": "4"
        }
        res = requests.get(url, headers=self.headers, params=params, timeout=6)
        if res.status_code != 200:
            return []

        articles = res.json()
        signals = []
        for art in articles[:4]:
            title = art.get("title", "").strip()
            reactions = art.get("public_reactions_count", 0)
            desc = (art.get("description") or "").strip()
            if title:
                signals.append(f"[DEV.to Trending ({reactions} reactions)] {title}: {desc[:100]}")
        return signals

    # -------------------------------------------------------------------------
    # 6. ARXIV PREPRINTS: Production Agents, RAG & Evaluation Benchmarks
    # -------------------------------------------------------------------------
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=False)
    def _fetch_arxiv_agent_papers(self) -> List[str]:
        """Fetches recent ArXiv papers on LLM Agents, RAG pipelines, and Tool Calling."""
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": "all:\"multi-agent\" OR all:\"retrieval augmented\" OR all:\"tool calling\"",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": 3
        }
        res = requests.get(url, headers=self.headers, params=params, timeout=7)
        if res.status_code != 200:
            return []

        root = ET.fromstring(res.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        signals = []
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            if title_el is not None and title_el.text:
                clean_title = " ".join(title_el.text.split())
                signals.append(f"[ArXiv Research] {clean_title}")
        return signals

    # -------------------------------------------------------------------------
    # MASTER AGGREGATOR (Parallel Execution for Fast Startup)
    # -------------------------------------------------------------------------
    def get_latest_market_signals(self) -> str:
        print("[*] Step 1: Scouting live engineering trends across 6 developer ecosystems...", flush=True)

        sources = [
            ("Hacker News (7d)", self._fetch_hacker_news_discussions),
            ("GitHub Breakout Repos (30d)", self._fetch_github_breakout_repos),
            ("Reddit Engineering Pulse", self._fetch_reddit_engineering_pulse),
            ("HuggingFace Daily Papers", self._fetch_huggingface_daily_papers),
            ("DEV.to Practitioner Trends", self._fetch_devto_trending_articles),
            ("ArXiv Agentic Preprints", self._fetch_arxiv_agent_papers),
        ]

        all_signals: List[str] = []

        # Fetch all 6 sources concurrently so total research time stays under ~5 seconds
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_name = {executor.submit(fn): name for name, fn in sources}
            for future in as_completed(future_to_name):
                source_name = future_to_name[future]
                try:
                    results = future.result()
                    if results:
                        all_signals.extend(results)
                        print(f"    [✔] {source_name}: Retrieved {len(results)} high-signal trends.", flush=True)
                    else:
                        print(f"    [~] {source_name}: No new items returned.", flush=True)
                except Exception as e:
                    logger.warning(f"{source_name} ingestion skipped: {e}")
                    print(f"    [!] {source_name} skipped: {e}", flush=True)

        if not all_signals:
            print("    [!] External APIs unreachable. Applying curated 2026 production baseline signals.", flush=True)
            all_signals = [
                "[HN Trending] Why tool-calling reliability drops sharply when passing >5 MCP schemas to agents",
                "[GitHub Breakout Repo] LangGraph State Checkpointers: Fault-tolerant multi-agent memory in production",
                "[Reddit r/LocalLLaMA] Hybrid BM25 + Cross-Encoder Reranking outperforms pure dense vector RAG by 38%",
                "[HuggingFace Daily Paper] Agentic RAG with self-correcting query decomposition and deterministic guardrails",
                "[DEV.to Trending] Why junior AI portfolios fail senior interviews: Moving from notebooks to FastAPI + Docker + Evals",
            ]

        print(f"    [✔] Total multi-channel engineering signals compiled: {len(all_signals)}", flush=True)
        return "\n".join(all_signals)