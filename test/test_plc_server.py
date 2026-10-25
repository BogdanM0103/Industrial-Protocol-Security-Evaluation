import unittest
from plc_server import PLCServer
from protocol import Message, FunctionCode


class TestPLCServer(unittest.TestCase):
    def setUp(self):
        # handle() mutates register state, so each test gets a fresh server.
        # This runs before every test_* method -> no state leaks between tests.
        self.plc = PLCServer()

    def test_read_fresh_register_is_zero(self):
        # a register that was never written reads back as its initial 0
        read = Message(transaction_id=1, function_code=FunctionCode.READ, register=3, value=0)
        reply = self.plc.handle(read)
        self.assertEqual(reply.value, 0)
        self.assertEqual(reply.register, 3)
        self.assertEqual(reply.transaction_id, 1)
        self.assertEqual(reply.function_code, FunctionCode.READ)

    def test_write_acks_with_echo_and_stores_value(self):
        # WRITE must both (a) echo an ack back and (b) actually store the value.
        # Checking only the ack could miss a broken state write, so we assert both.
        write = Message(transaction_id=7, function_code=FunctionCode.WRITE, register=1, value=100)
        reply = self.plc.handle(write)
        # (a) the ack echoes the request
        self.assertEqual(reply.transaction_id, 7)
        self.assertEqual(reply.function_code, FunctionCode.WRITE)
        self.assertEqual(reply.register, 1)
        self.assertEqual(reply.value, 100)
        # (b) the value really landed in register state
        self.assertEqual(self.plc.registers[1], 100)

    def test_write_then_read_returns_stored_value(self):
        # the key state-persistence test: a value written in one call survives
        # to the next call and reads back unchanged.
        write = Message(transaction_id=1, function_code=FunctionCode.WRITE, register=1, value=100)
        read = Message(transaction_id=2, function_code=FunctionCode.READ, register=1, value=0)
        self.plc.handle(write)
        reply = self.plc.handle(read)
        self.assertEqual(reply.value, 100)

    def test_registers_are_independent(self):
        # writing one register must not disturb another
        write = Message(transaction_id=1, function_code=FunctionCode.WRITE, register=1, value=100)
        read = Message(transaction_id=2, function_code=FunctionCode.READ, register=2, value=0)
        self.plc.handle(write)
        reply = self.plc.handle(read)
        self.assertEqual(reply.value, 0)

    def test_unknown_function_code_raises(self):
        # FunctionCode only defines READ=0 / WRITE=1. A raw int in the code slot
        # (the annotation isn't enforced at runtime) falls through handle()'s
        # match to `case _` -> ValueError.
        bogus = Message(transaction_id=1, function_code=2, register=0, value=0)
        with self.assertRaises(ValueError):
            self.plc.handle(bogus)

    def test_read_out_of_range_raises(self):
        # default server has registers 0..9; READing reg 10 indexes a missing
        # dict key -> KeyError. Documents the lack of bounds validation on READ.
        read = Message(transaction_id=1, function_code=FunctionCode.READ, register=10, value=0)
        with self.assertRaises(KeyError):
            self.plc.handle(read)

    def test_write_out_of_range_creates_register(self):
        # ASYMMETRY (unsecured-protocol story): unlike READ, WRITE to a register
        # outside 0..9 does NOT raise -- assigning to a missing dict key creates
        # it. So WRITE silently invents registers; there is no bounds checking.
        write = Message(transaction_id=1, function_code=FunctionCode.WRITE, register=99, value=42)
        self.plc.handle(write)
        self.assertEqual(self.plc.registers[99], 42)

    def test_register_count_parameter(self):
        # the constructor param sizes the register bank
        small = PLCServer(register_count=4)
        self.assertEqual(len(small.registers), 4)
        self.assertIn(3, small.registers)
        self.assertNotIn(4, small.registers)


if __name__ == "__main__":
    unittest.main()
