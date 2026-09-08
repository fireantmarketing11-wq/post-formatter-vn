# -*- coding: utf-8 -*-
"""
formatter.py
Hàm auto_format(text, mode='markdown'|'fancy')
Quy tắc (heuristic):
 - Nếu từ VIẾT HOA TOÀN BỘ (>=2 ký tự): in đậm + in nghiêng (strong emphasis)
 - Nếu từ bắt đầu bằng chữ hoa: nếu dài <=3 ký tự -> in nghiêng, else -> in đậm
 - Nếu từ chứa số hoặc kết thúc bằng dấu chấm than / hỏi -> in đậm
 - Các từ khác để nguyên
 - Chế độ 'markdown' sử dụng **, *, ***, 'fancy' cố gắng chuyển chữ ASCII sang ký tự Unicode tương ứng (nếu không chuyển được thì fallback sang Markdown)
"""
import re
from utils import to_unicode_style

LETTER_RE = re.compile(r"([^\W\d_]+)", flags=re.UNICODE)

def is_all_upper(token: str) -> bool:
    # Có ít nhất 2 ký tự chữ và tất cả chữ là uppercase theo Unicode
    letters = [c for c in token if c.isalpha()]
    if len(letters) < 2:
        return False
    return all(c.upper() == c and c.isalpha() for c in letters) and any(c.isalpha() for c in token)

def starts_with_upper(token: str) -> bool:
    for c in token:
        if c.isalpha():
            return c == c.upper()
    return False

def contains_digit(token: str) -> bool:
    return any(ch.isdigit() for ch in token)

def choose_style(token: str):
    # trả về 'bold', 'italic', 'bold_italic', hoặc None
    if is_all_upper(token):
        return 'bold_italic'
    if contains_digit(token) or token.endswith('!') or token.endswith('?'):
        return 'bold'
    if starts_with_upper(token):
        # nếu quá ngắn -> italic, else bold; đây là cách "tùy" tự động
        letters = [c for c in token if c.isalpha()]
        if len(letters) <= 3:
            return 'italic'
        else:
            # kết hợp thêm biến đổi ngẫu nhiên có thể làm nội dung phong phú;
            # để deterministic, dựa vào độ dài parity
            return 'bold' if (len(letters) % 2 == 0) else 'italic'
    return None

def apply_markdown(token: str, style: str):
    if style == 'bold_italic':
        return f'***{token}***'
    if style == 'bold':
        return f'**{token}**'
    if style == 'italic':
        return f'*{token}*'
    return token

def apply_fancy(token: str, style: str):
    # cố gắng chuyển các chữ ASCII sang unicode style; với ký tự khác (ví dụ dấu tiếng Việt) fallback sang markdown wrap
    mapped = None
    try:
        if style == 'bold':
            mapped = to_unicode_style(token, 'bold')
        elif style == 'italic':
            mapped = to_unicode_style(token, 'italic')
        elif style == 'bold_italic':
            mapped = to_unicode_style(token, 'bold_italic')
    except Exception:
        mapped = None
    # kiểm tra nếu mapped giống token (không đổi ký tự ASCII), hoặc token chứa ký tự ngoài ascii -> fallback
    if mapped and any('A' <= ch <= 'Z' or 'a' <= ch <= 'z' for ch in token):
        # Nếu token có cả chữ non-ascii (điểm diacritics) mapped sẽ giữ original; fallback để dễ nhìn
        if mapped == token:
            return apply_markdown(token, style)
        return mapped
    else:
        # fallback: dùng markdown markers
        return apply_markdown(token, style)

def replacer(match, mode='markdown'):
    token = match.group(0)
    style = choose_style(token)
    if style is None:
        return token
    if mode == 'markdown':
        return apply_markdown(token, style)
    else:
        return apply_fancy(token, style)

def auto_format(text: str, mode: str = 'markdown') -> str:
    if mode not in ('markdown', 'fancy'):
        mode = 'markdown'
    # Thay từng block chữ (chỉ letters) theo quy tắc
    def _repl(m):
        return replacer(m, mode=mode)
    out = re.sub(LETTER_RE, _repl, text)
    return out
