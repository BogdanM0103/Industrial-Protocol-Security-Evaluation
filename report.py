# Task 1 — Design the message format (protocol.py, unsecured version).
# Decide on a fixed layout for a request. Start simple, e.g. fields: transaction_id, function_code 
# (1=read, 2=write), register, value. Implement two functions: one that turns those fields into 
# bytes, one that turns bytes back into the fields. Look up Python's struct.pack/struct.unpack 
# — that's the tool for turning integers into a fixed byte layout. Keep it human-readable at 
# first if you like (even JSON over the socket) so you can see that it's plaintext.

