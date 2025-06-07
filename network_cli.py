import socket
import subprocess
import time
import struct
import os
from urllib.parse import urlparse

# --- Chức năng Ping ---
def ping_host():
    ip = input("Nhập địa chỉ IP để ping: ").strip()
    if not ip:
        print("❌ Bạn chưa nhập địa chỉ IP.")
        return

    command = f"sudo ip netns exec ue1 ping -i 0.1 {ip}"
    print(f"==> Đang chạy: {command}")
    try:
        # Chạy lệnh và in output theo thời gian thực
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1 # Đảm bảo output được in ra ngay lập tức
        )
        for line in process.stdout:
            print(line, end='')
        
        process.wait() # Đợi quá trình kết thúc
        
        if process.returncode == 0:
            print("\n✅ Lệnh ping đã hoàn thành thành công.")
        else:
            print(f"\n❌ Lệnh ping thất bại với mã lỗi: {process.returncode}")
            print("Lưu ý: Đảm bảo 'ue1' network namespace đang hoạt động và có kết nối.")
            
    except FileNotFoundError:
        print("❌ Lỗi: Lệnh 'ip' hoặc 'ping' không tìm thấy. Đảm bảo chúng có trong PATH.")
    except KeyboardInterrupt:
        print("\n[!] Bạn đã dừng quá trình.")
        if 'process' in locals() and process.poll() is None: # Kiểm tra tiến trình còn chạy không
            process.terminate() 
            process.wait()
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi không mong muốn: {e}")


