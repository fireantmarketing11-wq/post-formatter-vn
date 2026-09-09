---
*** Begin Patch
*** Update File: formatter.py
@@
 def apply_special_formatting(text: str, style: str, exceptions_lower: set) -> str:
     for pat in SPECIAL_PATTERNS:
         text = pat.sub(lambda m: convert_special_match(m, style, exceptions_lower), text)
     return text
+
+
+def convert_all_ascii_tokens(text: str, style: str, exceptions_lower: set) -> str:
+    """Final pass: ensure every ASCII-only token (including separator-containing tokens)
+    is converted to the chosen fancy style. This guarantees all English words are formatted
+    and repeated occurrences are also formatted. We skip tokens that contain diacritics
+    (Vietnamese) or are empty.
+    """
+    # Match runs of ASCII letters/digits possibly separated by / - . : e.g. P/E, VN-INDEX, 09/09/2026
+    TOKEN_RE = re.compile(r"\b[A-Za-z0-9]+(?:[\/\-\.:][A-Za-z0-9]+)*\b")
+
+    def _conv(m):
+        tok = m.group(0)
+        # skip if token has diacritic (shouldn't match) or is empty
+        if not tok:
+            return tok
+        # If token in exceptions (exact lower) -> do not skip (we still format)
+        # Convert only ASCII letters/digits inside token
+        out = []
+        for ch in tok:
+            if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ch.isdigit():
+                out.append(to_unicode_style(ch, style))
+            else:
+                out.append(ch)
+        return ''.join(out)
+
+    return TOKEN_RE.sub(_conv, text)
*** End Patch
