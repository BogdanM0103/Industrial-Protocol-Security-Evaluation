import unittest
import struct
from protocol import Message, FunctionCode, encode_message, decode_message, SIZE, FORMAT

class TestProtocol(unittest.TestCase):
    def test_round_trip(self):
        # test that encoding and decoding preserves the original message
        # testing for boundary values of the fields
        test_cases = [
            Message(transaction_id=0, function_code=FunctionCode.READ, register=0, value=0),
            Message(transaction_id=0, function_code=FunctionCode.WRITE, register=0, value=0),
            Message(transaction_id=12345, function_code=FunctionCode.READ, register=12345, value=12345),
            Message(transaction_id=12345, function_code=FunctionCode.WRITE, register=12345, value=12345),
            Message(transaction_id=65535, function_code=FunctionCode.READ, register=65535, value=65535),
            Message(transaction_id=65535, function_code=FunctionCode.WRITE, register=65535, value=65535),
        ]
        for original_message in test_cases:
            encoded = encode_message(original_message)
            decoded_message = decode_message(encoded)
            self.assertEqual(original_message, decoded_message)

    def test_out_of_range_values(self):
        # test that out-of-range values raise an error
        with self.assertRaises(struct.error):
            encode_message(Message(transaction_id=-1, function_code=FunctionCode.READ, register=-1, value=-1))  # transaction_id out of range
        with self.assertRaises(struct.error):
            encode_message(Message(transaction_id=70000, function_code=FunctionCode.READ, register=70000, value=70000))  # transaction_id out of range
        with self.assertRaises(struct.error):
            encode_message(Message(transaction_id=0, function_code=FunctionCode.READ, register=-1, value=-1))  # register out of range
        with self.assertRaises(struct.error):
            encode_message(Message(transaction_id=0, function_code=FunctionCode.READ, register=70000, value=70000))  # register out of range
        with self.assertRaises(struct.error):
            encode_message(Message(transaction_id=0, function_code=FunctionCode.READ, register=0, value=-1))  # value out of range
        with self.assertRaises(struct.error):
            encode_message(Message(transaction_id=0, function_code=FunctionCode.READ, register=0, value=70000))  # value out of range

    def test_decoded_code_is_functioncode(self):
        # test that an invalid function code raises an error
        message = Message(transaction_id=1, function_code=FunctionCode.READ, register=1, value=1)
        encode = encode_message(message)
        decode = decode_message(encode)
        self.assertIsInstance(decode.function_code, FunctionCode)

    def test_field_independence(self):
        # test that changing one field does not affect others
        original_message = Message(transaction_id=1, function_code=FunctionCode.READ, register=10, value=100)
        encoded = encode_message(original_message)
        decoded_message = decode_message(encoded)
        self.assertEqual(decoded_message.transaction_id, 1)
        self.assertEqual(decoded_message.function_code, FunctionCode.READ)
        self.assertEqual(decoded_message.register, 10)
        self.assertEqual(decoded_message.value, 100)

    def test_decode_wrong_length_bytes(self):
        # decode must reject byte strings that aren't exactly SIZE long.
        # struct.unpack demands exactly SIZE bytes, so both a too-short and a
        # too-long buffer raise struct.error. Using SIZE (not a literal 7) keeps
        # this correct even if the wire format changes later.
        with self.assertRaises(struct.error):
            decode_message(b"\x00" * (SIZE - 1))  # one byte too short
        with self.assertRaises(struct.error):
            decode_message(b"\x00" * (SIZE + 1))  # one byte too long

    def test_decode_unknown_function_code(self):
        # a buffer of the RIGHT length but with an undefined code byte must be rejected.
        # we build valid-length bytes with pack, passing 3 where the code goes:
        # pack only checks 3 fits in a 'B', so the bytes look well-formed...
        # ...but decode_message does FunctionCode(3), which raises ValueError.
        corrupt = struct.pack(FORMAT, 1, 3, 0, 0)  # 3 is not a defined FunctionCode
        with self.assertRaises(ValueError):
            decode_message(corrupt)

if __name__ == "__main__":
    unittest.main()