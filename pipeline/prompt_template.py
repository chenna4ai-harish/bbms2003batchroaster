# pipeline/prompt_template.py
from langchain_core.prompts import ChatPromptTemplate

def get_prompt(format_instructions: str) -> ChatPromptTemplate:
    # Spam prompt kept for back-compat (unchanged)
    messages = [
        ("system", "You are ScamGuard, an expert spam detector. Return ONLY a JSON object."),
        ("system", "{format_instructions}"),
        ("human", 'Classify this message:\n"{message}"'),
    ]
    return ChatPromptTemplate.from_messages(messages)

def get_roast_prompt(format_instructions: str) -> ChatPromptTemplate:
    """
    Reunion "Roaster" prompt builder (funnier, tighter, 3–4 jokes).

    Variables expected:
      - original_name   : string (can include aliases)
      - about           : bio/background text
      - joke_scenarios  : contexts to inspire jokes
      - in5years        : hints for playful forecast
      - roast_level     : 0..100 overall spiciness (wrapper clamps/applies peak rule)
      - dark_joke_level : 0..100 'dark-ish' intensity (wrapper clamps/applies peak rule)
    """
    messages = [
        # Tone + safety guardrails
        (
            "system",
            "You are the Reunion Roaster: a friendly, witty host who roasts with love in simple English. "
            "Keep it playful, clever, and PG-13. Avoid slurs, stereotypes, harassment, or sensitive topics "
            "(religion, caste, politics, health, tragedy). No doxxing or private details. "
            "Return ONLY a JSON object."
        ),
        # Strict JSON schema instructions from PydanticOutputParser
        ("system", "{format_instructions}"),
        # Live input and precise style rules
        (
            "human",
            "Create a fun roast and a playful 5-year forecast for this classmate using only the info provided in simple english.\n"
            "Name (aliases): {original_name}\n"
            "About: {about}\n"
            "commonly_called:{commonly_called}\n"
            "Joke scenarios: {joke_scenarios}\n"
            "Five-year hints: {in5years}\n"
            "Roast level (0-100): {roast_level}\n"
            "Dark-joke level (0-100): {dark_joke_level}\n"
            "Style rules:\n"
            "- Use short, punchy lines with strong sarcasm.\n"
            "- Be fun, not mean. Make the person feel embarassed .\n"
            "- Ground the humor in 'About','commonly_called' and 'Joke scenarios' so it feels personal and relevant.\n"
            "- Exactly 3 to 4 jokes in the 'dark_jokes' list. Keep them PG-13 and event-appropriate.\n"
            "- The 'summary_funny' should be 5-6 sentences max, energetic and funny roasting.\n"
            "- The 'five_year_forecast' should be 1–2 sentences, playful,fun and optimistic.\n"
        ),
    ]
    return ChatPromptTemplate.from_messages(messages)
