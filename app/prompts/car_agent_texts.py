# app/prompts/car_agent_texts.py

# Ordem das perguntas base
KEY_ORDER = ["price_max", "make", "model", "year_min", "fuel"]

# Schemas (usados no response_schema do google-genai)
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "make": {"type": "string"},
        "model": {"type": "string"},
        "fuel":  {"type": "string", "enum": ["gasoline","flex","diesel","electric","hybrid"]},
        "year_min": {"type": "integer"},
        "price_max": {"type": "integer"},
        "mileage_max": {"type": "integer"},
        "is_new": {"type": "boolean"},
        "is_automatic": {"type": "boolean"},
        "has_air_conditioning": {"type": "boolean"},
        "has_bt_radio": {"type": "boolean"},
        "has_charger_plug": {"type": "boolean"},
        "is_armored": {"type": "boolean"},
    },
    "additionalProperties": False,
}

PROCEED_SCHEMA = {
    "type": "string",
    "enum": ["PROCEED", "ASK"]
}

# Mapa de perguntas (next_question)
QUESTIONS_MAP = {
    "price_max": "Do you have a budget in USD? (e.g., 'under 20k')",
    "make":      "Any preferred brand? (e.g., Toyota, Lexus; or 'any')",
    "model":     "Any specific model? (you can skip)",
    "year_min":  "Minimum fabrication year? (e.g., 'since 2018')",
    "fuel":      "Preferred fuel? (gasoline, flex, diesel, electric, hybrid; or 'any')",
}

# Textos de interface
INTRO_HEADER = (
    "Car finder. Free-form conversation. Type 'search' when ready; 'exit' to quit.\n"
)

INTRO_EXAMPLES = (
    "Examples:\n- 'I want a Honda under 30k'\n- 'Since 2018, hybrid, under 25k'\n"
)

EXTRA_CONSTRAINTS_PROMPT = (
    "\nAny extra constraints before I search?\n"
    "- mileage max\n"
    "- new or used\n"
    "- automatic or manual\n"
    "- air conditioning\n"
    "- Bluetooth radio\n"
    "- charger plug\n"
    "- armored\n"
    "(If none, type 'search')"
)
