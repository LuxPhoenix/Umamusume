#!/usr/bin/env python3
import sys
import json
import re
from typing import List, Tuple, Dict, Optional

# ----------------------------
# Parsing utilities
# ----------------------------

BLOCK_SPLIT_RE = re.compile(r"\n\s*\n", flags=re.UNICODE)

# Symbols to strip at the end of names
TRAILING_MARKERS = (" ◎", " ○", " ×")
FULLWIDTH_MARKERS = ("◎", "○", "×")

def clean_name(name: str) -> str:
    # Normalize whitespace, strip Unicode NBSP etc.
    s = " ".join(name.strip().split())
    # Remove trailing markers (both with preceding space and raw symbol at end)
    for m in TRAILING_MARKERS:
        if s.endswith(m):
            s = s[: -len(m)]
    for m in FULLWIDTH_MARKERS:
        if s.endswith(m):
            s = s[: -len(m)]
    # Standardize ASCII hyphen for cases like "Head-To-Head" vs "Head‑To‑Head"
    s = s.replace("–", "-").replace("—", "-").replace("‑", "-")
    return s

def parse_first_lines(raw: str) -> List[str]:
    """
    Split the raw text into blocks by blank lines; take the first
    non-empty line of each block as the skill name.
    """
    skills = []
    for block in BLOCK_SPLIT_RE.split(raw.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip() != ""]
        if not lines:
            continue
        skills.append(lines[0].strip())
    return skills

def make_pairs(en_names: List[str], ja_names: List[str]) -> List[Tuple[str, Optional[str]]]:
    """
    One-to-one pairing by position. If lists differ in size, we pair up to the min length.
    If JP is a "Not translated yet" placeholder, map to None.
    """
    pairs: List[Tuple[str, Optional[str]]] = []
    n = min(len(en_names), len(ja_names))
    for i in range(n):
        en = clean_name(en_names[i])
        ja = clean_name(ja_names[i])
        if ja in {"Not translated yet", "未翻訳", "未対応"}:
            ja_val: Optional[str] = None
        else:
            ja_val = ja
        pairs.append((en, ja_val))
    return pairs

def invert_map(d: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    inv: Dict[str, Optional[str]] = {}
    for k, v in d.items():
        if v is None:
            continue
        # If colliding, keep the first occurrence
        inv.setdefault(v, k)
    return inv

# ----------------------------
# Main build function
# ----------------------------

def build_and_save_maps(en_text: str, ja_text: str,
                        out_en_ja: str = "skill_name_map_en_ja.json",
                        out_ja_en: str = "skill_name_map_ja_en.json") -> Tuple[Dict[str, Optional[str]], Dict[str, Optional[str]]]:
    en_names = parse_first_lines(en_text)
    ja_names = parse_first_lines(ja_text)

    if len(en_names) != len(ja_names):
        print(f"[WARN] Count mismatch: EN={len(en_names)} vs JP={len(ja_names)}. Pairing by min length.")

    pairs = make_pairs(en_names, ja_names)
    en_to_ja = {en: ja for en, ja in pairs}
    ja_to_en = invert_map(en_to_ja)

    # Save
    with open(out_en_ja, "w", encoding="utf-8") as f:
        json.dump(en_to_ja, f, ensure_ascii=False, indent=2)
    with open(out_ja_en, "w", encoding="utf-8") as f:
        json.dump(ja_to_en, f, ensure_ascii=False, indent=2)

    # Preview a handful
    print(f"Built EN->JA ({len(en_to_ja)} entries) and JA->EN ({len(ja_to_en)} entries).")
    print("Sample pairs:")
    for i, (en, ja) in enumerate(pairs[:10]):
        print(f"  {i+1:02d}. EN: {en!r}  ->  JP: {ja!r}")
    return en_to_ja, ja_to_en

# ----------------------------
# CLI
# ----------------------------

def main():
    if len(sys.argv) == 3:
        en_path, ja_path = sys.argv[1], sys.argv[2]
        with open(en_path, "r", encoding="utf-8") as f:
            en_text = f.read()
        with open(ja_path, "r", encoding="utf-8") as f:
            ja_text = f.read()
        build_and_save_maps(en_text, ja_text)
    else:
        print("[INFO] No files provided. Using in-memory placeholders.")
        # Paste your raw blocks below if you want to run in-memory.
        EN_TEXT = """
        Right-Handed ◎
        Increase performance on right-handed tracks.
        
        Left-Handed ○
        Moderately increase performance on left-handed tracks.
        """.strip()

        JA_TEXT = """
        右回り◎
        右回りコースが得意になる
        
        左回り○
        左回りコースが少し得意になる
        """.strip()

        build_and_save_maps(EN_TEXT, JA_TEXT)

if __name__ == "__main__":
    main()
