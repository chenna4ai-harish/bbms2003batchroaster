# pipeline/parser.py
"""
Typed output models and parsers for LCEL pipelines.

- Pydantic models define the exact JSON shape expected from the LLM.
- PydanticOutputParser generates format_instructions and validates LLM JSON.
- Keep this file free of other pipeline imports to avoid circular imports.
"""

from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


# -------------------------------
# Reunion "roast" generator model
# -------------------------------
class ClassmateRoast(BaseModel):
    """
    Output schema for the Reunion Roaster use-case.

    Fields:
    - summary_funny: witty, affectionate summary built from 'about_person'.
    - dark_jokes: 1..5 PG‑13, light dark‑ish jokes guided by 'joke_scinareo' and intensity knobs.
    - five_year_forecast: playful prediction grounded in 'in5years'.
    - roast_rating: optional 1..10 spice meter for UI display.
    - roast_level_used, dark_joke_level_used: optional echoes of applied intensities for transparency.
    """
    summary_funny: str
    dark_jokes: List[str] = Field(..., min_items=1, max_items=5)
    five_year_forecast: str

    roast_rating: int = Field(5, ge=1, le=10, description="1..10 spice level")

    roast_level_used: Optional[int] = Field(
        None, ge=0, le=100, description="Echo of applied roast intensity 0..100"
    )
    dark_joke_level_used: Optional[int] = Field(
        None, ge=0, le=100, description="Echo of applied dark‑joke intensity 0..100"
    )


def get_roast_parser() -> Tuple[PydanticOutputParser, str]:
    """
    Returns (parser, format_instructions) for the roaster chain.

    Usage pattern in chain builder:
        parser, fmt = get_roast_parser()
        prompt = get_roast_prompt(fmt)
        llm = get_llm(...)
        chain = prompt | llm | parser
    """
    parser = PydanticOutputParser(pydantic_object=ClassmateRoast)
    return parser, parser.get_format_instructions()
