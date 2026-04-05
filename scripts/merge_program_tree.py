# -*- coding: utf-8 -*-
"""Merge data.json with 'BioVision - cây chương trình 10.csv' — grade 10 only, CSV order."""
import csv
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "BioVision - cây chương trình 10.csv"
DATA_PATH = ROOT / "data.json"


def norm(s: str) -> str:
    if not s:
        return ""
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def canon_chapter(ch: str) -> str:
    """Map chapter strings to a key for matching CSV vs stored data."""
    n = norm(ch)
    if "vi sinh" in n and "vật" in n:
        return "vi_sinh"
    return n


def new_model_id() -> str:
    return "model_" + secrets.token_hex(8)


def load_csv_rows():
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        ch_key = "Chương"
        if fieldnames and fieldnames[0].startswith("\ufeff"):
            ch_key = fieldnames[0]
        for r in reader:
            ch = (r.get(ch_key) or r.get("Chương") or "").strip()
            name = (r.get("Tên mô hình") or "").strip()
            uid = (r.get("UID sketchfab") or "").strip()
            rows.append({"chapter": ch, "name": name, "modelUid": uid})
    return rows


def main():
    csv_rows = load_csv_rows()
    with open(DATA_PATH, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    models = list(data.get("models") or [])

    # UID -> model (any grade); later entries overwrite — prefer keeping richest if needed
    by_uid: dict[str, dict] = {}
    for m in models:
        u = (m.get("modelUid") or "").strip().lower()
        if u:
            by_uid[u] = m

    # Secondary: (canon_chapter, norm(name)) -> list of models (for empty uid / rename)
    by_ch_name: dict[tuple[str, str], list] = {}
    for m in models:
        ck = canon_chapter(m.get("chapter") or "")
        nk = norm(m.get("name") or "")
        by_ch_name.setdefault((ck, nk), []).append(m)

    used_ids: set[str] = set()

    def is_used(m: dict) -> bool:
        return m.get("id") in used_ids

    def mark_used(m: dict | None):
        if m and m.get("id"):
            used_ids.add(m["id"])

    out: list[dict] = []

    for row in csv_rows:
        uid = (row["modelUid"] or "").strip()
        chapter = row["chapter"]
        name = row["name"]
        m = None

        if uid:
            cand = by_uid.get(uid.lower())
            if cand and not is_used(cand):
                m = cand

        if m is None:
            ck = canon_chapter(chapter)
            nk = norm(name)
            candidates = [x for x in by_ch_name.get((ck, nk), []) if not is_used(x)]
            if len(candidates) >= 1:
                m = candidates[0]

        if m is None:
            out.append(
                {
                    "chapter": chapter,
                    "feature": "",
                    "funFact": "",
                    "grade": "10",
                    "id": new_model_id(),
                    "items": [],
                    "modelUid": uid,
                    "name": name,
                }
            )
        else:
            merged = json.loads(json.dumps(m))
            merged["chapter"] = chapter
            merged["name"] = name
            merged["modelUid"] = uid
            merged["grade"] = "10"
            out.append(merged)
            mark_used(m)

    # Anything from old grade 10 not matched (not in CSV / renamed away)
    g10_old = [m for m in models if str(m.get("grade", "")).strip() == "10"]
    unmatched_g10 = [m for m in g10_old if m.get("id") not in used_ids]

    backup_dir = ROOT / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / "unmatched_grade10_before_merge.json"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump({"unmatched_grade10": unmatched_g10}, f, ensure_ascii=False, indent=2)

    data["models"] = out
    data["version"] = data.get("version", 1)
    data["updatedAt"] = datetime.now(timezone.utc).isoformat()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("CSV rows:", len(csv_rows))
    print("Output models:", len(out))
    print("Unmatched old grade-10 (see backups):", len(unmatched_g10))
    print("Backup:", backup_path)


if __name__ == "__main__":
    main()
