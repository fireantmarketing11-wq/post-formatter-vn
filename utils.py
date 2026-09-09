# -*- coding: utf-8 -*-
"""
utils.py
Use exact mapping tables provided by user for three styles: bold, italic, bold_italic.
This file maps ASCII a-zA-Z0-9 to the corresponding fancy unicode characters using the
strings you've provided. If a character has no mapping, it is left unchanged.
"""

ASCII = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# Mappings provided by user (must preserve exact characters)
BOLD_SEQ = '𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
ITALIC_SEQ = '𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍0123456789'
BOLD_ITALIC_SEQ = '𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁0123456789'

# Validate lengths
if len(ASCII) != len(BOLD_SEQ) or len(ASCII) != len(ITALIC_SEQ) or len(ASCII) != len(BOLD_ITALIC_SEQ):
    # If lengths mismatch, fall back to programmatic mapping (not expected)
    raise RuntimeError('Mapping sequences length mismatch — please ensure the provided sequences match ASCII length')

# Build dicts
BOLD_MAP = {ASCII[i]: BOLD_SEQ[i] for i in range(len(ASCII))}
ITALIC_MAP = {ASCII[i]: ITALIC_SEQ[i] for i in range(len(ASCII))}
BOLD_ITALIC_MAP = {ASCII[i]: BOLD_ITALIC_SEQ[i] for i in range(len(ASCII))}

STYLE_MAPS = {
    'bold': BOLD_MAP,
    'italic': ITALIC_MAP,
    'bold_italic': BOLD_ITALIC_MAP,
}


def to_unicode_style(s: str, style: str) -> str:
    """Convert string s to the given style using the exact mappings provided.
    Supported styles: 'bold', 'italic', 'bold_italic'. Unknown style -> return original string.
    Characters not present in the ASCII mapping are left unchanged.
    """
    if style not in STYLE_MAPS:
        return s
    mapping = STYLE_MAPS[style]
    out = []
    for ch in s:
        out.append(mapping.get(ch, ch))
    return ''.join(out)
