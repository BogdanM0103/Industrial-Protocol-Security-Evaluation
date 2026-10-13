from protocol import Message, FunctionCode
from socket import socket

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
def recv_exactly(conn: socket, n: int) -> bytearray:
    buffer = bytearray()
    while len(buffer) < n:
        chunk = conn.recv(n - len(buffer))
        if not chunk:
            return buffer
        buffer.extend(chunk)
    return buffer
    

