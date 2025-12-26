# app/parser.py

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "ticket_attributes_text.json"
OUTPUT_FILE = BASE_DIR / "data" / "ticket_attributes_structured.json"


def load_scraped_text():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["content"]


def parse_attributes(text: str):
    attributes = []
    lines = text.splitlines()
    parsing = False

    for line in lines:
        # Detect table header
        if re.search(r"Attribute\s+Type\s+Description", line):
            parsing = True
            continue

        # Stop at next section
        if parsing and line.strip().startswith("Ticket Properties"):
            break

        if parsing:
            parts = re.split(r"\s{2,}|\t+", line.strip())
            if len(parts) >= 3:
                attributes.append({
                    "attribute": parts[0],
                    "type": parts[1],
                    "description": parts[2]
                })

    return attributes


def run():
    print(" Parsing ticket attributes...")

    text = load_scraped_text()
    attributes = parse_attributes(text)

    if not attributes:
        raise RuntimeError("No attributes parsed")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(attributes, f, indent=2)

    print(f" Parsed {len(attributes)} attributes")
    print(f" Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
