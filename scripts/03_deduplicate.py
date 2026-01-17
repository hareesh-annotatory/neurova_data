import json, hashlib, datetime, os

INPUT_FILE = "../validated/neurova_micro_validated_v1.jsonl"
OUT_MAIN = "../deduped/neurova_micro_deduped_v1.jsonl"
OUT_DUP = "../deduped/neurova_micro_duplicates.jsonl"
REPORT = "../reports/dedup_summary.json"
LOG = "../logs/dedup.log"

os.makedirs(os.path.dirname(OUT_MAIN), exist_ok=True)
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(msg):
    with open(LOG, "a", encoding="utf-8") as l:
        l.write(f"{datetime.datetime.utcnow()} | {msg}\n")

def norm(text: str) -> str:
    """Normalize text to avoid trivial whitespace differences."""
    if not text:
        return ""
    return " ".join(text.strip().split())

seen = {}
kept = 0
dup = 0

with open(INPUT_FILE, "r", encoding="utf-8") as src, \
     open(OUT_MAIN, "w", encoding="utf-8") as main, \
     open(OUT_DUP, "w", encoding="utf-8") as dups:

    for line_no, line in enumerate(src, 1):
        try:
            s = json.loads(line)

            persona = s.get("persona_mode", "UNKNOWN")
            user_input = norm(s.get("user_input", ""))
            message = norm(s.get("expected_response", {}).get("message", ""))

            # ✅ FIX: persona-aware dedup key
            raw_key = f"{persona}||{user_input}||{message}"
            key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

            if key in seen:
                dups.write(json.dumps(s, ensure_ascii=False) + "\n")
                dup += 1
            else:
                seen[key] = True
                main.write(json.dumps(s, ensure_ascii=False) + "\n")
                kept += 1

        except Exception as e:
            log(f"LINE_ERROR {line_no} | {str(e)}")

with open(REPORT, "w", encoding="utf-8") as r:
    json.dump(
        {
            "kept": kept,
            "duplicates": dup,
            "total_seen": kept + dup,
            "dedup_key": "persona_mode + user_input + expected_response.message"
        },
        r,
        indent=2
    )

log(f"DEDUP COMPLETE | kept={kept} | dup={dup}")
