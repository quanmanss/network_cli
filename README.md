# network_cli
Basic CLI app to ping or send message by 5G
Chương trình mô phỏng gửi tin nhắn, giả video bằng dữ liệu.
Đầu tiên cần khởi động 5G core, gNodeB và UE.
Sau đó chạy chương trình bằng lệnh python3 network_cli.py trong thư mục chứa.
Màn hình sẽ hiện ra menu các lựa chọn.
Ví dụ cần gửi tin nhắn bằng TCP, ta cần khởi tạo TCP server (nhấn phím 1), nhập IP ( mặc định không nhập là 0.0.0.0 là nghe từ mọi nguồn) và cổng (thường chọn số lớn ví dụ 12345). Mở Terminal khác và chạy Client để nhập gửi tin nhắn.
Tương tự với gửi video cần chạy UDP server. Chương trình chỉ mô phỏng gửi hàng loạt các văn bản ngẫu nhiên với các tham số thời gian, dung lượng,..
Một vài chức năng như nhấn phím 4 còn đang sửa đổi chưa dùng được hoặc không cần thiết.