# --- Chức năng TCP ---
def tcp_client(host, port, message, num_messages=1):
    print(f"\n[TCP Client] Đang gửi tới {host}:{port}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            if message:
                encoded_message = message.encode('utf-8')
                s.sendall(encoded_message)
                print(f"Đã gửi {len(encoded_message)} bytes: '{message}'")
                # Nhận phản hồi từ server
                s.settimeout(5)
                try:
                    data = s.recv(4096)
                    decoded_response = data.decode('utf-8', errors='replace').strip()
                    print(f"Nhận phản hồi từ server: '{decoded_response}'")
                except socket.timeout:
                    print("Không nhận được phản hồi từ server trong thời gian quy định.")
                except Exception as e:
                    print(f"Lỗi khi nhận phản hồi TCP: {e}")
    except Exception as e:
        print(f"[TCP Client] Đã xảy ra lỗi: {e}")
    finally:
        print("[TCP Client] Đã dừng.")

def tcp_server(host, port):
    print(f"\n[TCP Server] Đang lắng nghe trên {host}:{port}...")
    try:
        # Tạo socket TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Cho phép tái sử dụng địa chỉ để tránh lỗi "Address already in use" khi khởi động lại server nhanh
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind((host, port))
        s.listen(5) # Bắt đầu lắng nghe, với tối đa 5 kết nối đang chờ trong hàng đợi

        print("Chờ kết nối...")
        while True: # Vòng lặp chính để server liên tục chấp nhận các kết nối mới
            conn, addr = s.accept() # Chặn và chờ một kết nối mới
            with conn: # Sử dụng 'with' để đảm bảo kết nối được đóng đúng cách
                print(f"Kết nối mới từ {addr}")
                while True: # Vòng lặp này để nhận nhiều tin nhắn trên CÙNG một kết nối
                    data = conn.recv(4096) # Nhận dữ liệu (đặt kích thước buffer lớn hơn một chút)
                    if not data: # Nếu không còn dữ liệu (client đã đóng kết nối hoặc gửi rỗng)
                        print(f"Client {addr} đã đóng kết nối.")
                        break # Thoát vòng lặp nhận dữ liệu cho kết nối hiện tại
                    
                    decoded_data = data.decode('utf-8', errors='ignore').strip() # Giải mã và loại bỏ khoảng trắng thừa
                    print(f"Nhận từ {addr}: {decoded_data}")
                    
                    # Gửi phản hồi lại cho client (ví dụ: xác nhận đã nhận)
                    response_message = f"Server received: '{decoded_data}'".encode('utf-8')
                    conn.sendall(response_message)
            # Khi khối 'with conn' kết thúc, kết nối 'conn' sẽ tự động đóng.
            # Server sau đó quay trở lại vòng lặp 'while True' bên ngoài để chấp nhận kết nối mới.

    except KeyboardInterrupt:
        print("\n[TCP Server] Server bị ngắt bởi người dùng (Ctrl+C).")
    except Exception as e:
        print(f"[TCP Server] Đã xảy ra lỗi: {e}")
    finally:
        if 's' in locals() and s:
            s.close() # Đảm bảo socket server được đóng khi thoát
        print("[TCP Server] Đã dừng.")
# --- Chức năng UDP ---
def udp_client(host, port, message, num_messages=1):
    """
    Client UDP: Gửi tin nhắn tới server UDP.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            print(f"Đang gửi tin nhắn UDP tới {host}:{port}...")
            for i in range(num_messages):
                full_message = f"[{i+1}/{num_messages}] {message}".encode('utf-8')
                s.sendto(full_message, (host, port))
                print(f"Đã gửi: '{full_message.decode('utf-8')}'")
                # UDP không có kết nối, không có phản hồi mặc định trừ khi server gửi lại
                time.sleep(0.1)
            print("Hoàn tất gửi tin nhắn UDP.")
    except socket.gaierror:
        print(f"Lỗi: Không thể phân giải địa chỉ host '{host}'.")
    except Exception as e:
        print(f"Đã xảy ra lỗi UDP client: {e}")

def udp_server(host, port):
    print(f"\n[UDP Server] Đang lắng nghe trên {host}:{port}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        print("Chờ dữ liệu...")

        start_time = None
        last_packet_time = None
        total_bytes_received = 0
        packet_count = 0
        
        print("\n--- Đang chờ gói tin để bắt đầu đo lường ---")

        while True:
            data, addr = s.recvfrom(4096)
            
            if start_time is None:
                start_time = time.time() # Ghi lại thời gian nhận gói đầu tiên
                print(f"\n--- Bắt đầu đo lường từ {addr} ---")

            last_packet_time = time.time() # Ghi lại thời gian nhận gói hiện tại
            total_bytes_received += len(data)
            packet_count += 1
            
            # (Phần giải mã và in ra nội dung đã có trong bản sửa lỗi trước, giữ nguyên)
            # print(f"Nhận được {len(data)} bytes từ {addr}.")
            # decoded_content = "[Dữ liệu không phải văn bản hoặc mã hóa không tương thích]"
            # is_text_data = False
            # try:
            #     temp_decoded = data.decode('utf-8', errors='replace').strip()
            #     if temp_decoded.count('\ufffd') * 2 > len(temp_decoded):
            #         pass # Đây là dữ liệu nhị phân
            #     else:
            #         decoded_content = temp_decoded
            #         is_text_data = True
            #         print(f"  --> Giải mã UTF-8 thành: '{decoded_content}'")
            # except Exception:
            #     pass # Lỗi giải mã, coi là nhị phân

            # if is_text_data:
            #     response_message = f"Server received text: '{decoded_content}'".encode('utf-8')
            # else:
            #     response_message = f"Server received {len(data)} bytes (binary)".encode('utf-8')
            # s.sendto(response_message, addr)
            
            # In thông báo trạng thái nhỏ gọn để không làm ngập console
            # if packet_count % 100 == 0:
            #     print(f"Đã nhận {packet_count} gói, {total_bytes_received / (1024 * 1024):.2f} MB")

    except KeyboardInterrupt:
        print("\n[UDP Server] Server bị ngắt bởi người dùng (Ctrl+C).")
        # Tính toán và in kết quả khi dừng server
        if start_time is not None and last_packet_time is not None and total_bytes_received > 0:
            actual_duration = last_packet_time - start_time
            if actual_duration > 0:
                throughput_mbps = (total_bytes_received * 8) / (actual_duration * 1024 * 1024)
                throughput_mb_per_s = total_bytes_received / (actual_duration * 1024 * 1024)
                print(f"\n--- Báo cáo hiệu suất UDP Server ---")
                print(f"Tổng dữ liệu đã nhận: {total_bytes_received / (1024 * 1024):.2f} MB")
                print(f"Tổng số gói nhận: {packet_count}")
                print(f"Thời gian nhận thực tế: {actual_duration:.2f} giây")
                print(f"**Tốc độ truyền (Nhận): {throughput_mbps:.2f} Mbps ({throughput_mb_per_s:.2f} MB/s)**")
            else:
                print("Thời gian nhận quá ngắn để tính tốc độ truyền.")
        else:
            print("Không có dữ liệu nào được nhận để tính toán.")

    except Exception as e:
        print(f"[UDP Server] Đã xảy ra lỗi tổng quát: {e}")
    finally:
        if 's' in locals() and s:
            s.close()
        print("[UDP Server] Đã dừng.")

def send_video_udp(host, port, duration=10, packet_size=1400, interval=0.01):
    """
    Gửi dữ liệu video mô phỏng qua UDP.
    Gửi các gói dữ liệu ngẫu nhiên để mô phỏng luồng video.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            print(f"Đang gửi dữ liệu video mô phỏng qua UDP tới {host}:{port} trong {duration} giây...")
            start_time = time.time()
            packet_count = 0
            while time.time() - start_time < duration:
                # Tạo dữ liệu ngẫu nhiên mô phỏng một khung hình video
                dummy_video_data = os.urandom(packet_size)
                s.sendto(dummy_video_data, (host, port))
                packet_count += 1
                time.sleep(interval) # Điều chỉnh để kiểm soát tốc độ gửi
            print(f"Hoàn tất gửi {packet_count} gói video mô phỏng qua UDP.")
    except socket.gaierror:
        print(f"Lỗi: Không thể phân giải địa chỉ host '{host}'.")
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gửi video qua UDP: {e}")

import sys
# ...existing code...

def iperf3():
    mode = input("Chọn chế độ (s: server, c: client): ").strip().lower()
    if mode == 's':
        command = "iperf3 -s"
        print("==> Đang chạy iperf3 ở chế độ server...")
    elif mode == 'c':
        ip = input("Nhập IP server: ").strip()
        command = f"sudo ip netns exec ue1 iperf3 -c {ip} -t 10"
        print(f"==> Đang chạy iperf3 ở chế độ client tới {ip}...")
    else:
        print("Chỉ nhập 's' (server) hoặc 'c' (client).")
        return

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in process.stdout:
            print(line, end='')
        process.wait()
    except FileNotFoundError:
        print("❌ Lệnh 'iperf3' không tìm thấy. Hãy cài đặt iperf3.")
    except KeyboardInterrupt:
        print("\n[!] Đã dừng iperf3.")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            process.wait()
    except Exception as e:
        print(f"❌ Lỗi khi chạy iperf3: {e}")



def main_interactive():
    while True:
        print("\n--- Menu (Network CLI) ---")
        print("1. Chạy TCP Server (trên Host)")
        print("2. Chạy TCP Client (từ UE)")
        print("3. Chạy UDP Server (trên Host)")
        print("4. Chạy UDP Client (từ UE)")
        print("5. Chạy Video Client (từ UE)")
        print("6. Ping ")
        print("7. Đo Data Rate bằng iperf3")
        print("0. Thoát")
        print("-------------------------------")

        choice = input("Vui lòng chọn chức năng (nhập số): ").strip()

        if choice == '1':
            print("\n--- Cấu hình TCP Server ---")
            host = input("Nhập IP để lắng nghe (mặc định: 0.0.0.0): ") or "0.0.0.0"
            port = int(input("Nhập cổng để lắng nghe (ví dụ: 12345): "))
            tcp_server(host, port)
        
        elif choice == '2':
            print("\n--- Cấu hình TCP Client ---")
            host = input("Nhập IP của server (ví dụ: IP của wlo1): ")
            port = int(input("Nhập cổng của server (ví dụ: 12345): "))
            message = input("Nhập tin nhắn để gửi: ")
            tcp_client(host,port,message)
        elif choice == '3':
            print("\n--- Cấu hình UDP Server ---")
            host = input("Nhập IP để lắng nghe (ví dụ: 0.0.0.0): ") or "0.0.0.0"
            port = int(input("Nhập cổng để lắng nghe (ví dụ: 54321): "))
            udp_server(host,port)
           

        # elif choice == '4':
        #     print("\n--- Cấu hình UDP Client ---")
        #     host = input("Nhập IP của server: ")
        #     port = int(input("Nhập cổng của server: "))
        #     message = input("Nhập tin nhắn để gửi: ")
        #     udp_server(host,port)
        elif choice == '5':
            host = input("Nhập IP của server: ")
            port = int(input("Nhập cổng: ")) 
            send_video_udp(host, port, duration=10, packet_size=1400, interval=0.01)
        elif choice == '6':
            ping_host()
        elif choice == '7':
            iperf3()
        elif choice == '0':
            print("Đang thoát chương trình. Tạm biệt!")
            sys.exit(0)
        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại.")

        input("\nNhấn Enter để tiếp tục...") # Đợi người dùng nhấn Enter trước khi hiển thị menu lại
if __name__ == "__main__":
    main_interactive()
