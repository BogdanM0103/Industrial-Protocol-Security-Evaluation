from protocol import Message, FunctionCode, HOST, PORT, SIZE, encode_message, decode_message, recv_exactly
import socket

def send_and_receive(sock: socket.socket, msg: Message) -> Message:
	sock.sendall(encode_message(msg))
	response = recv_exactly(sock, SIZE)
	if len(response) < SIZE:
		raise ConnectionError("PLC closed connection / truncated reply")
	return decode_message(bytes(response))

def main():
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print(f"HMI connected to {HOST}:{PORT}")

    # WRITE register 1 = 100; the PLC echoes the message back as an ack
    write = Message(transaction_id=1, function_code=FunctionCode.WRITE, register=1, value=100)
    ack = send_and_receive(sock, write)
    print(f"WRITE ack: {ack}")

    # READ register 1 back; value=0 on the request is ignored, the reply fills it in
    read = Message(transaction_id=2, function_code=FunctionCode.READ, register=1, value=0)
    reply = send_and_receive(sock, read)
    print(f"READ reg 1 -> {reply.value}")

if __name__ == "__main__": main()
	
    
