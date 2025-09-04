"""
Author: Yara
"""
from __future__ import annotations
import asyncio, json, os
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types as genai_types
from app.mcp_client import CarClient

KEY_ORDER = ["price_max", "make", "model", "year_min", "fuel"]

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

PROMPT = (
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

class TerminalCarAgent:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise SystemExit("Requires environment variable GEMINI_API_KEY.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash"  # free-tier-elegible

        # Unified controler dict: None = 'haven't asked abou the filter'; ""/0 = don't apply filter; real value = apply
        self.filters: Dict[str, Any] = {
            "make": None, "model": None, "fuel": None, "color": None,
            "year_min": None, "price_max": None, "mileage_max": None,
            "is_new": None, "is_automatic": None,
            "has_air_conditioning": None, "has_bt_radio": None,
            "has_charger_plug": None, "is_armored": None,
        }

    def apply_extracted_filters(self, parsed: Dict[str, Any]) -> None:
        """Applies 'response JSON' on 'unified controller dictinary', that is, get filters from response."""
        for k, v in (parsed or {}).items():
            if k in ("make","model","fuel","color"):
                self.filters[k] = "" if v is None else str(v)
            elif k in ("year_min","price_max","mileage_max"):
                self.filters[k] = 0 if v is None else int(v)
            elif k in ("is_new","is_automatic","has_air_conditioning","has_bt_radio",
                       "has_charger_plug","is_armored"):
                if v is not None:
                    self.filters[k] = bool(v)

    def relax_filters(self, runs: int) -> Dict[str, Any]:
        """first run drop model, relaxes price and year ; second run drops car maker filter."""
        relaxed = dict(self.filters)
        if runs > 1:
            relaxed["make"] = ""      # drop make e encerra
            return relaxed
        # runs == 1 → relax suave
        relaxed["model"] = ""         # sem preferência de modelo
        y = relaxed.get("year_min")
        if isinstance(y, int) and y and y > 1980:
            relaxed["year_min"] = max(1980, y - 3)
        p = relaxed.get("price_max")
        if isinstance(p, int) and p:
            relaxed["price_max"] = int(p * 1.25)
        return relaxed

    def _current_key(self) -> Optional[str]:
        for k in KEY_ORDER:
            if self.filters.get(k) is None:
                return k
        return None

    def _build_extraction_prompt(self, user_text: str) -> str:
        ck = self._current_key()
        field_instr = ""
        if ck:
            field_instr = (
                f"\nCURRENT_FIELD: {ck}\n"
                "When answering, focus ONLY on CURRENT_FIELD.\n"
                "- If the message indicates 'skip', 'any', or 'no preference' for CURRENT_FIELD, "
                "return that key explicitly with empty string \"\" (for string fields) or 0 (for numeric fields).\n"
                "- If the message does not specify CURRENT_FIELD, return an empty JSON object {}.\n"
                "- Do not include any other keys unless they were explicitly stated."
            )
        return (
            f"{PROMPT}{field_instr}\n\n"
            f"User text:\n{user_text}\n\n"
            f"Return ONLY a valid JSON object that matches the schema."
        )

    def next_question(self) -> Optional[str]:
        """aplies question that weren't asked yet"""
        for key in KEY_ORDER:
            v = self.filters.get(key)
            if v is None:
                return {
                    "price_max": "Do you have a budget in USD? (e.g., 'under 20k')",
                    "make":      "Any preferred brand? (e.g., Toyota, Lexus; or 'any')",
                    "model":     "Any specific model? (you can skip)",
                    "year_min":  "Minimum fabrication year? (e.g., 'since 2018')",
                    "fuel":      "Preferred fuel? (gasoline, flex, diesel, electric, hybrid; or 'any')",
                }[key]
        return None

    def llm_wants_to_proceed(self, latest_user_text: str) -> bool:
        """
        LLM gatekeeper: decide if we should proceed to search now.
        Minimal-guard: only allow the LLM to say PROCEED after all base questions
        are answered (i.e., next_question() is None). Until then, always ASK.
        """
        # if base questions weren't answered, keep asking
        if self.next_question() is not None:
            return False

        instruction = (
            "You are a strict gatekeeper. Decide if the user explicitly asked to proceed with the search now.\n"
            "Respond with EXACTLY ONE of: PROCEED or ASK.\n"
            "Return PROCEED ONLY if the user clearly expressed intent to start the search using phrases like:\n"
            "  'search', 'go', 'run', 'proceed', 'ready', \"that's it\", \"let's search\", 'please search', 'query', 'enough questions', 'done', 'finish'.\n"
            "For any other message (including more preferences), return ASK.\n"
        )
        full = f"{instruction}\n\nUser input:\n{latest_user_text}"

        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=[genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(full)]
            )],
            #: schema exige application/json
            config=genai_types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=PROCEED_SCHEMA,
            ),
        )

        raw = (getattr(resp, "text", None) or "")
        # O SDK costuma devolver um JSON string, ex: "\"PROCEED\"" — tratamos ambos os casos.
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw.strip().strip('"')

        return str(parsed).strip().upper() == "PROCEED"

    async def run(self) -> None:
        print("Car finder. Free-form conversation. Type 'search' when ready; 'exit' to quit.\n")
        print("Examples:\n- 'I want a Honda under 30k'\n- 'Since 2018, hybrid, under 25k'\n")

        q = self.next_question()
        if q: print(q)

        while True:
            text = input("> ").strip()
            if not text:
                if (q := self.next_question()): print(q)
                continue

            low = text.lower()
            if low in {"exit","quit","sair"}:
                print("Bye."); return
            if self.llm_wants_to_proceed(text):
                break

            # Extract filter based on response text  [INJETADO: CURRENT_FIELD via helper]
            full = self._build_extraction_prompt(text)
            resp = self.client.models.generate_content(
                model=self.model_name,
                contents=[genai_types.Content(
                    role="user",
                    parts=[genai_types.Part.from_text(full)]
                )],
                config=genai_types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                ),
            )
            args = json.loads((getattr(resp, "text", None) or "{}"))
            self.apply_extracted_filters(args)

            if self.next_question() is not None:
                if self.llm_wants_to_proceed(text):
                    break

            if (q := self.next_question()):
                print(q)
            else:
                break

        # the other filter options are always presented before confirming query
        print(
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
        while True:
            t = input("> ").strip()
            if self.llm_wants_to_proceed(t):
                break

            # Extra constraints extraction  [INJETADO: CURRENT_FIELD via helper]
            full2 = self._build_extraction_prompt(t)
            resp = self.client.models.generate_content(
                model=self.model_name,
                contents=[genai_types.Content(
                    role="user",
                    parts=[genai_types.Part.from_text(full2)]
                )],
                config=genai_types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                ),
            )
            args = json.loads((getattr(resp, "text", None) or "{}"))
            self.apply_extracted_filters(args)

        # Sen query to mcp client
        c = CarClient()
        await c.initialize()
        try:
            rows = await c.search_cars(
                make=self.filters.get("make"),
                fuel=self.filters.get("fuel"),
                year_min=self.filters.get("year_min"),
                price_max=self.filters.get("price_max"),
                limit=50,
            )
        finally:
            await c.close()

        # If results are insufficient, look for similar results
        if not rows:
            print("No exact match. Looking for similar results...")
            nf = self.relax_filters(runs=1)
            c = CarClient(); await c.initialize()
            try:
                rows = await c.search_cars(
                    make=nf.get("make"),
                    fuel=nf.get("fuel"),
                    year_min=nf.get("year_min"),
                    price_max=nf.get("price_max"),
                    limit=50,
                )
            finally:
                await c.close()

        if not rows or len(rows) < 3:
            print("Querying additional similar cars...")
            nf = self.relax_filters(runs=2)
            c = CarClient(); await c.initialize()
            try:
                more = await c.search_cars(
                    make=nf.get("make"),
                    fuel=nf.get("fuel"),
                    year_min=nf.get("year_min"),
                    price_max=nf.get("price_max"),
                    limit=50,
                )
            finally:
                await c.close()
            if more:
                rows = (rows or []) + more

        if not rows:
            print("Sorry, at the moment we don't have cars available that matches your search. Please try again")
            return

        print("\nResults:")
        for i, car in enumerate(rows, 1):
            make = car.get("make"); model = car.get("model")
            year = car.get("year"); color = car.get("color")
            mileage = car.get("mileage"); price = car.get("dollar_price")
            km = f"{int(mileage):,}".replace(",", ".") if isinstance(mileage,(int,float)) else str(mileage)
            pr = "US$ " + f"{int(price):,}".replace(",", ".") if isinstance(price,(int,float)) else str(price)
            print(f"- {i}. {make} {model} {year}, {color}, {km} km, {pr}")

        print("\nType 'new' to start another search or 'exit' to quit.")
        if input("> ").strip().lower() in {"new","again","y","yes"}:
            self.__init__(); await self.run()

if __name__ == "__main__":
    asyncio.run(TerminalCarAgent().run())
