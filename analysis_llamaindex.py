# analysis_llamaindex.py

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from llama_index.core import SQLDatabase, Settings
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.openrouter import OpenRouter
from llama_index.core.embeddings import MockEmbedding

load_dotenv()

MODEL = "openai/gpt-oss-120b"

if not os.environ.get("OPENROUTER_API_KEY"):
    raise SystemExit("OPENROUTER_API_KEY not found - add it to your .env file.")

# Load scraped data into an in-memory SQLite table.
# StaticPool keeps one shared connection so the table survives across queries.
df = pd.read_csv("data/city24_commercials.csv")
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
df.to_sql("listings", engine, index=False)

# LLM via OpenRouter
llm = OpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model=MODEL,
    max_tokens=512,
    context_window=8192,
)
Settings.llm = llm

# Avoid loading default OpenAI embeddings (not needed for explicit-table SQL)
Settings.embed_model = MockEmbedding(embed_dim=1)

# Text-to-SQL query engine over the table
sql_database = SQLDatabase(engine, include_tables=["listings"])
query_engine = NLSQLTableQueryEngine(sql_database=sql_database, tables=["listings"], llm=llm)

questions = [
    "Kuram objektam (address) ir zemākā price_eur vērtība un cik tā ir? Izlaid tukšās price_eur vērtības.",
    "Kāda ir vidējā cena kolonnā price_eur?",
    "Kuras 3 pilsētas kolonnā city ir visbiežāk sastopamās?",
]

for q in questions:
    print("Q:", q)
    try:
        response = query_engine.query(q)
        print("A:", response)
    except Exception as e:
        print("Query failed:", e)
    print("-" * 50)