"""
LLM service — supports Groq, OpenAI, Gemini, and Mock provider.
All calls use temperature=0 for determinism.
"""
from __future__ import annotations

import json
import re
from config import settings


def _call_groq(system_prompt: str, user_content: str) -> str:
    from groq import Groq  # type: ignore
    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=settings.llm_model or "llama-3.3-70b-versatile",
        temperature=settings.llm_temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return response.choices[0].message.content or "{}"


def _call_openai(system_prompt: str, user_content: str) -> str:
    from openai import OpenAI  # type: ignore
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return response.choices[0].message.content or "{}"


def _call_gemini(system_prompt: str, user_content: str) -> str:
    import google.generativeai as genai  # type: ignore
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.llm_model,
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            temperature=settings.llm_temperature,
            response_mime_type="application/json",
        ),
    )
    response = model.generate_content(user_content)
    return response.text


def _call_mock(system_prompt: str, user_content: str) -> str:
    """
    Deterministic rule-based mock implementation that strictly conforms to the
    Problem Statement specification when no real API key is configured.
    """
    text_lower = user_content.lower()

    # Plan B prompt handling
    if "Plan B Card" in system_prompt:
        if any(w in text_lower for w in ["stop", "cancel", "band"]):
            return json.dumps({
                "card_text": "If a month gets tight, I will stop my SIP.",
                "lever": "none",
                "faithful": True,
                "issues": ["cancel_intent"],
                "confidence": 0.95
            })
        if any(w in text_lower for w in ["pause", "hold"]):
            return json.dumps({
                "card_text": "If a month gets tight, I will pause my SIP.",
                "lever": "none",
                "faithful": False,
                "issues": ["unsupported_feature"],
                "confidence": 0.90
            })
        if any(w in text_lower for w in ["skip", "chhod"]):
            return json.dumps({
                "card_text": "If a month gets tight, I will skip that month's instalment using Edit SIP in Groww.",
                "lever": "skip_one",
                "faithful": True,
                "issues": [],
                "confidence": 0.95
            })
        if any(w in text_lower for w in ["amount", "kam", "reduce", "lower", "heavy"]):
            return json.dumps({
                "card_text": "If a month gets tight, I will reduce my SIP amount using Edit SIP in Groww.",
                "lever": "change_amount",
                "faithful": True,
                "issues": [],
                "confidence": 0.95
            })
        # Default or date
        return json.dumps({
            "card_text": "If a month gets tight, I will change my SIP date using Edit SIP in Groww.",
            "lever": "change_date",
            "faithful": True,
            "issues": [],
            "confidence": 0.95
        })

    # Lever Coach handling
    # 1. Advice request
    if any(w in text_lower for w in ["which fund", "best fund", "recommend", "should i invest", "returns", "profit"]):
        match = re.search(r"(which fund|best fund|recommend|returns)", user_content, re.IGNORECASE)
        quote = match.group(0) if match else user_content[:20]
        return json.dumps({
            "levers": ["none_applicable"],
            "situation_type": "advice_request",
            "confidence": 0.98,
            "evidence_quote": quote,
            "explanation": "This tool provides educational information only and does not recommend funds or provide financial advice.",
            "fact_ids": ["K6"]
        })

    # 2. Out of scope / Cancellation
    if any(w in text_lower for w in ["cancel", "stop", "refund", "band karna"]):
        match = re.search(r"(cancel|stop|refund)", user_content, re.IGNORECASE)
        quote = match.group(0) if match else user_content[:20]
        return json.dumps({
            "levers": ["none_applicable"],
            "situation_type": "out_of_scope",
            "confidence": 0.95,
            "evidence_quote": quote,
            "explanation": "Cancelling or pausing an SIP is not covered here. Please refer to Groww Help for assistance.",
            "fact_ids": ["K6"]
        })

    # 3. Timing gap (Date adjustment)
    if any(w in text_lower for w in ["salary", "tarikh", "date", "late", "after", "kat", "5 ko"]):
        quote = user_content
        return json.dumps({
            "levers": ["change_date"],
            "situation_type": "timing_gap",
            "confidence": 0.92,
            "evidence_quote": quote,
            "explanation": "If your salary arrives after your SIP date, you can update your SIP date using Groww's Edit SIP feature.",
            "fact_ids": ["K1", "K2"]
        })

    # 4. Recurring squeeze (Amount adjustment)
    if any(w in text_lower for w in ["heavy", "every month", "har mahine", "kam karna", "too much", "high"]):
        quote = user_content
        return json.dumps({
            "levers": ["change_amount"],
            "situation_type": "recurring_squeeze",
            "confidence": 0.90,
            "evidence_quote": quote,
            "explanation": "If the monthly amount feels too heavy, Groww allows you to edit and change your SIP instalment amount.",
            "fact_ids": ["K1", "K2"]
        })

    # 5. One off month (Skip one)
    quote = user_content
    return json.dumps({
        "levers": ["skip_one"],
        "situation_type": "one_off_month",
        "confidence": 0.88,
        "evidence_quote": quote,
        "explanation": "For a single tight month, you can skip an instalment in Groww without stopping your entire SIP.",
        "fact_ids": ["K3"]
    })


def call_llm(system_prompt: str, user_content: str) -> dict:
    """
    Calls the configured LLM and returns a parsed dict.
    If no API key is set or provider is 'mock', falls back cleanly to the mock engine.
    """
    provider = settings.llm_provider.lower()
    
    # Auto-fallback to mock if provider credentials are not set
    if (
        provider == "mock"
        or (provider == "groq" and not settings.groq_api_key)
        or (provider == "openai" and not settings.openai_api_key)
        or (provider == "gemini" and not settings.gemini_api_key)
    ):
        raw = _call_mock(system_prompt, user_content)
    elif provider == "groq":
        raw = _call_groq(system_prompt, user_content)
    elif provider == "gemini":
        raw = _call_gemini(system_prompt, user_content)
    else:
        raw = _call_openai(system_prompt, user_content)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned non-JSON: {raw[:200]}") from exc
