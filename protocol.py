# field                     modbus tcp equivalent
# transaction_id(2 bytes) - Matches a response to a request
# function code(1 byte) - Simplified 0=READ 1=WRITE from 1=Read Coils, 3=Read Holding Registers, 6=Write Single Register, etc.
# register              - Register/Address reference
# value                 - Value stored at the register address

# struct.pack(FORMAT, *values): Takes your Python integers and lays them out as a compact binary buffer according to FORMAT.
# The format letters:
# - ! — big-endian (network byte order): most-significant byte first. That's why 256 would be 01 00, not 00 01.
# - H — unsigned 16-bit int → 2 bytes, range 0…65535.
# - B — unsigned 8-bit int → 1 byte, range 0…255.

# example:
# pack("!HBHH", 1, 1, 10, 100)
# 1 -> H -> 2 bytes -> 00 01
# 1 -> B -> 1 byte -> 01
# 10 -> H -> 2 bytes -> 00 0a
# 100 -> H -> 2 bytes -> 00 64
# result: b'\x00\x01\x01\x00\x0a\x00\x64' — exactly 7 bytes (= SIZE).

# struct.unpack(FORMAT, *values): Takes your Python byte buffer and using the same FORMAT, slices it back into python values. It returns a tuple.
# If the unpack doesnt have the same FORMAT as pack, the slicing will be done incorrect and the information will come out different.
# https://docs.python.org/3/library/struct.html#struct-alignment

import enum
import struct
from dataclasses import dataclass

class FunctionCode(enum.IntEnum):
    READ = 1
    WRITE = 2

@dataclass
class Message:
    transaction_id: int
    function_code: FunctionCode
    register: int
    value: int

# transaction_id: 2 bytes, function_code: 1 byte, register: 2 bytes, value: 2 bytes
FORMAT = "!HBHH"
SIZE = struct.calcsize(FORMAT)

def encode_message(message: Message) -> bytes:
    return struct.pack(FORMAT, message.transaction_id, message.function_code, message.register, message.value)

def decode_message(data: bytes) -> Message:
    transaction_id, function_code, register, value = struct.unpack(FORMAT, data)
    return Message(transaction_id, FunctionCode(function_code), register, value)

if __name__ == "__main__":
    # Example usage
    msg = Message(transaction_id=1, function_code=FunctionCode.READ, register=10, value=100)
    encoded = encode_message(msg)
    print(f"Encoded: {encoded}")

    decoded = decode_message(encoded)
    print(f"Decoded: {decoded}")