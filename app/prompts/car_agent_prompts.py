# app/prompts/car_agent_prompts.py
from typing import Optional

# Prompt base para extração de filtros
PROMPT_BASE = (
    "Extract car-shopping filters from English free text.\n"
    "- OUTPUT POLICY:\n"
    "  * Include ONLY the keys the user explicitly stated.\n"
    "  * Do NOT guess or infer unspecified fields.\n"
    "  * For brand/model/fuel:\n"
    "      - If the user says 'any' or 'no preference', return an empty string \"\".\n"
    "      - If the user does not specify, OMIT the key.\n"
    "  * For numeric fields (price, mileage, etc.):\n"
    "      - If the user says 'no limit', return 0.\n"
    "      - If the user does not specify, OMIT the key.\n"
    "- Interpret 'under 20k' => price_max=20000; 'since 2018' => year_min=2018.\n"
    "- Fuels: gasoline, flex, diesel, electric, hybrid. Prices in USD. Mileage in kilometers.\n"
    "Return ONLY a JSON object that matches the schema. Do not wrap in markdown. No extra text.\n"
)

# Prompt do gatekeeper (decidir se prossegue)
GATEKEEPER_INSTRUCTION = (
    "You are a strict gatekeeper. Decide if the user explicitly asked to proceed with the search now.\n"
    "Respond with EXACTLY ONE of: PROCEED or ASK.\n"
    "Return PROCEED ONLY if the user clearly expressed intent to start the search using phrases like:\n"
    "  'search', 'go', 'run', 'proceed', 'ready', \"that's it\", \"let's search\", "
    "'please search', 'query', 'enough questions', 'done', 'finish'.\n"
    "For any other message (including more preferences), return ASK.\n"
)

def build_extraction_prompt(user_text: str, current_key: Optional[str]) -> str:
    """
    Monta o prompt de extração aceitando múltiplas chaves mencionadas na mesma mensagem
    e aplicando a regra de 'negativo' somente ao campo atual (CURRENT_FIELD).
    """
    field_instr = ""
    if current_key:
        string_fields = {"make", "model", "fuel", "color"}
        numeric_fields = {"price_max", "year_min", "mileage_max"}
        type_hint = (
            "string" if current_key in string_fields else
            "numeric" if current_key in numeric_fields else
            "string"
        )
        field_instr = (
            f"\nCURRENT_FIELD: {current_key}\n"
            f"CURRENT_FIELD_TYPE: {type_hint}\n"
            "TASK: Return a JSON object with any keys explicitly stated by the user in THIS message.\n"
            "ALSO apply this special rule ONLY for CURRENT_FIELD:\n"
            "  - If the message is negative for CURRENT_FIELD (e.g., 'no', 'none', 'nope', 'n/a', 'na', 'skip', 'any', "
            "'no preference', or the line is blank), then include CURRENT_FIELD with empty string \"\" (if string) "
            "or 0 (if numeric).\n"
            "RULES:\n"
            "  - Do NOT invent keys. Apart from the special rule above for CURRENT_FIELD, only include keys explicitly "
            "stated in the text.\n"
            "  - Never unset or change other keys implicitly; only output keys explicitly stated in this message or "
            "the special CURRENT_FIELD mapping.\n"
            "  - If nothing is extractable, return {}.\n"
            "EXAMPLES (apply to this message only):\n"
            "  Asked: budget; User: 'no' → {\"price_max\": 0}\n"
            "  Asked: budget; User: 'No, I want a new Fiat since 2017' → "
            "{\"price_max\": 0, \"is_new\": true, \"make\": \"Fiat\", \"year_min\": 2017}\n"
            "  Asked: brand;  User: 'I want a Honda under 30k' → {\"make\": \"Honda\", \"price_max\": 30000}\n"
        )

    return (
        f"{PROMPT_BASE}{field_instr}\n\n"
        f"User text:\n{user_text}\n\n"
        f"Return ONLY a valid JSON object that matches the schema."
    )
