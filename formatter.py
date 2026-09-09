# -*- coding: utf-8 -*-
"""
formatter.py
Cập nhật: phrase-based emphasis, preserve newlines, bullets rule, Vietnamese detection, exceptions list, always output fancy Unicode emphasis that can be copy/pasted to social.
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
    # crude check: presence of Vietnamese-specific characters (non-ASCII letters)
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
            # map according to style
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


def emphasize_phrase(phrase_tokens, style, exceptions_lower):
    # phrase_tokens is list of tokens/strings (original substrings)
    phrase = ''.join(phrase_tokens)
    # If phrase contains diacritics -> do not convert letters individually; try to wrap using unicode for ascii parts
    if any(has_diacritic(t) for t in phrase_tokens):
        # if all tokens are exceptions, allow emphasis by converting ascii parts
        if any(t.lower() in exceptions_lower for t in phrase_tokens):
            return apply_fancy_phrase(phrase, style)
        # otherwise, return phrase unchanged (no markers)
        return phrase
    # else safe to convert ascii letters
    return apply_fancy_phrase(phrase, style)


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
            # Only bullet the group if there was no blank line between header and first item (we checked)
            # and header is not part of the group
            for idx in group:
                to_bullet.add(idx)
    return to_bullet


def auto_format(text: str, use_bullets: bool = True, footer: str = None, exceptions=None) -> str:
    if exceptions is None:
        exceptions = []
    exceptions_lower = set([e.lower() for e in exceptions])

    # preserve newlines
    lines_with_endings = []
    # splitlines(True) keeps line endings
    raw_lines = text.splitlines(True)
    # Normalize to list of content without endings and remember endings
    contents = []
    endings = []
    for ln in raw_lines:
        if ln.endswith('\r\n'):
            endings.append('\r\n')
            contents.append(ln[:-2])
        elif ln.endswith('\n'):
            endings.append('\n')
            contents.append(ln[:-1])
        else:
            endings.append('')
            contents.append(ln)
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
        # if this line should be bulleted, and it's in a group, replace leading marker and apply bullet
        line = content
        if i in bullet_indices:
            # replace leading non-alphanumeric up to first alnum
            m = re.match(r"^\s*([^A-Za-z0-9À-ỹ\u00C0-\u024F\u1EA0-\u1EFF]*)(.*)$", line)
            if m:
                rest = m.group(2)
                line = BULLET_SYMBOL + ' ' + rest.lstrip()
        # now process phrase-based emphasis on this line
        parts = SPLIT_RE.findall(line)
        # parts are alternating word-like and separators
        out_parts = []
        idx = 0
        N = len(parts)
        while idx < N:
            part = parts[idx]
            if LETTER_TOKEN_RE.fullmatch(part):
                # start building a phrase of consecutive tokens (allow interleaved separators like spaces kept separate)
                # We'll collect tokens and intervening separators
                phrase_tokens = [part]
                sep_tokens = []
                j = idx + 1
                # collect subsequent tokens if they are word-like, allowing separators between
                while j < N:
                    if parts[j] and LETTER_TOKEN_RE.fullmatch(parts[j]):
                        phrase_tokens.append(parts[j])
                        j += 1
                    elif parts[j] and not LETTER_TOKEN_RE.fullmatch(parts[j]):
                        # separator; include if it's a single space or punctuation within phrase
                        sep = parts[j]
                        # allow space or small punctuation inside phrase
                        if sep.strip() == '' or re.match(r"^[,.:;&()\-–—–]$", sep.strip()):
                            sep_tokens.append(sep)
                            j += 1
                        else:
                            break
                    else:
                        break
                # Build full_phrase substrings by interleaving phrase_tokens and sep_tokens accordingly
                # Simple approach: join parts from idx to j
                full_phrase = ''.join(parts[idx:j])
                # Decide whether to emphasize this full_phrase
                # Check if any token in phrase is candidate
                tokens_only = LETTER_TOKEN_RE.findall(full_phrase)
                candidates = [choose_token_candidate(t, exceptions_lower) for t in tokens_only]
                # Context: if any token has diacritic or stopword nearby => treat as vietnamese and skip
                vietnamese_nearby = any(token_is_vietnamese(t) for t in tokens_only)
                # If any token is exception -> force candidate
                if any(t.lower() in exceptions_lower for t in tokens_only):
                    candidate_phrase = True
                else:
                    candidate_phrase = any(candidates)
                    if vietnamese_nearby:
                        # if any token has diacritic or is stopword, treat phrase as Vietnamese => skip
                        candidate_phrase = False
                if candidate_phrase:
                    # choose style: if all upper in phrase -> bold_italic; else if any token has digit or any token starts with upper -> bold/italic
                    if all(is_all_upper(t) for t in tokens_only if t):
                        style = 'bold_italic'
                    elif any(contains_digit(t) for t in tokens_only):
                        style = 'bold'
                    elif any(starts_with_upper(t) for t in tokens_only):
                        # choose bold if length of phrase letters even else italic
                        total_letters = sum(len([c for c in t if c.isalpha()]) for t in tokens_only)
                        style = 'bold' if total_letters % 2 == 0 else 'italic'
                    else:
                        style = 'bold'
                    emphasized = emphasize_phrase([p for p in parts[idx:j]], style, exceptions_lower)
                    out_parts.append(emphasized)
                else:
                    out_parts.append(full_phrase)
                idx = j
            else:
                out_parts.append(part)
                idx += 1
        out_line = ''.join(out_parts)
        # append original line ending
        out_lines.append(out_line + endings[i])
    result = ''.join(out_lines)
    if footer:
        if not result.endswith('\n'):
            result += '\n'
        result += '\n' + footer
    return result
