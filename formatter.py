# -*- coding: utf-8 -*-
"""
formatter.py
Cập nhật: phrase-based emphasis, preserve newlines, bullets rule, Vietnamese detection, exceptions list.
Điều chỉnh: khi một cụm chứa cả token có dấu và không có dấu, sẽ chỉ chuyển các token ASCII không dấu sang fancy unicode (không bỏ qua toàn cụm) — khắc phục trường hợp tiêu đề có mix ASCII + tiếng Việt.
"""
import re
from utils import to_unicode_style

# minimal Vietnamese stopwords to detect Vietnamese context
VIET_STOPWORDS = set([
    'và','là','của','cho','trên','với','các','những','một','như','được','để','khi','vì','đã','vẫn','có','không','bạn','mình','của','từ'
])

LETTER_TOKEN_RE = re.compile(r"[A-Za-z0-9À-ỹ̀-ỹ]+", flags=re.UNICODE)
SPLIT_RE = re.compile(r"([A-Za-z0-9À-ỹ̀-ỹ]+|[^A-Za-z0-9À-ỹ̀-ỹ]+)", flags=re.UNICODE)

# bullet symbol
BULLET_SYMBOL = '•\u2060\u2009'

# helpers

def has_diacritic(s: str) -> bool:
    # crude check: presence of non-ASCII letters (used as indicator for Vietnamese characters)
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
    # if has diacritics -> Vietnamese
    if has_diacritic(token):
        return True
    # if token lower in stopwords
    if token.lower() in VIET_STOPWORDS:
        return True
    return False


def choose_token_candidate(token: str, exceptions_lower: set):
    # Determine if token is candidate for emphasis
    if not token:
        return False
    if token.lower() in exceptions_lower:
        return True
    if token_is_vietnamese(token):
        return False
    # require ascii letter presence
    if not re.search(r"[A-Za-z]", token):
        # numbers/symbols maybe; allow if contains digit
        return contains_digit(token)
    # skip short tokens
    letters = [c for c in token if c.isalpha()]
    if len(letters) <= 2:
        return False
    # candidate if starts with upper or all upper or contains digit
    if is_all_upper(token) or starts_with_upper(token) or contains_digit(token):
        return True
    # otherwise not candidate
    return False


def apply_fancy_phrase(phrase: str, style: str) -> str:
    # apply unicode mapping to ascii letters only; keep other chars as-is
    out = []
    for ch in phrase:
        if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z':
            if style == 'bold':
                out.append(to_unicode_style(ch, 'bold'))
            elif style == 'italic':
                out.append(to_unicode_style(ch, 'italic'))
            elif style == 'bold_italic':
                out.append(to_unicode_style(ch, 'bold_italic'))
            else:
                out.append(ch)
        else:
            out.append(ch)
    return ''.join(out)


def emphasize_phrase(phrase_parts, style, exceptions_lower):
    """
    phrase_parts: list of substrings (may include separators).
    We will apply fancy mapping to tokens without diacritics or tokens listed in exceptions,
    and leave other tokens (e.g., Vietnamese with diacritics) unchanged.
    """
    out = []
    for part in phrase_parts:
        # if this substring is a word-like token
        if LETTER_TOKEN_RE.fullmatch(part):
            if part.lower() in exceptions_lower:
                out.append(apply_fancy_phrase(part, style))
            elif not has_diacritic(part):
                # ascii-only word (or ascii letters) -> convert
                out.append(apply_fancy_phrase(part, style))
            else:
                # token has diacritics (Vietnamese) -> keep as-is
                out.append(part)
        else:
            # separators/punctuation -> keep
            out.append(part)
    return ''.join(out)


def find_bullet_indices(lines):
    # lines: list of raw line strings (without newline endings)
    to_bullet = set()
    for i in range(len(lines)):
        # line i is potential header if non-empty
        if not lines[i].strip():
            continue
        # check immediate next line exists and is non-empty
        j = i + 1
        if j >= len(lines):
            continue
        if not lines[j].strip():
            continue
        # now collect contiguous non-empty lines starting at j
        k = j
        group = []
        while k < len(lines) and lines[k].strip():
            group.append(k)
            k += 1
        # require group length >=2
        if len(group) >= 2:
            for idx in group:
                to_bullet.add(idx)
    return to_bullet


def auto_format(text: str, use_bullets: bool = True, footer: str = None, exceptions=None) -> str:
    if exceptions is None:
        exceptions = []
    exceptions_lower = set([e.lower() for e in exceptions])

    # preserve newlines
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

    # detect bullet groups
    bullet_indices = set()
    if use_bullets:
        bullet_indices = find_bullet_indices(contents)

    out_lines = []
    # find first non-empty line index as title
    first_idx = None
    for i, c in enumerate(contents):
        if c.strip():
            first_idx = i
            break

    for i, content in enumerate(contents):
        is_title = (i == first_idx)
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
                # collect phrase span
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
                        style = 'bold_italic'
                    elif any(contains_digit(t) for t in tokens_only):
                        style = 'bold'
                    elif any(starts_with_upper(t) for t in tokens_only):
                        total_letters = sum(len([c for c in t if c.isalpha()]) for t in tokens_only)
                        style = 'bold' if total_letters % 2 == 0 else 'italic'
                    else:
                        style = 'bold'
                    emphasized = emphasize_phrase(full_span, style, exceptions_lower)
                    out_parts.append(emphasized)
                else:
                    out_parts.append(''.join(full_span))
                idx = j
            else:
                out_parts.append(part)
                idx += 1
        out_line = ''.join(out_parts)
        out_lines.append(out_line + endings[i])
    result = ''.join(out_lines)
    if footer:
        if not result.endswith('\n'):
            result += '\n'
        result += '\n' + footer
    return result
