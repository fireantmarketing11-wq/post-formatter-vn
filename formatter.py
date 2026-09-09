# -*- coding: utf-8 -*-
"""
formatter.py
Final updates:
- Add final_forced_replace(original_text, result_text, style, exceptions_lower) which ensures any ASCII token present in the original input
  is forced-formatted in the final result (unless in exceptions or contains diacritics).
- Call final_forced_replace before returning final result so repeated occurrences or tokens missed earlier are formatted.
"""
import re
from utils import to_unicode_style

# minimal Vietnamese stopwords to detect Vietnamese context
VIET_STOPWORDS = set([
    'và','là','của','cho','trên','với','các','những','một','như','được','để','khi','vì','đã','vẫn','có','không','bạn','mình','từ'
])

# Token regex: allow ASCII/Unicode letters and digits, and allow internal separators like / - . : between segments
LETTER_TOKEN_RE = re.compile(r"[A-Za-z0-9À-ỹ̀-ỹ]+(?:[\/\-\.:][A-Za-z0-9À-ỹ̀-ỹ]+)*", flags=re.UNICODE)
# Split text into tokens or separators — keep separator-containing tokens intact
SPLIT_RE = re.compile(r"([A-Za-z0-9À-ỹ̀-ỹ]+(?:[\/\-\.:][A-Za-z0-9À-ỹ̀-ỹ]+)*|[^A-Za-z0-9À-ỹ̀-ỹ\/\-\.:]+)", flags=re.UNICODE)

# bullet symbol
BULLET_SYMBOL = '•\u2060\u2009'

# helpers

def has_diacritic(s: str) -> bool:
    for ch in s:
        if ord(ch) > 127:
            return True
    return False


def token_is_vietnamese(token: str) -> bool:
    # If token contains any diacritic character, treat as Vietnamese and do not convert letters in it.
    if has_diacritic(token):
        return True
    if token.lower() in VIET_STOPWORDS:
        return True
    return False


def choose_token_candidate(token: str, exceptions_lower: set):
    """Decide if a token should be formatted.
    Rules:
      - If token is listed in exceptions -> do NOT skip (we will format exceptions if present)
      - If token contains any diacritic (Vietnamese) -> do not format letters in it
      - Otherwise, if token contains any ASCII letter or digit -> force format (user requested all English words must be formatted)
    """
    if not token:
        return False
    if token.lower() in exceptions_lower:
        return True
    if token_is_vietnamese(token):
        return False
    # If contains ASCII letter or digit, mark as candidate
    if re.search(r"[A-Za-z0-9]", token):
        return True
    return False


def apply_fancy_phrase(phrase: str, style: str) -> str:
    # convert each ASCII letter/digit to the chosen unicode style; leave other characters (diacritics, separators) unchanged
    out = []
    for ch in phrase:
        if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ch.isdigit():
            out.append(to_unicode_style(ch, style))
        else:
            out.append(ch)
    return ''.join(out)


def emphasize_phrase(phrase_parts, style, exceptions_lower):
    out = []
    for part in phrase_parts:
        # part may be token-like or separator
        if LETTER_TOKEN_RE.fullmatch(part):
            if part.lower() in exceptions_lower:
                out.append(apply_fancy_phrase(part, style))
            elif not has_diacritic(part):
                out.append(apply_fancy_phrase(part, style))
            else:
                out.append(part)
        else:
            out.append(part)
    return ''.join(out)


def find_bullet_indices(lines):
    to_bullet = set()
    for i in range(len(lines)):
        if not lines[i].strip():
            continue
        j = i + 1
        if j >= len(lines):
            continue
        if not lines[j].strip():
            continue
        k = j
        group = []
        while k < len(lines) and lines[k].strip():
            group.append(k)
            k += 1
        if len(group) >= 2:
            for idx in group:
                to_bullet.add(idx)
    return to_bullet

