from __future__ import annotations

import gzip
import json

path = "data/raw/meta_All_Beauty.jsonl.gz"

total = 0
with_categories = 0
examples = []

with gzip.open(path, "rt", encoding="utf-8") as file:
    for line in file:
        row = json.loads(line)
        total += 1

        categories = row.get("categories")

        if categories:
            with_categories += 1

            if len(examples) < 5:
                examples.append(
                    (
                        row.get("parent_asin"),
                        categories,
                    )
                )

print(f"Metadata products: {total:,}")
print(f"Products with categories: {with_categories:,}")
print(f"Category coverage: {with_categories / total:.2%}")
print("Examples:")

for parent_asin, categories in examples:
    print(parent_asin, "->", categories)