# analysis_crewai.py

import os

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

from scraper import scrape_city24

load_dotenv()

MODEL = "openrouter/openai/gpt-oss-120b"

if not os.environ.get("OPENROUTER_API_KEY"):
    raise SystemExit("OPENROUTER_API_KEY not found - add it to your .env file.")

llm = LLM(
    model=MODEL,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


@tool("Scrape city24")
def scrape_tool() -> str:
    """Scrape commercial property listings from city24.lv. Returns them as text lines."""
    listings = scrape_city24()
    return "\n".join(
        f"{x['address']}, {x['city']} | {x['price_eur']} EUR | {x['category']}"
        for x in listings
    )


scraper_agent = Agent(
    role="Web Scraper",
    goal="Collect commercial property listings from city24.lv",
    backstory="You gather raw real-estate data using a Selenium-based tool.",
    tools=[scrape_tool],
    llm=llm,
    verbose=True,
)

analyst_agent = Agent(
    role="Data Analyst",
    goal="Summarize the listings and highlight the best offers",
    backstory="You analyze real-estate data and write clear Latvian summaries.",
    llm=llm,
    verbose=True,
)

scrape_task = Task(
    description="Use the tool to scrape the city24.lv commercial listings.",
    expected_output="A list of listings with address, city, price and category.",
    agent=scraper_agent,
)

analyze_task = Task(
    description=(
        "Analyze the scraped listings. Write a short business summary in Latvian "
        "and list the 5 cheapest offers as 'Top 5 piedāvājumi'."
    ),
    expected_output="A Latvian summary with a Top 5 cheapest offers list.",
    agent=analyst_agent,
    context=[scrape_task],
)

crew = Crew(
    agents=[scraper_agent, analyst_agent],
    tasks=[scrape_task, analyze_task],
    process=Process.sequential,
    memory=False,
    verbose=True,
)

result = crew.kickoff()
print(result)

os.makedirs("data", exist_ok=True)
with open("data/crew_summary.md", "w", encoding="utf-8") as f:
    f.write(str(result))