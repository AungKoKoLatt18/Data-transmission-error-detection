"""Client 2 - Receiver + Error Checker"""
import socket
from methods import compute, hamming_correct, recv_all

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 5001))
srv.listen()
print("Client 2 waiting for packets on port 5001... (Ctrl+C to stop)")

while True:
    conn, _ = srv.accept()
    with conn:
        packet = recv_all(conn)

    data, method, incoming_control = packet.rsplit("|", 2)
    computed = compute(method, data)
    ok = computed == incoming_control

    print("\n" + "-" * 40)
    print(f"Received Data       : {data}")
    print(f"Method              : {method}")
    print(f"Sent Check Bits     : {incoming_control}")
    print(f"Computed Check Bits : {computed}")
    print(f"Status              : {'DATA CORRECT' if ok else 'DATA CORRUPTED'}")
    if method == "HAMMING" and not ok:
        fixed = hamming_correct(data, incoming_control)
        if fixed is None:
            print("Correction          : not possible (length changed)")
        else:
            print(f"Corrected Data      : {fixed}")
    print("-" * 40)
