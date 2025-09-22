# pipeline/load_pipeline.py
from functools import lru_cache
from langchain_core.runnables import Runnable
from pipeline.llm import get_roast_llm
from pipeline.prompt_template import get_roast_prompt
from pipeline.parser import get_roast_parser

@lru_cache(maxsize=1)
def get_roast_chain() -> tuple[Runnable, str]:
    """
    Build the LCEL pipeline: prompt | llm | parser and cache it once.
    Returns (chain, format_instructions).
    """
    parser, format_instructions = get_roast_parser()
    prompt = get_roast_prompt(format_instructions)
    llm = get_roast_llm()
    chain = prompt | llm | parser
    return chain, format_instructions
