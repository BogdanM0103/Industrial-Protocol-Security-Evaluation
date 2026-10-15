import socket
from protocol import Message, FunctionCode, HOST, PORT, SIZE, recv_exactly, decode_message, encode_message

class PLCServer:
    def __init__(self, register_count: int = 10):
        self.registers = {i: 0 for i in range(register_count)}
    def handle(self, msg: Message) -> Message:
        match msg.function_code:
            case FunctionCode.READ:
                return Message(msg.transaction_id, FunctionCode.READ, msg.register, self.registers[msg.register])
            case FunctionCode.WRITE:
                self.registers[msg.register] = msg.value
                return Message(msg.transaction_id, FunctionCode.WRITE, msg.register, msg.value)
            case _:
                raise ValueError(f"Unknown function code {msg.function_code}")

def serve():
    plc = PLCServer()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"PLC listening on {HOST}:{PORT}")

    try:
        while True:                       # serve one client, then loop back for the next
            conn, addr = server.accept()
            print(f"HMI connected from {addr}")
            with conn:                    # auto-closes this client's socket when done
                while True:               # per-message loop for this client
                    raw = recv_exactly(conn, SIZE)
                    if len(raw) < SIZE:   # clean disconnect or truncated frame -> stop
                        print("HMI disconnected")
                        break
                    msg = decode_message(raw)
                    reply = plc.handle(msg)
                    conn.sendall(encode_message(reply))
    except KeyboardInterrupt:
        print("\nPLC shutting down")
    finally:
        server.close()