# Special token regexes (improved to match separator-containing tokens as single matches)
RE_NUMBER = re.compile(r"\b\d{1,3}(?:[\,\.\s]\d{3})*(?:[\.,]\d+)?\b")
RE_PERCENT = re.compile(r"\b\d+(?:[\.,]\d+)?%")
RE_TIME = re.compile(r"\b\d{1,2}:\d{2}\b")
RE_DATE1 = re.compile(r"\b\d{1,4}[\-/]\d{1,2}[\-/]\d{1,4}\b")  # 09/09/2026, 2026-09-09
RE_DATE2 = re.compile(r"\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b", flags=re.IGNORECASE)
# tickers / indices and tokens with internal separators e.g., P/E, VN-INDEX, A-123, HOSE, VN30
RE_TICKER = re.compile(r"\b[A-Za-z0-9]+(?:[\/\-\.:][A-Za-z0-9]+)+\b|\b[A-Z]{2,}[0-9A-Z\-]*\b")

SPECIAL_PATTERNS = [RE_PERCENT, RE_DATE1, RE_DATE2, RE_TIME, RE_NUMBER, RE_TICKER]


def convert_special_match(m, style, exceptions_lower):
    txt = m.group(0)
    out_chars = []
    for ch in txt:
        if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ch.isdigit():
            out_chars.append(to_unicode_style(ch, style))
        else:
            out_chars.append(ch)
    return ''.join(out_chars)


def apply_special_formatting(text: str, style: str, exceptions_lower: set) -> str:
    for pat in SPECIAL_PATTERNS:
        text = pat.sub(lambda m: convert_special_match(m, style, exceptions_lower), text)
    return text


def convert_all_ascii_tokens(text: str, style: str, exceptions_lower: set) -> str:
    """Final pass: ensure every ASCII-only token (including separator-containing tokens)
    is converted to the chosen fancy style. This guarantees all English words are formatted
    and repeated occurrences are also formatted. We skip tokens that contain diacritics
    (Vietnamese) or are empty.
    """
    # Match runs of ASCII letters/digits possibly separated by / - . : e.g. P/E, VN-INDEX, 09/09/2026
    TOKEN_RE = re.compile(r"\b[A-Za-z0-9]+(?:[\/\-\.:][A-Za-z0-9]+)*\b")

    def _conv(m):
        tok = m.group(0)
        # skip if token has diacritic (shouldn't match) or is empty
        if not tok:
            return tok
        # Convert only ASCII letters/digits inside token
        out = []
        for ch in tok:
            if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ch.isdigit():
                out.append(to_unicode_style(ch, style))
            else:
                out.append(ch)
        return ''.join(out)

    return TOKEN_RE.sub(_conv, text)


def final_forced_replace(original_text: str, result_text: str, style: str, exceptions_lower: set) -> str:
    """Ensure that every ASCII token that appears in original_text is formatted in result_text.
    For each token in original_text (matched by TOKEN_RE), if token is not in exceptions and
    does not contain diacritics, replace occurrences of the exact ASCII token in result_text with its
    formatted version. Uses word boundaries that consider letters/digits to avoid partial replacements.
    """
    TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[\/\-\.:][A-Za-z0-9]+)*")
    seen = set()

    def _replace_token(match):
        tok = match.group(0)
        if tok in seen:
            return None
        seen.add(tok)
        # skip diacritics and exceptions
        if token_is_vietnamese(tok) or tok.lower() in exceptions_lower:
            return None
        # build formatted token
        formatted = apply_fancy_phrase(tok, style)
        # replace all exact occurrences of tok in result_text that are not part of larger alnum sequences
        pattern = re.compile(r"(?<![A-Za-z0-9])" + re.escape(tok) + r"(?![A-Za-z0-9])")
        return (tok, pattern, formatted)

    replacements = []
    for m in TOKEN_RE.finditer(original_text):
        r = _replace_token(m)
        if r:
            replacements.append(r)

    out = result_text
    for tok, pattern, formatted in replacements:
        out = pattern.sub(formatted, out)
    return out


