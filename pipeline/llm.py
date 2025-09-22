# pipeline/llm.py
import os
import itertools
import random
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from langchain_google_genai import ChatGoogleGenerativeAI
from config import MODEL_NAME

# Optional round-robin iterator held at module scope
_key_cycle = None

def _collect_api_keys() -> list[str]:
    """Collect candidate API keys from env."""
    keys = []
    # Back-compat single key wins if set
    single = os.environ.get("GOOGLE_API_KEY")
    if single:
        return [single]
    # Else gather numbered keys
    for i in range(1,3):  # support up to 9; extend if needed
        k = os.environ.get(f"GOOGLE_API_KEY_{i}")
        if k:
            keys.append(k.strip())
    return [k for k in keys if k]

def _choose_key(strategy: str = "random") -> str:
    """
    Choose an API key using the desired strategy:
    - 'random': uniform random each call
    - 'round_robin': cycle through the list within this process
    """
    global _key_cycle
    keys = _collect_api_keys()
    if not keys:
        raise RuntimeError("Missing GOOGLE_API_KEY or GOOGLE_API_KEY_[1..N] in environment. "
                           "Set it or use .env + utils.init_env().")
    if len(keys) == 1 or strategy == "random":
        return random.choice(keys)
    # round robin
    if _key_cycle is None:
        _key_cycle = itertools.cycle(keys)
    return next(_key_cycle)

def get_roast_llm(temperature: float = 0.0, top_p: float | None = None, top_k: int | None = None) -> ChatGoogleGenerativeAI:
    """
    Create the Gemini chat model with selected API key.
    Defaults keep spam parsing deterministic; pass higher temperature from roast chain.
    """
    api_key = _choose_key(strategy=os.environ.get("GOOGLE_API_KEY_STRATEGY", "random"))
    kwargs = {"model": MODEL_NAME, "google_api_key": api_key, "temperature": temperature}
    if top_p is not None:
        kwargs["top_p"] = top_p
    if top_k is not None:
        kwargs["top_k"] = top_k
    return ChatGoogleGenerativeAI(**kwargs)
