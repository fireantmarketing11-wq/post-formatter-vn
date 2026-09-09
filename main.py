#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
Ứng dụng GUI nhỏ để định dạng bài đăng mạng xã hội tự động.
Cập nhật: thêm chọn font hiển thị cho Output (để hỗ trợ ký tự Unicode fancy như 𝐭𝐞𝐬𝐭).
Chạy: python main.py
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont
from formatter import auto_format
import os
import config

APP_TITLE = "Trình Định dạng Bài Post (Tiếng Việt)"

# Fonts to thử (tên font trên Windows / hệ thống). Người dùng có thể nhập tên khác trong ô chọn.
FONT_OPTIONS = [
    "Cambria Math",
    "Segoe UI Symbol",
    "Symbola",
    "Noto Sans Symbols",
    "Arial Unicode MS",
    "DejaVu Sans",
    "Liberation Sans",
    "Segoe UI",
]


def load_sample():
    path = os.path.join(os.path.dirname(__file__), "sample_input.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        input_text.delete("1.0", tk.END)
        input_text.insert("1.0", txt)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không mở được file mẫu:\n{e}")


def open_file():
    p = filedialog.askopenfilename(title="Chọn file văn bản", filetypes=[("Text","*.txt"),("All files","*.*")])
    if p:
        try:
            with open(p, "r", encoding="utf-8") as f:
                txt = f.read()
            input_text.delete("1.0", tk.END)
            input_text.insert("1.0", txt)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không mở được file:\n{e}")


def save_output():
    p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")], title="Lưu kết quả ra file")
    if p:
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(output_text.get("1.0", tk.END).rstrip())
            messagebox.showinfo("Đã lưu", f"Đã lưu kết quả vào:\n{p}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không lưu được file:\n{e}")


def copy_output():
    o = output_text.get("1.0", tk.END).rstrip()
    root.clipboard_clear()
    root.clipboard_append(o)
    messagebox.showinfo("Sao chép", "Đã sao chép phần Output vào clipboard.")


def format_action():
    try:
        src = input_text.get("1.0", tk.END)
        if not src.strip():
            messagebox.showwarning("Chưa có nội dung", "Vui lòng nhập hoặc dán nội dung vào ô Input.")
            return
        use_bullets = bool(bullets_var.get())
        include_footer = bool(footer_enable_var.get())
        footer_text = footer_textbox.get("1.0", tk.END).strip() if include_footer else None
        exceptions_raw = exceptions_text.get("1.0", tk.END).strip()
        exceptions = [e.strip() for e in exceptions_raw.split(',') if e.strip()]
        # ensure output widget editable
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        res = auto_format(src, use_bullets=use_bullets, footer=footer_text, exceptions=exceptions)
        output_text.insert("1.0", res)
        # leave output editable for easy copy/paste
    except Exception as e:
        import traceback, sys
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        messagebox.showerror("Lỗi khi định dạng", f"Đã xảy ra lỗi, xem terminal/console.\n{e}")


def save_config():
    cfg = config.load()
    cfg['footer'] = footer_textbox.get("1.0", tk.END).strip()
    cfg['include_footer'] = bool(footer_enable_var.get())
    cfg['use_bullets'] = bool(bullets_var.get())
    exceptions_raw = exceptions_text.get("1.0", tk.END).strip()
    cfg['exceptions'] = [e.strip() for e in exceptions_raw.split(',') if e.strip()]
    # font
    cfg['font_family'] = font_var.get()
    config.save(cfg)
    messagebox.showinfo("Đã lưu", "Đã lưu cấu hình (footer, bullets, exceptions, font).")


def apply_font_selection(event=None):
    fam = font_var.get()
    try:
        f = tkfont.Font(family=fam, size=12)
        output_text.configure(font=f)
        # also set input font slightly for consistency
        input_text.configure(font=tkfont.Font(family=fam, size=12))
    except Exception:
        messagebox.showwarning("Font không hợp lệ", f"Không thể áp dụng font: {fam}. Hệ thống sẽ dùng font mặc định.")


# GUI
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1100x740")

# Toolbar frame
toolbar = ttk.Frame(root)
toolbar.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

ttk.Button(toolbar, text="Mở file", command=open_file).pack(side=tk.LEFT, padx=4)
ttk.Button(toolbar, text="Tải ví dụ", command=load_sample).pack(side=tk.LEFT, padx=4)
ttk.Button(toolbar, text="Định dạng", command=format_action).pack(side=tk.LEFT, padx=8)

# Save/Copy buttons
ttk.Button(toolbar, text="Lưu Output", command=save_output).pack(side=tk.RIGHT, padx=4)
ttk.Button(toolbar, text="Sao chép Output", command=copy_output).pack(side=tk.RIGHT, padx=4)

# Font selection in toolbar
font_var = tk.StringVar()
font_combo = ttk.Combobox(toolbar, textvariable=font_var, values=FONT_OPTIONS + ["(custom)"], width=24)
font_combo.set(FONT_OPTIONS[0])
font_combo.pack(side=tk.RIGHT, padx=8)
font_combo.bind("<<ComboboxSelected>>", apply_font_selection)

# Panes
panes = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
panes.pack(fill=tk.BOTH, expand=1, padx=6, pady=6)

left_frame = ttk.Labelframe(panes, text="Input (Dán bài ở đây)")
right_frame = ttk.Labelframe(panes, text="Output (Kết quả định dạng)")

panes.add(left_frame, weight=1)
panes.add(right_frame, weight=1)

# Input text
input_text = tk.Text(left_frame, wrap=tk.WORD, font=("Helvetica", 12))
input_text.pack(fill=tk.BOTH, expand=1, padx=6, pady=6)

# Output text - font will be set after loading config
output_text = tk.Text(right_frame, wrap=tk.WORD, font=("Helvetica", 12))
output_text.pack(fill=tk.BOTH, expand=1, padx=6, pady=6)

# Footer / options frame
opts = ttk.Frame(root)
opts.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)