def auto_format(text: str, use_bullets: bool = True, footer: str = None, exceptions=None, format_specials: bool = True, style: str = 'bold') -> str:
    if exceptions is None:
        exceptions = []
    exceptions_lower = set([e.lower() for e in exceptions])

    raw_lines = text.splitlines(True)
    contents = []
    endings = []
    for ln in raw_lines:
        if ln.endswith('\r\n'):
            endings.append('\r\n'); contents.append(ln[:-2])
        elif ln.endswith('\n'):
            endings.append('\n'); contents.append(ln[:-1])
        else:
            endings.append(''); contents.append(ln)

    bullet_indices = set()
    if use_bullets:
        bullet_indices = find_bullet_indices(contents)

    out_lines = []
    first_idx = None
    for i, c in enumerate(contents):
        if c.strip():
            first_idx = i
            break

    for i, content in enumerate(contents):
        line = content
        if i in bullet_indices:
            m = re.match(r"^\s*([^A-Za-z0-9À-ỹ\u00C0-\u024F\u1EA0-\u1EFF\/\-\.:]*)(.*)$", line)
            if m:
                rest = m.group(2)
                line = BULLET_SYMBOL + ' ' + rest.lstrip()
        parts = SPLIT_RE.findall(line)
        out_parts = []
        idx = 0
        N = len(parts)
        while idx < N:
            part = parts[idx]
            if LETTER_TOKEN_RE.fullmatch(part):
                j = idx + 1
                while j < N:
                    if parts[j] and LETTER_TOKEN_RE.fullmatch(parts[j]):
                        j += 1
                    elif parts[j] and not LETTER_TOKEN_RE.fullmatch(parts[j]):
                        sep = parts[j]
                        if sep.strip() == '' or re.match(r'^[,.:;&()\-–—–]$', sep.strip()):
                            j += 1
                        else:
                            break
                    else:
                        break
                full_span = parts[idx:j]
                tokens_only = LETTER_TOKEN_RE.findall(''.join(full_span))
                # determine candidate phrase: format if any token is candidate; we changed choose_token_candidate to force-format ascii words
                candidates = [choose_token_candidate(t, exceptions_lower) for t in tokens_only]
                vietnamese_nearby = any(token_is_vietnamese(t) for t in tokens_only)
                if any(t.lower() in exceptions_lower for t in tokens_only):
                    candidate_phrase = True
                else:
                    candidate_phrase = any(candidates)
                    if vietnamese_nearby:
                        # If any token has diacritics we keep those characters but still format ASCII parts
                        # We'll still treat the phrase as candidate so apply emphasis which skips diacritic characters.
                        candidate_phrase = True
                if candidate_phrase:
                    # choose style heuristics as before
                    if all(re.match(r'^[A-Z0-9\/\-\.:]+$', t) for t in tokens_only if t):
                        chosen_style = 'bold_italic'
                    elif any(contains_digit(t) for t in tokens_only):
                        chosen_style = 'bold'
                    elif any(starts_with_upper(t) for t in tokens_only):
                        total_letters = sum(len([c for c in t if c.isalpha()]) for t in tokens_only)
                        chosen_style = 'bold' if total_letters % 2 == 0 else 'italic'
                    else:
                        chosen_style = style
                    emphasized = emphasize_phrase(full_span, chosen_style, exceptions_lower)
                    out_parts.append(emphasized)
                else:
                    out_parts.append(''.join(full_span))
                idx = j
            else:
                out_parts.append(part)
                idx += 1
        out_line = ''.join(out_parts)
        if format_specials:
            out_line = apply_special_formatting(out_line, style, exceptions_lower)
        out_lines.append(out_line + endings[i])
    result = ''.join(out_lines)

    # Final forced pass: ensure tokens from the original input are formatted in the result
    result = final_forced_replace(text, result, style, exceptions_lower)

    if footer:
        if not result.endswith('\n'):
            result += '\n'
        result += '\n' + footer
    return result
