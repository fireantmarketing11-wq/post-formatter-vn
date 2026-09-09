# -*- coding: utf-8 -*-
"""
config.py
Lưu cấu hình đơn giản (footer, include_footer, use_bullets, exceptions, format_specials) vào config.json trong thư mục project.
"""
import json
import os

CFG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

DEFAULT = {
    'footer': '',
    'include_footer': False,
    'use_bullets': True,
    'exceptions': [],
    'format_specials': True
}

def load():
    try:
        if os.path.exists(CFG_PATH):
            with open(CFG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULT.copy()

def save(d):
    try:
        with open(CFG_PATH, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
