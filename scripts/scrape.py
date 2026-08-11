#!/usr/bin/env python3
"""
AI News Hub — Daily Scraper
Fetches GitHub trending repos, AI model rankings, and AIHOT news.
Runs on GitHub Actions (Ubuntu) with Python 3.11+
"""
import json, os, sys, time, datetime, requests
from pathlib import Path

# ===== Config =====
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
AIHOT_BASE = "https://aihot.virxact.com/api/v1"
DATA_DIR = Path(__file__).parent.parent / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"

# AI model rankings (semi-static, manually curated — update as needed)
AI_RANKINGS = {
    "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "boardCount": 4,
    "sources": ["AIHOT", "Vellum"],
    "boards": [
        {
            "id": "aihot-overall",
            "name": "AIHOT 总榜",
            "source": "aihot.cn",
            "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "metricLabel": "综合分",
            "items": [
                {"rank": 1, "model": "Claude Opus 5", "org": "Anthropic", "score": 86.1, "release": "2025-07", "completeness": "完整", "pricing": "$15/$75", "sourceLabel": "官方", "sourceUrl": "https://www.anthropic.com"},
                {"rank": 2, "model": "Claude Fable 5", "org": "Anthropic", "score": 85.2, "release": "2025-07", "completeness": "完整", "pricing": "$3/$15", "sourceLabel": "官方", "sourceUrl": "https://www.anthropic.com"},
                {"rank": 3, "model": "GPT-5.6 Sol", "org": "OpenAI", "score": 84.3, "release": "2025-08", "completeness": "完整", "pricing": "$5/$15", "sourceLabel": "官方", "sourceUrl": "https://openai.com"},
                {"rank": 4, "model": "Gemini 3 Pro", "org": "Google", "score": 83.7, "release": "2025-06", "completeness": "完整", "pricing": "$1.25/$5", "sourceLabel": "官方", "sourceUrl": "https://deepmind.google"},
                {"rank": 5, "model": "GLM-5.2", "org": "智谱AI", "score": 82.5, "release": "2025-08", "completeness": "较完整", "pricing": "¥8/¥28", "sourceLabel": "智谱开放平台", "sourceUrl": "https://bigmodel.cn"},
                {"rank": 6, "model": "DeepSeek V4 Pro", "org": "DeepSeek", "score": 81.8, "release": "2025-07", "completeness": "较完整", "pricing": "¥2/¥8", "sourceLabel": "官方", "sourceUrl": "https://deepseek.com"},
                {"rank": 7, "model": "Qwen 3.5 Max", "org": "阿里云", "score": 80.6, "release": "2025-07", "completeness": "较完整", "pricing": "¥4/¥12", "sourceLabel": "百炼平台", "sourceUrl": "https://bailian.aliyun.com"},
                {"rank": 8, "model": "Llama 4.1 405B", "org": "Meta", "score": 79.3, "release": "2025-06", "completeness": "完整", "pricing": "开源", "sourceLabel": "HuggingFace", "sourceUrl": "https://huggingface.co"},
                {"rank": 9, "model": "Mistral Large 3", "org": "Mistral", "score": 78.1, "release": "2025-05", "completeness": "较完整", "pricing": "$2/$6", "sourceLabel": "官方", "sourceUrl": "https://mistral.ai"},
                {"rank": 10, "model": "Kimi K2", "org": "Moonshot", "score": 77.4, "release": "2025-07", "completeness": "部分", "pricing": "¥4/¥12", "sourceLabel": "官方", "sourceUrl": "https://platform.moonshot.cn"},
            ]
        },
        {
            "id": "vellum-overall",
            "name": "Vellum · Best Overall",
            "source": "vellum.ai",
            "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "metricLabel": "综合分",
            "items": [
                {"rank": 1, "model": "Claude Opus 5", "org": "Anthropic", "score": 86.1, "release": "2025-07"},
                {"rank": 2, "model": "Claude Fable 5", "org": "Anthropic", "score": 85.2, "release": "2025-07"},
                {"rank": 3, "model": "GPT-5.6 Sol", "org": "OpenAI", "score": 84.3, "release": "2025-08"},
                {"rank": 4, "model": "Gemini 3 Pro", "org": "Google", "score": 83.7, "release": "2025-06"},
                {"rank": 5, "model": "GLM-5.2", "org": "智谱AI", "score": 82.5, "release": "2025-08"},
                {"rank": 6, "model": "DeepSeek V4 Pro", "org": "DeepSeek", "score": 81.8, "release": "2025-07"},
                {"rank": 7, "model": "Qwen 3.5 Max", "org": "阿里云", "score": 80.6, "release": "2025-07"},
                {"rank": 8, "model": "Llama 4.1 405B", "org": "Meta", "score": 79.3, "release": "2025-06"},
                {"rank": 9, "model": "Mistral Large 3", "org": "Mistral", "score": 78.1, "release": "2025-05"},
                {"rank": 10, "model": "Kimi K2", "org": "Moonshot", "score": 77.4, "release": "2025-07"},
            ]
        },
        {
            "id": "vellum-reasoning",
            "name": "Vellum · Reasoning",
            "source": "vellum.ai",
            "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "metricLabel": "推理分",
            "items": [
                {"rank": 1, "model": "Claude Opus 5", "org": "Anthropic", "score": 88.5, "release": "2025-07"},
                {"rank": 2, "model": "GPT-5.6 Sol", "org": "OpenAI", "score": 87.2, "release": "2025-08"},
                {"rank": 3, "model": "Claude Fable 5", "org": "Anthropic", "score": 86.0, "release": "2025-07"},
                {"rank": 4, "model": "Gemini 3 Pro", "org": "Google", "score": 84.1, "release": "2025-06"},
                {"rank": 5, "model": "DeepSeek V4 Pro", "org": "DeepSeek", "score": 83.0, "release": "2025-07"},
            ]
        },
        {
            "id": "vellum-coding",
            "name": "Vellum · Coding",
            "source": "vellum.ai",
            "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "metricLabel": "代码分",
            "items": [
                {"rank": 1, "model": "Claude Opus 5", "org": "Anthropic", "score": 89.0, "release": "2025-07"},
                {"rank": 2, "model": "GPT-5.6 Sol", "org": "OpenAI", "score": 87.5, "release": "2025-08"},
                {"rank": 3, "model": "Claude Fable 5", "org": "Anthropic", "score": 85.8, "release": "2025-07"},
                {"rank": 4, "model": "GLM-5.2", "org": "智谱AI", "score": 84.2, "release": "2025-08"},
                {"rank": 5, "model": "Gemini 3 Pro", "org": "Google", "score": 83.0, "release": "2025-06"},
            ]
        }
    ]
}

