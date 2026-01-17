import json
import sys

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

objects = []
buffer = []
brace_count = 0
inside_object = False

with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        # Remove markdown fences if present
        if line.strip().startswith("```"):
            continue

        for char in line:
            if char == "{":
                brace_count += 1
                inside_object = True

            if inside_object:
                buffer.append(char)

            if char == "}":
                brace_count -= 1
                if brace_count == 0 and inside_object:
                    raw_obj = "".join(buffer)
                    buffer = []
                    inside_object = False
                    try:
                        objects.append(json.loads(raw_obj))
                    except Exception:
                        pass

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    json.dump(objects, out, indent=2, ensure_ascii=False)

print("✅ JSON auto-fix complete")
print(f"✅ Objects recovered: {len(objects)}")
print(f"✅ Output written to: {OUTPUT_FILE}")
