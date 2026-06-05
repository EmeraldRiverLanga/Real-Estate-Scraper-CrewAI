# analysis_langchain.py

import os

import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

MODEL = "mistralai/mistral-nemo"

# Stop if the API key is missing
if not os.environ.get("OPENROUTER_API_KEY"):
    raise SystemExit("OPENROUTER_API_KEY not found - add it to your .env file.")

# Load scraped data
df = pd.read_csv("data/city24_commercials.csv")

# Keep only rows with a numeric price
priced = df.dropna(subset=["price_eur"]).copy()
cheapest5 = priced.nsmallest(5, "price_eur")

# Summary statistics
stats = {
    "total": len(df),
    "with_price": len(priced),
    "avg_price": round(priced["price_eur"].mean()),
    "min_price": int(priced["price_eur"].min()),
    "max_price": int(priced["price_eur"].max()),
}

# Format the 5 cheapest listings for the prompt
top5_text = "\n".join(
    f"- {row['address']}, {row['city']} | {int(row['price_eur'])} EUR | {row['link']}"
    for _, row in cheapest5.iterrows()
)

# LLM via OpenRouter
llm = ChatOpenAI(
    model=MODEL,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=0.3,
)

# System role + user message with placeholders
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Tu esi nekustamo īpašumu analītiķis. Raksti īsu, lietišķu kopsavilkumu "
     "latviešu valodā. Izmanto TIKAI dotos skaitļus - neko nerēķini un "
     "nepievieno datus, kas nav doti."),
    ("human",
     "Komerciālo objektu sludinājumi (City24.lv).\n"
     "Kopā: {total}, ar norādītu cenu: {with_price}.\n"
     "Vidējā cena: {avg_price} EUR. Lētākais: {min_price} EUR. "
     "Dārgākais: {max_price} EUR.\n\n"
     "5 lētākās ofertes:\n{top5}\n\n"
     "Uzraksti kopsavilkumu un izcel šīs 5 kā 'Top 5 piedāvājumi'."),
])

# Run the chain
chain = prompt | llm
try:
    result = chain.invoke({**stats, "top5": top5_text})
    print(result.content)
except Exception as e:
    print("AI summary failed:", e)