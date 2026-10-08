What are these machines?

HMI - Human Machine Interface, aka. the operator's console. When the operator clicks "set pump to 50%", the HMI sends a command over the network telling the PLC to write 50 to the pump speed register.

PLC - Programmable Logic Controller. Computer wired to motors, valves, sensors. Holds state in registers.

Simulation: HMI -> sends commands -> PLC -> changes registers

A protocol is just an agreed format for messages so both sides understand each other. Like agreeing that an envelope always has "recipient, then sender, then message" in that order. Your protocol.py defines that envelope: "a message is always transaction_id, then function_code, then register, then value." Both HMI and PLC follow the same rule, so they can read each other.


The foundational model of all cybersecurity — the CIA triad:

1. Confidentiality — can an outsider read the message? (secrecy)
2. Integrity — can an outsider change the message without being caught? (tampering)
3. Availability — is the system up and responsive when needed?

Plus two more that matter here:
- Authentication — is the sender really who they claim to be?
- Freshness / anti-replay — is this a new message, or an old one someone recorded and is re-sending?

unsecured protocol fails: integrity, authentication, freshness
secured version fixes integrity, authentication, freshness

Attacker's position: from HMI to PLC the attacker places a device, the message passes through it
"mitm_attack.py" simulates being in that spot, acting as a proxy the HMI unknowlingly talks to.

Mitm attack: the HMI talks to the proxy instead, and the proxy modifies the value of the pump on its way to the PLC

Replay attack: attacker doesnt need to understand or change the message, it just needs to record a valid one and send it again later.

In project: capture the bytes of one legitimate "open valve" command. An hour later you re-send those exact bytes. The PLC sees a perfectly valid message and opens the valve again — because the protocol has no sense of time or novelty. Every message looks fresh. (Real-world analogy: recording the radio code that opens a garage door, then replaying it.)

Two defenses, each killing one weakness:

1. HMAC — defeats tampering & forgery (MITM).
   HMAC = a keyed fingerprint of the message. The HMI and PLC share a secret key. The HMI computes HMAC(key, message) and attaches it. The PLC recomputes it on arrival and checks they match.
   - Attacker changes the message? The fingerprint no longer matches → PLC rejects it.
   - Attacker tries to forge a new fingerprint? They can't — they don't have the key.
   - This gives you integrity + authentication at once. (It's a hash with a secret, which is why your spec says "hashing or encryption.")
2. Nonce or timestamp — defeats replay.
   Add a "freshness token" to each message:
   - Nonce = a number used once. PLC remembers nonces it has seen; a repeat → reject.
   - Timestamp = the time the message was made. PLC rejects anything too old.
   - Replayed message carries an old nonce/timestamp → PLC rejects it.
   - Crucial detail: the freshness token must be inside what the HMAC covers, so the attacker can't just swap in a fresh-looking timestamp — that would break the fingerprint.

So the secured message = [the command] + [freshness token] + [HMAC over all of it]. MITM edits → HMAC fails. Replay → freshness fails. Both attacks now bounce off.