# pipeline/alias_lookup.py
from __future__ import annotations
import re
from typing import Dict, List, Tuple
import pandas as pd

NORMALIZE_RE = re.compile(r"[^a-z0-9 ]+")

def normalize(s: str) -> str:
    s = s.strip().lower()
    s = NORMALIZE_RE.sub(" ", s)
    s = " ".join(s.split())
    return s

def split_aliases(name_cell: str) -> List[str]:
    # Split on commas, also tolerate semicolons or pipes if later used in data
    raw = re.split(r"[,\|;]", name_cell or "")
    return [a.strip() for a in raw if a.strip()]

def build_alias_index(df: pd.DataFrame, name_col: str = "name") -> Tuple[Dict[str, int], Dict[int, List[str]]]:
    alias_to_row: Dict[str, int] = {}
    row_to_aliases: Dict[int, List[str]] = {}
    
    for i, val in enumerate(df[name_col].astype(str).tolist()):
        aliases = split_aliases(val)
        norm_aliases = list({normalize(a) for a in aliases})
        row_to_aliases[i] = norm_aliases
        for a in norm_aliases:
            # If a duplicate alias appears for different rows, keep first and ignore later to avoid ambiguity
            alias_to_row.setdefault(a, i)
    return alias_to_row, row_to_aliases

def fuzzy_best_match(q: str, candidates: List[str]) -> Tuple[str, int]:
    # Simple token-set similarity without external deps (score 0..100)
    q_tokens = set(normalize(q).split())
    best_alias, best_score = "", 0
    for c in candidates:
        c_tokens = set(normalize(c).split())
        if not q_tokens or not c_tokens:
            score = 0
        else:
            inter = len(q_tokens & c_tokens)
            union = len(q_tokens | c_tokens)
            score = int(100 * inter / union)
        if score > best_score:
            best_alias, best_score = c, score
    return best_alias, best_score

def resolve_name(
    query: str,
    df: pd.DataFrame,
    alias_to_row: Dict[str, int],
    row_to_aliases: Dict[int, List[str]],
    name_col: str = "name",
    threshold: int = 70,
) -> Tuple[int | None, str, int]:
    """
    Returns (row_index, matched_alias, score). If exact alias hit => score=100.
    If fuzzy match above threshold => row_index with score.
    Otherwise => (None, "", 0).
    """
    qn = normalize(query)
    if not qn:
        return None, "", 0

    if qn in alias_to_row:
        return alias_to_row[qn], qn, 100

    # Consider all unique aliases for fuzzy
    all_aliases = []
    for aliases in row_to_aliases.values():
        all_aliases.extend(aliases)
    # Make unique to speed up
    all_aliases = list(dict.fromkeys(all_aliases))

    best_alias, best_score = fuzzy_best_match(qn, all_aliases)
    if best_score < threshold:
        return None, "", best_score

    row_idx = alias_to_row.get(normalize(best_alias))
    if row_idx is None:
        return None, "", best_score
    return row_idx, best_alias, best_score
