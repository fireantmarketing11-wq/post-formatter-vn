# -*- coding: utf-8 -*-
"""
formatter.py
Cập nhật: giữ phrase-based emphasis, preserve newlines, bullets rule, Vietnamese detection, exceptions list.
Mới: hỗ trợ format các token đặc biệt (số, phần trăm, ngày/thời gian, chỉ số/tickers) bằng cách convert chữ ASCII và chữ số bên trong các token đó
sang các ký tự fancy unicode (sử dụng to_unicode_style từ utils).
"""
import re
from utils import to_unicode_style

# minimal Vietnamese stopwords to detect Vietnamese context
VIET_STOPWORDS = set([
    'và','là','của','cho','trên','với','các','những','một','như','được','để','khi','vì','đã','vẫn','có','không','bạn','mình','từ'
])

LETTER_TOKEN_RE = re.compile(r"[A-Za-z0-9À-ỹ̀-ỹ]+", flags=re.UNICODE)
SPLIT_RE = re.compile(r"([A-Za-z0-9À-ỹ̀-ỹ]+|[^A-Za-z0-9À-ỹ̀-ỹ]+)", flags=re.UNICODE)

# bullet symbol
BULLET_SYMBOL = '•\u2060\u2009'

# helpers

def has_diacritic(s: str) -> bool:
    for ch in s:
        if ord(ch) > 127:
            return True
    return False


def is_all_upper(token: str) -> bool:
    letters = [c for c in token if c.isalpha()]
    if len(letters) < 2:
        return False
    return all(c.upper() == c and c.isalpha() for c in letters)


def starts_with_upper(token: str) -> bool:
    for c in token:
        if c.isalpha():
            return c == c.upper()
    return False


def contains_digit(token: str) -> bool:
    return any(ch.isdigit() for ch in token)


def token_is_vietnamese(token: str) -> bool:
    if has_diacritic(token):
        return True
    if token.lower() in VIET_STOPWORDS:
        return True
    return False


def choose_token_candidate(token: str, exceptions_lower: set):
    if not token:
        return False
    if token.lower() in exceptions_lower:
        return True
    if token_is_vietnamese(token):
        return False
    if not re.search(r"[A-Za-z]", token):
        return contains_digit(token)
    letters = [c for c in token if c.isalpha()]
    if len(letters) <= 2:
        return False
    if is_all_upper(token) or starts_with_upper(token) or contains_digit(token):
        return True
    return False


def apply_fancy_phrase(phrase: str, style: str) -> str:
    out = []
    for ch in phrase:
        if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or ch.isdigit():
            out.append(to_unicode_style(ch, style))
        else:
            out.append(ch)
    return ''.join(out)


def emphasize_phrase(phrase_parts, style, exceptions_lower):
    out = []
    for part in phrase_parts:
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

# Special token regexes
# We'll detect and convert numbers, percents, currencies, dates, times, indices/tickers
RE_NUMBER = re.compile(r"\b\d{1,3}(?:[\,\.\s]\d{3})*(?:[\.,]\d+)?\b")
RE_PERCENT = re.compile(r"\b\d+(?:[\.,]\d+)?%")
RE_TIME = re.compile(r"\b\d{1,2}:\d{2}\b")
RE_DATE1 = re.compile(r"\b\d{1,4}[\-/]\d{1,2}[\-/]\d{1,4}\b")  # 09/09/2026, 2026-09-09
RE_DATE2 = re.compile(r"\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b", flags=re.IGNORECASE)
RE_TICKER = re.compile(r"\b[A-Z0-9\-]{2,}\b")  # VN-INDEX, VN30, FPT, VNM

SPECIAL_PATTERNS = [RE_PERCENT, RE_DATE1, RE_DATE2, RE_TIME, RE_NUMBER, RE_TICKER]


def convert_special_match(m, style, exceptions_lower):
    txt = m.group(0)
    # convert only ASCII letters and digits inside txt
    out_chars = []
    for ch in txt:
        if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ch.isdigit():
            # if part is in exceptions (lowercase compare) and is alpha sequence, keep converting only if listed
            out_chars.append(to_unicode_style(ch, style))
        else:
            out_chars.append(ch)
    return ''.join(out_chars)


def apply_special_formatting(text: str, style: str, exceptions_lower: set) -> str:
    # Apply patterns sequentially; re.sub with function to convert matches
    for pat in SPECIAL_PATTERNS:
        text = pat.sub(lambda m: convert_special_match(m, style, exceptions_lower), text)
    return text


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
            m = re.match(r"^\s*([^A-Za-z0-9À-ỹ\u00C0-\u024F\u1EA0-\u1EFF]*)(.*)$", line)
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
                candidates = [choose_token_candidate(t, exceptions_lower) for t in tokens_only]
                vietnamese_nearby = any(token_is_vietnamese(t) for t in tokens_only)
                if any(t.lower() in exceptions_lower for t in tokens_only):
                    candidate_phrase = True
                else:
                    candidate_phrase = any(candidates)
                    if vietnamese_nearby:
                        candidate_phrase = False
                if candidate_phrase:
                    if all(is_all_upper(t) for t in tokens_only if t):
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
        # after phrase-based emphasis, apply special token formatting if enabled
        if format_specials:
            out_line = apply_special_formatting(out_line, style, exceptions_lower)
        out_lines.append(out_line + endings[i])
    result = ''.join(out_lines)
    if footer:
        if not result.endswith('\n'):
            result += '\n'
        result += '\n' + footer
    return result