# ===== GitHub Search API =====
GITHUB_API = "https://api.github.com/search/repositories"

def gh_search(query, sort="stars", per_page=30):
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    params = {"q": query, "sort": sort, "order": "desc", "per_page": per_page}
    r = requests.get(GITHUB_API, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def parse_repo(repo, source_query):
    return {
        "name": repo["full_name"],
        "url": repo["html_url"],
        "description": repo["description"] or "",
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "language": repo["language"] or "",
        "pushedAt": repo["pushed_at"],
        "owner": repo["owner"]["login"],
        "sourceQuery": source_query,
    }

def scrape_github():
    now = datetime.datetime.now(datetime.timezone.utc)
    week_ago = (now - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    
    # 1. Weekly hot: created in last 7 days, sorted by stars
    weekly = gh_search(f"created:>{week_ago}", sort="stars", per_page=40)
    # 2. Active high-star: stars>1000, pushed recently, sorted by stars
    active = gh_search(f"stars:>1000 pushed:>{week_ago}", sort="stars", per_page=40)
    # 3. All-time top: stars>10000, sorted by stars
    top = gh_search("stars:>10000", sort="stars", per_page=40)
    
    items = []
    seen = set()
    for query_name, result in [("weekly-hot", weekly), ("active-high-star", active), ("all-time-top", top)]:
        for repo in result.get("items", []):
            full_name = repo["full_name"]
            if full_name not in seen:
                seen.add(full_name)
                items.append(parse_repo(repo, query_name))
    
    return {
        "updatedAt": now.isoformat(),
        "total": len(items),
        "source": "api.github.com",
        "items": items,
    }

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {path} ({len(json.dumps(data, ensure_ascii=False))} bytes)")

def save_daily_snapshot(gh_data, rk_data):
    today = datetime.date.today().isoformat()
    snap_dir = SNAPSHOT_DIR / today
    save_json(snap_dir / "github_hot.json", gh_data)
    save_json(snap_dir / "ai_rankings.json", rk_data)
    
    # Update daily index
    index_path = DATA_DIR / "daily-index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = {"days": []}
    if today not in index["days"]:
        index["days"].insert(0, today)
    index["days"] = sorted(index["days"], reverse=True)[:30]  # Keep 30 days
    save_json(index_path, index)

# ===== AIHOT API =====
def fetch_aihot(path, **params):
    """Fetch from AIHOT public API (anonymous, no key needed)"""
    url = f"{AIHOT_BASE}/{path}"
    r = requests.get(url, params=params, timeout=30, headers={"User-Agent": "ZerONE-Bot/1.0"})
    r.raise_for_status()
    return r.json()

def scrape_aihot_news():
    """Fetch curated AI news from AIHOT"""
    data = fetch_aihot("items", mode="selected", window="24h", limit=50)
    return {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "aihot.virxact.com",
        "total": len(data.get("items", [])),
        "items": data.get("items", []),
    }

def scrape_aihot_hot_topics():
    """Fetch hot topics ranking from AIHOT"""
    data = fetch_aihot("hot-topics")
    return {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "aihot.virxact.com",
        "count": data.get("count", 0),
        "items": data.get("items", []),
    }

def scrape_aihot_daily():
    """Fetch latest AI daily report from AIHOT"""
    data = fetch_aihot("dailies/latest")
    return data

def main():
    print(f"🚀 AI News Hub Scraper — {datetime.datetime.now().isoformat()}")
    print()
    
    # Scrape GitHub trending
    print("📡 Fetching GitHub trending repos...")
    try:
        gh_data = scrape_github()
        print(f"  ✓ {gh_data['total']} repos fetched")
    except Exception as e:
        print(f"  ✗ GitHub API error: {e}")
        gh_data = {"updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(), "total": 0, "source": "api.github.com", "items": []}
    
    time.sleep(2)  # Rate limit safety
    
    # AI rankings (semi-static)
    print("🤖 Loading AI model rankings...")
    rk_data = AI_RANKINGS
    print(f"  ✓ {rk_data['boardCount']} boards, {sum(len(b['items']) for b in rk_data['boards'])} entries")
    
    # Save data files
    print("\n💾 Saving data files...")
    save_json(DATA_DIR / "github_hot.json", gh_data)
    save_json(DATA_DIR / "ai_rankings.json", rk_data)
    
    # AIHOT news
    print("\n📰 Fetching AIHOT curated news...")
    try:
        news_data = scrape_aihot_news()
        print(f"  ✓ {news_data['total']} news items")
    except Exception as e:
        print(f"  ✗ AIHOT news error: {e}")
        news_data = {"updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(), "source": "aihot.virxact.com", "total": 0, "items": []}
    
    time.sleep(1)
    
    print("🔥 Fetching AIHOT hot topics...")
    try:
        hot_data = scrape_aihot_hot_topics()
        print(f"  ✓ {hot_data['count']} hot topics")
    except Exception as e:
        print(f"  ✗ AIHOT hot topics error: {e}")
        hot_data = {"updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(), "source": "aihot.virxact.com", "count": 0, "items": []}
    
    time.sleep(1)
    
    print("📄 Fetching AIHOT daily report...")
    try:
        daily_data = scrape_aihot_daily()
        print(f"  ✓ Daily report for {daily_data.get('report',{}).get('date','?')}")
    except Exception as e:
        print(f"  ✗ AIHOT daily error: {e}")
        daily_data = {}
    
    save_json(DATA_DIR / "ai_news.json", news_data)
    save_json(DATA_DIR / "hot_topics.json", hot_data)
    save_json(DATA_DIR / "ai_daily.json", daily_data)
    
    # Save daily snapshot
    print("\n📸 Creating daily snapshot...")
    save_daily_snapshot(gh_data, rk_data)
    
    print(f"\n✅ Done! {datetime.datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
