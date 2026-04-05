# -*- coding: utf-8 -*-
"""Rebuild grade-10 mindmap_order from CSV + migrate components_by_model keys."""
import csv
import json
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "BioVision - cây chương trình 10.csv"
MINDMAP_PATH = ROOT / "mindmap_order.json"

# Mindmap cũ (tên mô hình) -> tên trong CSV
MODEL_RENAMES = {
    ("Chu kì tế bào và phân bào", "Kì đầu nguyên phân"): ("Chu kì tế bào và phân bào", "Nguyên phân - kì đầu"),
    ("Chu kì tế bào và phân bào", "Kì giữa nguyên phân"): ("Chu kì tế bào và phân bào", "Nguyên phân - kì giữa"),
    ("Chu kì tế bào và phân bào", "Kì sau nguyên phân"): ("Chu kì tế bào và phân bào", "Nguyên phân - kì sau"),
    ("Chu kì tế bào và phân bào", "Kì cuối nguyên phân"): ("Chu kì tế bào và phân bào", "Nguyên phân - kì cuối"),
    ("Sinh học vi sinh vật", "VSV"): ("Vi sinh vật", "Vi sinh vật"),
}


def load_csv_chapters_models():
    chapters_order = []
    by_ch = OrderedDict()
    ch_key = "Chương"
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fn = reader.fieldnames or []
        if fn and fn[0].startswith("\ufeff"):
            ch_key = fn[0]
        for r in reader:
            ch = (r.get(ch_key) or "").strip()
            name = (r.get("Tên mô hình") or "").strip()
            if not ch:
                continue
            if ch not in by_ch:
                by_ch[ch] = []
                chapters_order.append(ch)
            by_ch[ch].append(name)
    return chapters_order, by_ch


def resolve_component_key(
    grade: str, chapter: str, model: str, by_ch: OrderedDict
) -> str | None:
    if grade != "10":
        return None
    if (chapter, model) in MODEL_RENAMES:
        ch2, m2 = MODEL_RENAMES[(chapter, model)]
        if ch2 in by_ch and m2 in by_ch[ch2]:
            return f"10::{ch2}::{m2}"
        return None
    if chapter in by_ch and model in by_ch[chapter]:
        return f"10::{chapter}::{model}"
    return None


def main():
    chapters_order, by_ch = load_csv_chapters_models()

    with open(MINDMAP_PATH, "r", encoding="utf-8") as f:
        mm = json.load(f)

    mm["grades"] = ["10"]
    mm["chapters_by_grade"] = {"10": chapters_order}

    models_by_chapter = {}
    for ch in chapters_order:
        models_by_chapter[f"10::{ch}"] = list(by_ch[ch])

    mm["models_by_chapter"] = models_by_chapter

    old_components = mm.get("components_by_model") or {}
    new_components = {}

    for key, items in old_components.items():
        parts = key.split("::", 2)
        if len(parts) != 3:
            continue
        g, ch, m = parts
        nk = resolve_component_key(g, ch, m, by_ch)
        if nk and nk not in new_components:
            new_components[nk] = items

    mm["components_by_model"] = new_components

    with open(MINDMAP_PATH, "w", encoding="utf-8") as f:
        json.dump(mm, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Updated mindmap_order.json")
    print("  grades:", mm["grades"])
    print("  chapters:", len(chapters_order))
    print("  component keys:", len(new_components))


if __name__ == "__main__":
    main()