bullets_var = tk.IntVar(value=1)
footer_enable_var = tk.IntVar(value=0)

ttk.Checkbutton(opts, text="Thay bullet cho các dòng danh sách (•  )", variable=bullets_var).pack(side=tk.LEFT, padx=8)
ttk.Checkbutton(opts, text="Thêm footer vào output", variable=footer_enable_var).pack(side=tk.LEFT, padx=8)

# Exceptions area
exceptions_frame = ttk.Labelframe(root, text="Exceptions (từ/cụm không muốn để tool bỏ qua) - phân tách bằng dấu phẩy")
exceptions_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)
exceptions_text = tk.Text(exceptions_frame, height=2, wrap=tk.WORD)
exceptions_text.pack(fill=tk.X, padx=6, pady=6)

# Footer frame
footer_frame = ttk.Labelframe(root, text="Footer (sẽ được lưu và tải lại)")
footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)
footer_textbox = tk.Text(footer_frame, height=3, wrap=tk.WORD)
footer_textbox.pack(fill=tk.X, padx=6, pady=6)
ttk.Button(footer_frame, text="Lưu cấu hình (footer, bullets, exceptions, font)", command=save_config).pack(side=tk.RIGHT, padx=6, pady=4)

# Load config
cfg = config.load()
footer_textbox.delete("1.0", tk.END)
footer_textbox.insert("1.0", cfg.get('footer',''))
footer_enable_var.set(1 if cfg.get('include_footer') else 0)
bullets_var.set(1 if cfg.get('use_bullets', True) else 0)
exceptions_text.delete("1.0", tk.END)
exceptions_text.insert("1.0", ', '.join(cfg.get('exceptions', [])))
font_var.set(cfg.get('font_family', FONT_OPTIONS[0]))

# apply selected font
try:
    f = tkfont.Font(family=font_var.get(), size=12)
    output_text.configure(font=f)
    input_text.configure(font=tkfont.Font(family=font_var.get(), size=12))
except Exception:
    # keep default fonts if requested font not available
    pass

# Footer hint
footer = ttk.Label(root, text="Luật định dạng: Tự động chọn các cụm từ quan trọng và chuyển sang ký tự Unicode để copy/paste lên social. Không format từ tiếng Việt có dấu hoặc cụm tiếng Việt.", anchor="w")
footer.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=4)

# Load example by default
load_sample()

root.mainloop()
