# pipeline/wrapper.py
from __future__ import annotations
import random
from typing import List, Dict
import pandas as pd

from pipeline.load_pipeline import get_roast_chain   # cached chain builder
from pipeline.parser import ClassmateRoast           # typed output model

def _clamp(v: int, lo: int = 0, hi: int = 100) -> int:
    try:
        iv = int(v)
    except Exception:
        iv = 0
    return max(lo, min(hi, iv))

def _apply_peak_rule(v: int) -> int:
    # If exactly 100, randomize to 80..100 for a bit of variety
    return random.randint(80, 100) if v == 100 else v

def roast_one(
    original_name: str,
    commonly_called: str,
    about: str,
    joke_scenarios: str,
    in5years: str,
    roast_level: int = 50,
    dark_joke_level: int = 30,
) -> ClassmateRoast:
    rl = _apply_peak_rule(_clamp(roast_level))
    dl = _apply_peak_rule(_clamp(dark_joke_level))
    chain, fmt = get_roast_chain()
    return chain.invoke({
        "format_instructions": fmt,
        "original_name": original_name,
        "commonly_called": commonly_called,
        "about": about,
        "joke_scenarios": joke_scenarios,
        "in5years": in5years,
        "roast_level": rl,
        "dark_joke_level": dl,
    })
