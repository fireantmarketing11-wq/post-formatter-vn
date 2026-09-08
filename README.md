# Trình Định dạng Bài Post (Tiếng Việt) — README

Mô tả nhanh:
- App desktop nhỏ bằng Python + Tkinter.
- Dán (paste) bài đăng vào ô Input, bấm "Định dạng", kết quả hiện ở ô Output.
- Có nút "Sao chép Output" để copy vào clipboard và "Lưu Output" để lưu file .txt.
- Chế độ: `markdown` (mặc định, dùng ** và *) hoặc `fancy` (cố gắng chuyển chữ latin sang ký tự Unicode kiểu yaytext khi có thể).

Cài đặt & chạy:
1. Yêu cầu: Python 3.8+ (Tkinter phải có sẵn).
2. Tải các file trong thư mục này.
3. Chạy:
   ```bash
   python main.py
   ```

Hướng dẫn dùng (dành cho người không biết code):
1. Mở chương trình bằng lệnh trên.
2. Dán bài post chưa format vào ô bên trái (Input).
3. Chọn "Chế độ" nếu muốn (markdown hoặc fancy).
4. Bấm "Định dạng".
5. Sao chép hoặc lưu file kết quả từ các nút bên trên.

Luật định dạng (heuristic) tóm tắt:
- Từ VIẾT HOA TOÀN BỘ → in đậm + in nghiêng (***từ***)
- Từ bắt đầu bằng chữ hoa → in đậm hoặc in nghiêng tùy độ dài (tự động)
- Từ có số hoặc kết thúc bằng !/? → in đậm
- Các từ khác giữ nguyên

Nếu bạn muốn thay quy tắc (ví dụ: chỉ in đậm chữ bắt đầu hoa, hoặc đổi dấu hiệu) mình sẽ chỉnh nhanh theo yêu cầu.
