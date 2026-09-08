#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
Ứng dụng GUI nhỏ để định dạng bài đăng mạng xã hội tự động.
Chạy: python main.py
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from formatter import auto_format
import os

APP_TITLE = "Trình Định dạng Bài Post (Tiếng Việt)"

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
    src = input_text.get("1.0", tk.END).strip()
    if not src:
        messagebox.showwarning("Chưa có nội dung", "Vui lòng nhập hoặc dán nội dung vào ô Input.")
        return
    mode = mode_var.get()
    res = auto_format(src, mode=mode)
    output_text.delete("1.0", tk.END)
    output_text.insert("1.0", res)

# GUI
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("900x600")

# Toolbar frame
toolbar = ttk.Frame(root)
toolbar.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

ttk.Button(toolbar, text="Mở file", command=open_file).pack(side=tk.LEFT, padx=4)
ttk.Button(toolbar, text="Tải ví dụ", command=load_sample).pack(side=tk.LEFT, padx=4)
ttk.Button(toolbar, text="Định dạng", command=format_action).pack(side=tk.LEFT, padx=8)

mode_var = tk.StringVar(value="markdown")
ttk.Label(toolbar, text="Chế độ:").pack(side=tk.LEFT, padx=(12,4))
mode_combo = ttk.Combobox(toolbar, textvariable=mode_var, values=["markdown", "fancy"], width=10, state="readonly")
mode_combo.pack(side=tk.LEFT)

ttk.Button(toolbar, text="Sao chép Output", command=copy_output).pack(side=tk.RIGHT, padx=4)
ttk.Button(toolbar, text="Lưu Output", command=save_output).pack(side=tk.RIGHT, padx=4)

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

# Output text
output_text = tk.Text(right_frame, wrap=tk.WORD, font=("Helvetica", 12))
output_text.pack(fill=tk.BOTH, expand=1, padx=6, pady=6)

# Footer hint
footer = ttk.Label(root, text="Luật định dạng: Tự động chọn từ cần nhấn mạnh. Chọn chế độ Markdown (**) hoặc Fancy (ký tự Unicode).", anchor="w")
footer.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=4)

# Load example by default
load_sample()

root.mainloop()
