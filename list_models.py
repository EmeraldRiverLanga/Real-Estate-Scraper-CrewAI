# list_models.py

import json
import urllib.request

with urllib.request.urlopen("https://openrouter.ai/api/v1/models") as r:
    data = json.load(r)

# Print paid models sorted by prompt price (cheapest first)
paid = [m for m in data["data"] if float(m.get("pricing", {}).get("prompt", "0")) > 0]
paid.sort(key=lambda m: float(m["pricing"]["prompt"]))
for m in paid[:15]:
    print(m["pricing"]["prompt"], m["id"])