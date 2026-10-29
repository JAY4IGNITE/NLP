import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
eval_file = ROOT / "data" / "evaluations" / "intent_dataset.json"
intents_file = ROOT / "data" / "structured" / "intents.json"
out_csv = ROOT / "data" / "aditya_university_queries.csv"

rows = []

if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    for ex in eval_data.get("examples", []):
        intent = ex["intents"][0] if ex.get("intents") else "general_inquiry"
        ents = ex.get("entities", {})
        rows.append({
            "query_id": ex.get("example_id"),
            "query": ex.get("text"),
            "intent": intent,
            "domain": ex.get("domain", "curriculum"),
            "language": ex.get("language", "en"),
            "course": ents.get("course", ""),
            "department": ents.get("department", ""),
            "semester": ents.get("semester", ""),
            "unit": ents.get("unit", "")
        })

if intents_file.exists():
    with open(intents_file, "r", encoding="utf-8") as f:
        intents_data = json.load(f)
    counter = len(rows) + 1
    for item in intents_data.get("intents", []):
        intent_name = item.get("name")
        domain = item.get("domain", "curriculum")
        for ex in item.get("examples", []):
            is_te = any(c in ex for c in "ఏమిటిఎన్నిసిలబస్ఆదిత్య")
            is_teen = any(w in ex.lower() for w in ["enni", "cheppandi", "emiti", "cheppu"])
            rows.append({
                "query_id": f"INT-AU-{counter:05d}",
                "query": ex,
                "intent": intent_name,
                "domain": domain,
                "language": "te" if is_te else ("te-en" if is_teen else "en"),
                "course": "",
                "department": "",
                "semester": "",
                "unit": ""
            })
            counter += 1

df = pd.DataFrame(rows)
df = df.drop_duplicates(subset=["query"])
df.to_csv(out_csv, index=False, encoding="utf-8")
print(f"[+] Successfully exported {len(df)} authentic Aditya University queries across {df['intent'].nunique()} intents to {out_csv}")
