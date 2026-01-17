import json, os, csv, datetime

INPUT_FILE = "../standardized/neurova_micro_standardized_v1.jsonl"
OUTPUT_FILE = "../validated/neurova_micro_validated_v1.jsonl"
REPORT_FILE = "../reports/schema_issues.csv"
LOG_FILE = "../logs/validate.log"

# ✅ FIX: include ALL expected persona modes
VALID_PERSONA = {
    "Companion",
    "Coach",
    "Listener",
    "Buddy",
    "Trainer"
}

VALID_SAFETY = {"low", "medium", "high"}

def log(msg):
    with open(LOG_FILE, "a") as l:
        l.write(f"{datetime.datetime.utcnow()} | {msg}\n")

issues = []

def fix(sample, line_no):
    issue_flags = []

    # 🔒 FIX: NEVER overwrite persona_mode
    persona = sample.get("persona_mode")
    if persona not in VALID_PERSONA:
        issue_flags.append("invalid_persona")
        # preserve original value for audit
        sample["_original_persona_mode"] = persona
        sample["persona_mode"] = "UNKNOWN"

    # safety level clamp (this is fine)
    if sample.get("safety_level") not in VALID_SAFETY:
        issue_flags.append("invalid_safety")
        sample["safety_level"] = "low"

    # user input fix
    if not sample.get("user_input"):
        issue_flags.append("missing_user_input")
        sample["user_input"] = ""

    # expected_response normalization
    er = sample.get("expected_response", {})
    for field in ["tone", "intent", "message", "ui_actions"]:
        if field not in er:
            issue_flags.append(f"missing_expected_{field}")
            er[field] = [] if field == "ui_actions" else ""

    sample["expected_response"] = er

    if issue_flags:
        issues.append({
            "line": line_no,
            "id": sample.get("id"),
            "issues": "|".join(issue_flags)
        })

    return sample

# -------- RUN VALIDATION --------

with open(INPUT_FILE, "r", encoding="utf-8") as src, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for i, line in enumerate(src, 1):
        try:
            s = json.loads(line)
            s = fix(s, i)
            out.write(json.dumps(s, ensure_ascii=False) + "\n")
        except Exception as e:
            log(f"LINE_ERROR {i} | {str(e)}")

# -------- WRITE REPORT --------

os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)

with open(REPORT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["line", "id", "issues"])
    writer.writeheader()
    writer.writerows(issues)

log(f"VALIDATION COMPLETE | issues={len(issues)}")
