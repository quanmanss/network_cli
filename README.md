# network_cli

Ứng dụng CLI cơ bản cho việc ping hoặc gửi tin nhắn qua mạng 5G.
Mô tả

network_cli là chương trình mô phỏng gửi tin nhắn hoặc giả lập truyền video bằng dữ liệu qua mạng 5G. Ứng dụng này giúp kiểm thử và trình diễn các tính năng mạng lõi (core), trạm gNodeB và thiết bị UE trong môi trường 5G.
Tính năng

    Gửi tin nhắn qua TCP.
    Mô phỏng gửi video (gửi hàng loạt văn bản ngẫu nhiên) qua UDP.
    Giao diện menu thân thiện, dễ sử dụng.
    Một số chức năng đang phát triển (ví dụ: phím 4).

Yêu cầu hệ thống

    Python 3.x
    Các thành phần mạng 5G core, gNodeB và UE đã được khởi động.

Cài đặt

    Clone repository:
    bash

git clone https://github.com/quanmanss/network_cli.git
    cd network_cli

(Nếu cần) Cài đặt các thư viện phụ thuộc:
bash

    pip install -r requirements.txt

Sử dụng

    Đảm bảo đã khởi động 5G core, gNodeB và UE.
    Chạy chương trình trong thư mục chứa file:
    bash

    python3 network_cli.py

    Màn hình sẽ hiện menu các lựa chọn:
        Gửi tin nhắn qua TCP: Nhấn phím 1, nhập IP (mặc định là 0.0.0.0) và cổng.
        Gửi video qua UDP: Nhấn phím tương ứng, nhập các tham số thời gian, dung lượng,...
        Một số chức năng như phím 4 đang phát triển.

Đóng góp

Mọi đóng góp đều được hoan nghênh!

    Fork repository, tạo nhánh mới và PR.
    Vui lòng mô tả rõ ràng các thay đổi khi gửi pull request.


