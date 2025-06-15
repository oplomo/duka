import json

input_file = "fixtures/shop_data.json"
output_file = "fixtures/categories_only.json"

encodings_to_try = ["utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"]

for encoding in encodings_to_try:
    try:
        with open(input_file, "r", encoding=encoding) as f:
            data = json.load(f)
        break  # Success!
    except UnicodeDecodeError:
        continue
else:
    raise ValueError("Could not decode the file with any known encoding")

# Filter and save
categories_only = [entry for entry in data if entry.get("model") == "shop.category"]
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(categories_only, f, indent=2)

print(f"✅ Extracted {len(categories_only)} categories to {output_file}")