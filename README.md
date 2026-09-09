# Trình Định dạng Bài Post (Tiếng Việt) — README

Mô tả nhanh:
- App desktop nhỏ bằng Python + Tkinter.
- Dán (paste) bài đăng vào ô Input, bấm "Định dạng", kết quả hiện ở ô Output.
- Có nút "Sao chép Output" để copy vào clipboard và "Lưu Output" để lưu file .txt.
- Thêm chức năng: Xem trước HTML và Xuất HTML (có style cho hashtag/mention).
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
4. Bấm "Định dạng" để xem kết quả (ô Output).
5. Dùng "Xem trước HTML" để mở bản xem HTML có style màu cho hashtag/mention trong trình duyệt.
6. Dùng "Xuất HTML" để lưu file HTML.
7. Sao chép hoặc lưu file kết quả từ các nút bên trên.

Luật định dạng (heuristic) tóm tắt:
- Từ VIẾT HOA TOÀN BỘ → in đậm + in nghiêng (***từ***)
- Từ bắt đầu bằng chữ hoa → in đậm hoặc in nghiêng tùy độ dài (tự động)
- Từ có số hoặc kết thúc bằng !/? → in đậm
- Hashtag (#tag) và Mention (@user) được tô màu trong chế độ HTML (hashtag: xanh, mention: xanh lá)
- Các từ khác giữ nguyên

Nếu bạn muốn thay quy tắc (ví d��: đổi màu hashtag, hoặc luôn in đậm chữ đầu câu) mình sẽ chỉnh nhanh theo yêu cầu.
