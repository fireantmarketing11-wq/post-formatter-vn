# -*- coding: utf-8 -*-
"""
formatter.py
Hàm auto_format(text, mode='markdown'|'fancy')
Quy tắc (heuristic):
 - Nếu từ VIẾT HOA TOÀN BỘ (>=2 ký tự): in đậm + in nghiêng (strong emphasis)
 - Nếu từ bắt đầu bằng chữ hoa: nếu dài <=3 ký tự -> in nghiêng, else -> in đậm
 - Nếu từ chứa số hoặc kết thúc bằng dấu chấm than / hỏi -> in đậm
 - Các từ khác để nguyên
 - Chế độ 'markdown' sử dụng **, *, ***; 'fancy' cố gắng chuyển chữ ASCII sang ký tự Unicode tương ứng (nếu không chuyển được thì fallback sang Markdown)

Thêm:
 - format_to_html(text, mode) trả về HTML có style cho hashtag/mention và các emphasis.
"""
import re
from utils import to_unicode_style
import html as _html

LETTER_RE = re.compile(r"([^\W\d_]+)", flags=re.UNICODE)
TAG_RE = re.compile(r"([#@])([^\s#@]+)", flags=re.UNICODE)

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
        # nếu quá ngắn -> italic, else bold; deterministic dựa vào độ dài parity
        letters = [c for c in token if c.isalpha()]
        if len(letters) <= 3:
            return 'italic'
        else:
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
    if mapped and any('A' <= ch <= 'Z' or 'a' <= ch <= 'z' for ch in token):
        if mapped == token:
            return apply_markdown(token, style)
        return mapped
    else:
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
    def _repl(m):
        return replacer(m, mode=mode)
    out = re.sub(LETTER_RE, _repl, text)
    return out

# HTML conversion

def _wrap_html(token: str, style: str, extra_class: str = None) -> str:
    content = _html.escape(token)
    open_tags = []
    close_tags = []
    if style == 'bold_italic':
        open_tags.extend(['<strong>', '<em>'])
        close_tags.extend(['</em>', '</strong>'])
    elif style == 'bold':
        open_tags.append('<strong>')
        close_tags.append('</strong>')
    elif style == 'italic':
        open_tags.append('<em>')
        close_tags.append('</em>')
    inner = ''.join(open_tags) + content + ''.join(close_tags)
    if extra_class:
        return f'<span class="{extra_class}">{inner}</span>'
    return inner

def format_to_html(text: str, mode: str = 'markdown') -> str:
    # First, handle tags (hashtags/mentions) so we can wrap '#' or '@' together with word
    def tag_repl(m):
        sign = _html.escape(m.group(1))
        token = m.group(2)
        style = choose_style(token)
        cls = 'hashtag' if sign == '#' else 'mention'
        # create inner with sign + token
        inner_token = sign + token
        # If fancy mode and ascii, try to convert token part
        if mode == 'fancy':
            try:
                if style == 'bold':
                    mapped = to_unicode_style(token, 'bold')
                elif style == 'italic':
                    mapped = to_unicode_style(token, 'italic')
                elif style == 'bold_italic':
                    mapped = to_unicode_style(token, 'bold_italic')
                else:
                    mapped = None
            except Exception:
                mapped = None
            if mapped and any('A' <= ch <= 'Z' or 'a' <= ch <= 'z' for ch in token):
                inner = _html.escape(sign) + mapped
                if style == 'bold_italic':
                    inner = '<strong><em>' + inner + '</em></strong>'
                elif style == 'bold':
                    inner = '<strong>' + inner + '</strong>'
                elif style == 'italic':
                    inner = '<em>' + inner + '</em>'
                return '<span class="' + cls + '">' + inner + '</span>'
        # fallback or markdown mode
        return _wrap_html(inner_token, style, extra_class=cls)

    step1 = re.sub(TAG_RE, tag_repl, text)

    # Then wrap remaining plain letter tokens
    def letter_repl(m):
        token = m.group(0)
        style = choose_style(token)
        if style is None:
            return _html.escape(token)
        return _wrap_html(token, style)

    body = re.sub(LETTER_RE, letter_repl, step1)

    # Build HTML using normal strings (NOT f-strings) so { } in CSS/JS are safe
    html = (
        "<!doctype html>\n"
        "<html lang=\"vi\">\n"
        "<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        "<title>Preview - Trình Định dạng Bài Post</title>\n"
        "<style>\n"
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding: 24px; line-height:1.6; color:#111 }\n"
        ".hashtag { color: #1da1f2; font-weight:600 }\n"
        ".mention { color: #16a34a }\n"
        "strong { font-weight:700 }\n"
        "em { font-style: italic }\n"
        ".container { max-width:780px }\n"
        ".copy-btn { position: fixed; right: 18px; top: 18px; padding:8px 12px; background:#111; color:#fff; border-radius:6px; cursor:pointer }\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "<div class=\"container\">\n"
        + body +
        "\n</div>\n"
        "<script>\n"
        "function copyText(){\n"
        "  const t = document.body.innerText;\n"
        "  navigator.clipboard.writeText(t).then(()=>alert('Đã sao chép nội dung (text)'));\n"
        "}\n"
        "</script>\n"
        "</body>\n"
        "</html>"
    )
    return html
