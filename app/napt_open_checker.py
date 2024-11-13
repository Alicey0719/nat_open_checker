import socket
import subprocess
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

# 環境変数からホストを取得
host = os.getenv("HOST")

# チェックするポートとプロトコルのリスト（ポート番号: プロトコル）
ports_to_check = {
    22: "SSH",
    53: "DNS (UDP)",
    80: "HTTP",
    123: "NTP (UDP)",
    514: "Syslog (UDP)",
    23: "Telnet",
    21: "FTP",
    69: "TFTP (UDP)", 
    25: "SMTP",
    110: "POP3",
    3306: "MySQL",
    1433: "MSSQL",
    5432: "PostgreSQL",
    3389: "RDP",
}

def check_tcp_port(host, port):
    """指定されたTCPポートが開いているかチェックします"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        return result == 0

def check_udp_port(host, port):
    """指定されたUDPポートが開いているかチェックします"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1)
        try:
            sock.sendto(b"", (host, port))
            sock.recvfrom(1024)
            return True
        except socket.error:
            return False

def check_icmp(host):
    """ICMP（Ping）が開いているかチェックします"""
    try:
        result = subprocess.run(["ping", "-c", "1", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def main():
    if not host:
        print("エラー: ホストが設定されていません。'.env'ファイルでHOST変数を設定してください。")
        return

    open_ports = []

    print("ポートスキャンを開始します...")
    for port, protocol in ports_to_check.items():
        if "UDP" in protocol:
            if check_udp_port(host, port):
                open_ports.append(f"{protocol} ポート {port}")
        else:
            if check_tcp_port(host, port):
                open_ports.append(f"{protocol} ポート {port}")

    # ICMP (Ping) チェック
    if check_icmp(host):
        open_ports.append("ICMP応答あり")

    # 結果を一度に出力
    if open_ports:
        print("以下のポートが開いています:\n" + "\n".join(open_ports))
    else:
        print("すべての指定ポートは閉じています。")

if __name__ == "__main__":
    main()
