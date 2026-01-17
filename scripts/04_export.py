import json
from collections import defaultdict

INPUT = "../deduped/neurova_micro_deduped_v1.jsonl"

OUT_SHADOW = "../exports/neurova_micro_shadow_eval_v1.jsonl"
OUT_RAG = "../exports/neurova_micro_rag_seed_v1.jsonl"
OUT_FULL = "../exports/neurova_micro_full_v1.jsonl"

MAX_RAG_LEN = 600  # character limit for RAG responses


def get_user_context(s):
    uc = s.get("user_context")
    if not isinstance(uc, dict):
        uc = {}
    return uc


def get_expected_message(s):
    er = s.get("expected_response")
    if not isinstance(er, dict):
        return ""
    return er.get("message", "") or ""


def is_short_response(sample):
    return len(get_expected_message(sample)) <= MAX_RAG_LEN


# ----------------------
# LOAD DEDUPED DATA
# ----------------------
full = []
with open(INPUT, "r", encoding="utf-8") as f:
    for line in f:
        full.append(json.loads(line))


# ----------------------
# EXPORT C — FULL DATASET
# ----------------------
def dump(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for s in data:
            f.write(json.dumps(s) + "\n")


dump(OUT_FULL, full)


# ----------------------
# EXPORT B — RAG SEED
# ----------------------
rag = [
    s for s in full
    if s.get("safety_level") != "high" and is_short_response(s)
]

dump(OUT_RAG, rag)


# ----------------------
# EXPORT A — SHADOW EVAL
# ----------------------
buckets = defaultdict(list)

for s in full:
    uc = get_user_context(s)
    key = (
        s.get("persona_mode"),
        s.get("safety_level"),
        uc.get("vertical")
    )
    buckets[key].append(s)

shadow = []
for bucket in buckets.values():
    take = max(1, len(bucket) // 2)
    shadow.extend(bucket[:take])

dump(OUT_SHADOW, shadow)


print("✅ Export complete")
print(f"Full dataset: {len(full)} samples")
print(f"RAG seed: {len(rag)} samples")
print(f"Shadow eval: {len(shadow)} samples")
