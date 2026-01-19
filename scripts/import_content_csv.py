import csv
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(ROOT, "BioVision - cấu trúc nd chi tiết.csv")
DATA_JSON_PATH = os.path.join(ROOT, "data.json")


def _norm(s: Optional[str]) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    # normalize whitespace
    s = re.sub(r"\s+", " ", s)
    return s


def _safe_id(s: str) -> str:
    s = _norm(s).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s, flags=re.IGNORECASE)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "id"


@dataclass
class CsvRow:
    grade: str
    chapter: str
    model_name: str
    model_fun: str
    model_feature: str
    uid: str
    item_name: str
    item_feature: str
    item_fun: str


def _read_csv_rows(path: str) -> List[CsvRow]:
    rows: List[CsvRow] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        # Column names in the CSV (Vietnamese)
        # Khối lớp,Chương,Mô hình,Góc thú vị chung,Đặc điểm,UID sketchfab,Chi tiết,Đặc điểm chi tiết,Góc thú vị chi tiết
        for r in reader:
            rows.append(
                CsvRow(
                    grade=_norm(r.get("Khối lớp")),
                    chapter=_norm(r.get("Chương")),
                    model_name=_norm(r.get("Mô hình")),
                    model_fun=_norm(r.get("Góc thú vị chung")),
                    model_feature=_norm(r.get("Đặc điểm")),
                    uid=_norm(r.get("UID sketchfab")),
                    item_name=_norm(r.get("Chi tiết")),
                    item_feature=_norm(r.get("Đặc điểm chi tiết")),
                    item_fun=_norm(r.get("Góc thú vị chi tiết")),
                )
            )
    return rows


def _load_existing(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"models": []}
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            return {"models": []}

    # migrate legacy format if needed
    if isinstance(data, dict) and "models" not in data and ("modelUid" in data or "items" in data):
        return {
            "models": [
                {
                    "id": "default",
                    "grade": "",
                    "chapter": "",
                    "name": "",
                    "modelUid": data.get("modelUid", ""),
                    "feature": "",
                    "funFact": "",
                    "items": data.get("items", []),
                }
            ]
        }
    if isinstance(data, dict) and "models" in data and isinstance(data["models"], list):
        return data
    return {"models": []}


def _index_existing_world_cam(existing: Dict[str, Any]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """
    Map (modelUid, item_name_lower) -> item dict to preserve world/cam from existing data.json
    """
    idx: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for m in existing.get("models", []) or []:
        mu = _norm(m.get("modelUid"))
        for it in m.get("items", []) or []:
            key = (mu, _norm(it.get("name")).lower())
            idx[key] = it
    return idx


def main() -> None:
    csv_rows = _read_csv_rows(CSV_PATH)
    existing = _load_existing(DATA_JSON_PATH)
    preserve_idx = _index_existing_world_cam(existing)

    models: List[Dict[str, Any]] = []
    current_ctx = {
        "grade": "",
        "chapter": "",
        "model_name": "",
        "uid": "",
        "model_feature": "",
        "model_fun": "",
    }

    # group by (grade, chapter, model_name, uid)
    model_map: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}

    for r in csv_rows:
        # carry-forward context for sparse rows
        if r.grade:
            current_ctx["grade"] = r.grade
        if r.chapter:
            current_ctx["chapter"] = r.chapter
        if r.model_name:
            current_ctx["model_name"] = r.model_name
        if r.uid:
            current_ctx["uid"] = r.uid
        if r.model_feature:
            current_ctx["model_feature"] = r.model_feature
        if r.model_fun:
            current_ctx["model_fun"] = r.model_fun

        grade = current_ctx["grade"]
        chapter = current_ctx["chapter"]
        model_name = current_ctx["model_name"]
        uid = current_ctx["uid"]
        model_feature = current_ctx["model_feature"]
        model_fun = current_ctx["model_fun"]

        if not uid:
            # Can't build a model without UID; skip until we have one
            continue

        mkey = (grade, chapter, model_name, uid)
        if mkey not in model_map:
            model_id = f"{_safe_id(grade)}_{_safe_id(chapter)}_{_safe_id(model_name)}_{_safe_id(uid)[:8]}"
            model_map[mkey] = {
                "id": model_id,
                "grade": grade,
                "chapter": chapter,
                "name": model_name or uid,
                "modelUid": uid,
                "feature": model_feature,
                "funFact": model_fun,
                "items": [],
            }

        # item row
        if r.item_name:
            it_name = r.item_name
            it = {
                "id": f"pt_{_safe_id(uid)[:8]}_{_safe_id(it_name)}",
                "name": it_name,
                "content": r.item_feature,
                "funFact": r.item_fun,
                "link": "",
            }

            # preserve world/cam if existing
            preserved = preserve_idx.get((uid, it_name.lower()))
            if preserved:
                if "world" in preserved:
                    it["world"] = preserved["world"]
                if "cam" in preserved:
                    it["cam"] = preserved["cam"]

            model_map[mkey]["items"].append(it)

    # stable ordering
    for (grade, chapter, model_name, uid), m in sorted(model_map.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], x[0][3])):
        models.append(m)

    out = {"models": models}
    with open(DATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=4)

    print(f"Imported {len(models)} models into data.json from CSV.")


if __name__ == "__main__":
    main()

