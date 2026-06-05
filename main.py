# main.py

import os

import pandas as pd

from scraper import scrape_city24

listings = scrape_city24()
df = pd.DataFrame(listings)

os.makedirs("data", exist_ok=True)
df.to_csv("data/city24_commercials.csv", index=False, encoding="utf-8-sig")
df.to_json("data/city24_commercials.json", orient="records", force_ascii=False, indent=2)

print(f"Saved {len(df)} listings to data/city24_commercials.csv and .json")