# src/agents/news_agent.py
from typing import List, Type
from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools import BaseTool
from crewai import Agent, Task, Crew

from ..tools.firecrawl_client import FireCrawlClient
from ..tools.summarizer import Summarizer

import os
from crewai import Crew, Task
from ..tools.firecrawl_client import FireCrawlClient
from ..tools.summarizer import Summarizer

# ---------- Custom CrewAI tools ---------- #

class HeadlineArgs(BaseModel):
    source_url: str = Field(..., description="News site URL")
    limit: int = Field(5, description="Number of headlines to fetch")


class FetchHeadlinesTool(BaseTool):
    name: str = "fetch_headlines"
    description: str = "Return a list of article URLs from the given site."
    args_schema: Type[BaseModel] = HeadlineArgs

    # Private attribute to hold the FireCrawl client
    _client: FireCrawlClient = PrivateAttr()

    def __init__(self, client: FireCrawlClient):
        super().__init__()
        self._client = client

    def _run(self, source_url: str, limit: int = 5) -> List[str]:
        return self._client.fetch_top_headlines(source_url, limit)


class ArticleArgs(BaseModel):
    url: str = Field(..., description="Article URL")


class FetchArticleTool(BaseTool):
    name: str = "fetch_article_body"
    description: str = "Fetch full markdown for a single article."
    args_schema: Type[BaseModel] = ArticleArgs

    _client: FireCrawlClient = PrivateAttr()

    def __init__(self, client: FireCrawlClient):
        super().__init__()
        self._client = client

    def _run(self, url: str) -> str:
        return self._client.fetch_article_body(url)


class SummarizeArgs(BaseModel):
    markdown: str = Field(..., description="Article content in markdown")


class SummarizeTool(BaseTool):
    name: str = "summarize_article"
    description: str = "Condense a news article into three bullets."
    args_schema: Type[BaseModel] = SummarizeArgs

    _summarizer: Summarizer = PrivateAttr()

    def __init__(self, summarizer: Summarizer):
        super().__init__()
        self._summarizer = summarizer

    def _run(self, markdown: str) -> str:
        return self._summarizer.summarize(markdown)


# ---------- Agent factory ---------- #

def create_news_agent(fc: FireCrawlClient, sz: Summarizer) -> Agent:
    tools = [
        FetchHeadlinesTool(fc),
        FetchArticleTool(fc),
        SummarizeTool(sz),
    ]
    return Agent(
        role="News Analyst",
        goal="Deliver concise, factual summaries of breaking news.",
        backstory=(
            "A veteran journalist who leverages AI tools for rapid information "
            "triage and reporting."
        ),
        tools=tools,
        verbose=False,
    )


# ---------- Convenience runner ---------- #

def run_news_report(source_url: str, limit: int, fc: FireCrawlClient, sz: Summarizer) -> str:
    agent = create_news_agent(fc, sz)

    report_task = Task(
        description=(
            "You’re a News Analyst. To generate a reliable report, "
            "it’s highly recommended that you:\n"
            "1) Use `fetch_headlines(source_url=\"{src}\", limit={lim})` to get article URLs.\n"
            "2) Then for each URL, call `fetch_article_body(url=…)`.\n"
            "3) Next, summarize each with `summarize_article(markdown=…)`.\n"
            "Finally, assemble a single Markdown document with each URL as a header "
            "followed by its 3-bullet summary.\n\n"
            "Feel free to ask clarifying questions if any step is unclear."
        ).format(src=source_url, lim=limit),
        expected_output="A Markdown string: H3 headers for each URL, each followed by three bullets.",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[report_task],
        verbose=False,
    )

    try:
        return crew.kickoff()
    except Exception as e:
        msg = str(e).lower()
        if "quota" in msg or "rate limit" in msg:
            raise RuntimeError(
                "It looks like CrewAI’s OpenAI-based planner hit a quota limit. "
                "You may need to check your OPENAI_API_KEY or billing, or reduce the headline limit."
            ) from e
        raise
