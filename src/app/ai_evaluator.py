"""AI-based signal evaluation."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


FALLBACK_RESPONSE = {
    "confidence": 0.0,
    "decision": "ACCEPT",
    "reason": "ai_fallback_error",
}


def evaluate_with_ai(signal: dict[str, Any] | None) -> dict[str, Any]:
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("missing_api_key")

        client = OpenAI(api_key=api_key)
        prompt = (
            "Return strict JSON with keys confidence (0..1), decision (ACCEPT|REJECT), "
            "reason (string). Evaluate this trading signal: "
            f"{json.dumps(signal, ensure_ascii=False)}"
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0,
        )

        text = response.output_text.strip()
        print("AI RAW:", text)

        cleaned = text
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        result = json.loads(cleaned)
        print("AI PARSED:", result)
        return result
    except Exception as e:
        print("AI ERROR:", e)
        return FALLBACK_RESPONSE.copy()
