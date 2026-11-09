"""
Digit masking service.
Masks any sequence of 4+ consecutive digits BEFORE the text reaches the LLM.
"""
import re

_DIGIT_RE = re.compile(r"\d{4,}")


def mask_digits(text: str) -> tuple[str, bool]:
    """
    Returns (masked_text, masking_occurred).
    Replaces every run of 4+ digits with an equal-length string of 'X'.
    """
    occurred = False

    def replace(m: re.Match) -> str:
        nonlocal occurred
        occurred = True
        return "X" * len(m.group())

    masked = _DIGIT_RE.sub(replace, text)
    return masked, occurred

