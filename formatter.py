# -*- coding: utf-8 -*-
"""
formatter.py
Cập nhật: giữ nguyên dòng xuống (preserve newlines), hỗ trợ chuyển các dòng danh sách sang bullet '•\u2060\u2009' khi cần,
heuristic thông minh hơn: không định dạng các từ rất ngắn (<=2) trừ khi viết HOA toàn bộ; nhận diện tiêu đề (dòng tiêu đề đầu tiên) để format mạnh.
format_to_html giờ bảo toàn xuống dòng (dùng <br>) và hỗ trợ include footer.
"""
import re
from utils import to_unicode_style
import html as _html

LETTER_RE = re.compile(r"([^\W\d_]+)", flags=re.UNICODE)
TAG_RE = re.compile(r"([#@])([^\s#@]+)", flags=re.UNICODE)

# Bullet symbol: bullet + word-joiner + thin space to approximate "•⁠  ⁠"
BULLET_SYMBOL = '•\u2060\u2009'

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

def choose_style(token: str):
    # Tránh format các từ quá ngắn trừ khi là ALL UPPER
    letters = [c for c in token if c.isalpha()]
    if is_all_upper(token):
        return 'bold_italic'
    if len(letters) <= 2:
        return None
    if contains_digit(token) or token.endswith('!') or token.endswith('?'):
        return 'bold'
    if starts_with_upper(token):
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

def format_line(line: str, mode: str = 'markdown', use_bullets: bool = True, is_title: bool = False) -> str:
    stripped = line.lstrip()
    # Detect list-like line (starts with common markers)
    list_mark = None
    if stripped.startswith(('-', '*', '•', '◻', '\u2610', '[')) or stripped.startswith('\u25A1'):
        list_mark = True
    # Also detect lines that start with an emoji icon (common emoji separated by space)
    if len(stripped) > 0 and ord(stripped[0]) > 10000:
        # rough emoji detection: non-ascii high codepoint at start
        list_mark = True
    # If use_bullets and looks like list, replace leading marker with BULLET_SYMBOL
    if use_bullets and list_mark:
        # remove leading non-alphanumeric until first letter/num
        m = re.match(r"^\s*([^A-Za-z0-9\u00C0-\u024F\u1EA0-\u1EFF]*)(.*)$", line)
        if m:
            rest = m.group(2)
            line = BULLET_SYMBOL + ' ' + rest.lstrip()
    # Process words but keep whitespace
    def repl(m):
        token = m.group(0)
        # If this is title line, prefer stronger emphasis for title words
        if is_title:
            # If token longer than 2 letters, make bold or bold_italic if all upper
            if is_all_upper(token):
                style = 'bold_italic'
            else:
                letters = [c for c in token if c.isalpha()]
                if len(letters) <= 2:
                    return token
                style = 'bold' if len(letters) > 2 else None
        else:
            style = choose_style(token)
        if style is None:
            return token
        return apply_fancy(token, style) if mode == 'fancy' else apply_markdown(token, style)
    out = re.sub(LETTER_RE, repl, line)
    return out

def auto_format(text: str, mode: str = 'markdown', use_bullets: bool = True, footer: str = None) -> str:
    if mode not in ('markdown', 'fancy'):
        mode = 'markdown'
    # Preserve original newline structure
    lines = text.splitlines(True)  # keepends
    out_lines = []
    # find first non-empty line as title
    first_idx = None
    for i, ln in enumerate(lines):
        if ln.strip():
            first_idx = i
            break
    for i, ln in enumerate(lines):
        is_title = (i == first_idx)
        # process line (without trailing newline) and re-append newline
        ending = ''
        if ln.endswith('\r\n'):
            ending = '\r\n'
            content = ln[:-2]
        elif ln.endswith('\n'):
            ending = '\n'
            content = ln[:-1]
        else:
            content = ln
        formatted = format_line(content, mode=mode, use_bullets=use_bullets, is_title=is_title)
        out_lines.append(formatted + ending)
    result = ''.join(out_lines)
    if footer:
        if not result.endswith('\n'):
            result += '\n'
        result += '\n' + footer
    return result

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

def format_to_html(text: str, mode: str = 'markdown', use_bullets: bool = True, footer: str = None) -> str:
    # handle tags
    def tag_repl(m):
        sign = _html.escape(m.group(1))
        token = m.group(2)
        style = choose_style(token)
        cls = 'hashtag' if sign == '#' else 'mention'
        inner_token = sign + token
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
        return _wrap_html(inner_token, style, extra_class=cls)

    step1 = re.sub(TAG_RE, tag_repl, text)

    # Process lines and preserve breaks using <br>
    lines = step1.splitlines(True)
    processed_lines = []
    # find title index
    first_idx = None
    for i, ln in enumerate(lines):
        if ln.strip():
            first_idx = i
            break
    for i, ln in enumerate(lines):
        is_title = (i == first_idx)
        content = ln.rstrip('\r\n')
        # handle bullets replacement (same as auto_format)
        if use_bullets:
            stripped = content.lstrip()
            if stripped.startswith(('-', '*', '•', '◻') ) or (len(stripped) > 0 and ord(stripped[0]) > 10000):
                m = re.match(r"^\s*([^A-Za-z0-9\u00C0-\u024F\u1EA0-\u1EFF]*)(.*)$", content)
                if m:
                    rest = m.group(2)
                    content = BULLET_SYMBOL + ' ' + _html.escape(rest.lstrip())
        # process remaining word tokens
        def letter_repl(m):
            token = m.group(0)
            style = choose_style(token) if not is_title else ('bold_italic' if is_all_upper(token) else ('bold' if len([c for c in token if c.isalpha()])>2 else None))
            if style is None:
                return _html.escape(token)
            inner = _wrap_html(token, style)
            return inner
        processed = re.sub(LETTER_RE, letter_repl, content)
        # replace line breaks with <br>
        processed_lines.append(processed + '<br>')
    body = '\n'.join(processed_lines)
    if footer:
        body += '\n<br>\n' + _html.escape(footer)

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
