import json, glob, uuid, os, datetime

INPUT_DIR = "../input_ready/"
OUTPUT_FILE = "../standardized/neurova_micro_standardized_v1.jsonl"
LOG_FILE = "../logs/standardize.log"

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as l:
        l.write(f"{datetime.datetime.now(datetime.UTC)} | {msg}\n")


def normalize(sample, source_file):
    return {
        "id": str(uuid.uuid4()),
        "sample_type": "chat",
        "persona_mode": sample.get("persona_mode", "Companion"),
        "user_context": sample.get("user_context", {
            "mood": 3,
            "sleep_hours": 6,
            "steps": 4000,
            "engagement_state": "active",
            "vertical": "b2c"
        }),
        "user_input": sample.get("user_input", "").strip(),
        "expected_response": {
            "tone": sample.get("expected_response", {}).get("tone", "warm"),
            "intent": sample.get("expected_response", {}).get("intent", "validate"),
            "message": sample.get("expected_response", {}).get("message", ""),
            "ui_actions": sample.get("expected_response", {}).get("ui_actions", [])
        },
        "safety_level": sample.get("safety_level", "low"),
        "notes": sample.get("notes", ""),
        "meta": {
            "source_file": source_file,
            "source_model": source_file.split("_")[0].lower()
        }
    }

processed = 0
broken = 0

with open(OUTPUT_FILE, "w") as out:
    for file in glob.glob(INPUT_DIR + "*.json*"):
        try:
            with open(file) as f:
                data = json.load(f)
                for sample in data:
                    out.write(json.dumps(normalize(sample, os.path.basename(file))) + "\n")
                    processed += 1
        except Exception as e:
            log(f"BROKEN FILE: {file} | {str(e)}")
            broken += 1

log(f"STANDARDIZATION COMPLETE | processed={processed} | broken_files={broken}")