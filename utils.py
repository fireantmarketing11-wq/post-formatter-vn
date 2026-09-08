# -*- coding: utf-8 -*-
"""
utils.py
Chứa hàm to_unicode_style(s, style) chuyển ký tự ASCII a-zA-Z sang các biến thể Unicode:
 - style in {'bold', 'italic', 'bold_italic'}
Lưu ý: ký tự có dấu (Tiếng Việt) không nằm trong bảng này -> bỏ qua (caller sẽ fallback).
"""

def to_unicode_style(s: str, style: str) -> str:
    out = []
    for ch in s:
        if 'A' <= ch <= 'Z':
            if style == 'bold':
                code = 0x1D400 + (ord(ch) - ord('A'))
            elif style == 'italic':
                code = 0x1D434 + (ord(ch) - ord('A'))
            elif style == 'bold_italic':
                code = 0x1D468 + (ord(ch) - ord('A'))
            else:
                out.append(ch); continue
            out.append(chr(code))
        elif 'a' <= ch <= 'z':
            if style == 'bold':
                code = 0x1D41A + (ord(ch) - ord('a'))
            elif style == 'italic':
                code = 0x1D44E + (ord(ch) - ord('a'))
            elif style == 'bold_italic':
                code = 0x1D482 + (ord(ch) - ord('a'))
            else:
                out.append(ch); continue
            out.append(chr(code))
        else:
            # Non-ascii letter (ví dụ chữ có dấu) -> giữ nguyên (caller sẽ fallback nếu cần)
            out.append(ch)
    return "".join(out)
