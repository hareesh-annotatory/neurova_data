import json, collections

INPUT = "../deduped/neurova_micro_deduped_v1.jsonl"
REPORT = "../reports/micro_dataset_report.md"

counts = collections.Counter()
safety = collections.Counter()
persona = collections.Counter()

with open(INPUT, "r", encoding="utf-8") as src:
    for line in src:
        s = json.loads(line)
        counts["total"] += 1
        safety[s.get("safety_level", "UNKNOWN")] += 1
        persona[s.get("persona_mode", "UNKNOWN")] += 1

with open(REPORT, "w", encoding="utf-8") as r:
    r.write("# Neurova Micro Interaction Dataset Report\n\n")

    r.write("## Total Samples\n")
    r.write(f"{counts['total']}\n\n")

    r.write("## Safety Distribution\n")
    for k, v in sorted(safety.items()):
        r.write(f"- {k}: {v}\n")

    r.write("\n## Persona Distribution\n")
    for k, v in sorted(persona.items()):
        r.write(f"- {k}: {v}\n")

    if "UNKNOWN" in persona:
        r.write("\n## ⚠️ Warnings\n")
        r.write(f"- UNKNOWN persona detected: {persona['UNKNOWN']} samples\n")
