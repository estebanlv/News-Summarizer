# News Summarizer

A tiny but complete pipeline that:

1. Crawls any news site with Firecrawl  
2. Summarises each article via Gemini 2.5 Flash  
3. Outputs a clean markdown digest

## Quick start

```bash
git clone ...
cd news_summarizer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env  # add your keys
python main.py https://techcrunch.com -n 5 -o digest.md
