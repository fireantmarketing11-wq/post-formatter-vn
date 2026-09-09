---
*** Begin Patch
*** Update File: main.py
@@
 def save_output():
-    p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")], title="Lưu kết quả ra file")
-    if p:
-        try:
-            with open(p, "w", encoding="utf-8") as f:
-                f.write(output_text.get("1.0", tk.END).rstrip())
-            messagebox.showinfo("Đã lưu", f"Đã lưu kết quả vào:\n{p}")
-        except Exception as e:
-            messagebox.showerror("Lỗi", f"Không lưu được file:\n{e}")
+    from datetime import datetime
+    import zipfile
+    p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")], title="Lưu kết quả ra file")
+    if p:
+        try:
+            content = output_text.get("1.0", tk.END).rstrip()
+            # save text file
+            with open(p, "w", encoding="utf-8") as f:
+                f.write(content)
+            # also create a zip adjacent to the chosen file with timestamp
+            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
+            zip_path = os.path.splitext(p)[0] + f"_{timestamp}.zip"
+            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
+                # store the text output inside the zip using the basename
+                z.write(p, arcname=os.path.basename(p))
+            # copy zip path to clipboard for convenience
+            try:
+                root.clipboard_clear()
+                root.clipboard_append(zip_path)
+            except Exception:
+                pass
+            messagebox.showinfo("Đã lưu", f"Đã lưu kết quả vào:\n{p}\n\nZIP: {zip_path}\n(đường dẫn ZIP đã được copy vào clipboard)")
+        except Exception as e:
+            messagebox.showerror("Lỗi", f"Không lưu được file:\n{e}")
*** End Patch
