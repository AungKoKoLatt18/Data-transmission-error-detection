"""Client 1 - Data Sender"""
import socket
from methods import METHODS, compute

SERVER = ("127.0.0.1", 5000)

text = input("Enter text to send: ")
if not text or "|" in text or not text.isascii():
    raise SystemExit("Text must be non-empty ASCII and must not contain '|'.")

print("\nControl information methods:")
for i, m in enumerate(METHODS, 1):
    print(f"  {i}. {m}")
choice = int(input("Select method (1-5): "))
method = METHODS[choice - 1]

control = compute(method, text)
packet = f"{text}|{method}|{control}"
print(f"\nPacket to send: {packet}")

with socket.socket() as s:
    s.connect(SERVER)
    s.sendall(packet.encode("ascii"))
print("Packet sent to server.")
