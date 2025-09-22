# pipeline/llm.py
import os
import itertools
import random
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from config import MODEL_NAME

_key_cycle = None

def _get_env(name: str):
    # Prefer Streamlit secrets in cloud; fall back to env for local dev
    if hasattr(st, "secrets") and name in st.secrets:
        return st.secrets[name]
    return os.environ.get(name)

def _collect_api_keys() -> list[str]:
    single = _get_env("GOOGLE_API_KEY")
    if single:
        return [single]
    keys = []
    for i in range(1, 10):
        k = _get_env(f"GOOGLE_API_KEY_{i}")
        if k:
            keys.append(k.strip())
    return keys

def _choose_key(strategy: str = "random") -> str:
    global _key_cycle
    keys = _collect_api_keys()
    if not keys:
        raise RuntimeError("Missing GOOGLE_API_KEY or GOOGLE_API_KEY_[1..N] in environment or secrets.")
    if len(keys) == 1 or strategy == "random":
        return random.choice(keys)
    if _key_cycle is None:
        _key_cycle = itertools.cycle(keys)
    return next(_key_cycle)

def get_roast_llm(temperature: float = 0.9, top_p: float | None = 0.9, top_k: int | None = 40):
    api_key = _choose_key(strategy=_get_env("GOOGLE_API_KEY_STRATEGY") or "random")
    kwargs = {"model": MODEL_NAME, "google_api_key": api_key, "temperature": temperature}
    if top_p is not None:
        kwargs["top_p"] = top_p
    if top_k is not None:
        kwargs["top_k"] = top_k
    return ChatGoogleGenerativeAI(**kwargs)
