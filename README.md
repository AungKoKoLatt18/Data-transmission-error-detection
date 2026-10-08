# Error Detection with Sockets

This project sends a message across a network and checks whether it was damaged on the way.

It uses **3 programs**:

1. **Client 1** sends a message with a "check code" attached.
2. **Server** damages the message on purpose (like a noisy cable would).
3. **Client 2** receives the message and checks if it was damaged.

```
Client 1  ──▶  Server  ──▶  Client 2
(sender)     (damages)     (checks)
```

## How to Run

You need **Python 3**. Open **3 terminals** in this folder and run them **in this order**:

```
python client2.py     # 1st: the receiver
python server.py      # 2nd: the damager (choose an error type)
python client1.py     # 3rd: the sender (type a message, choose a method)
```

On Mac/Linux, use `python3` instead of `python`.

## What Happens (Example)

1. In `client1.py`, type `HELLO` and choose method `3` (CRC16).
2. Client 1 sends this packet: `HELLO|CRC16|49D6`
   - `HELLO` = the message
   - `CRC16` = the method used
   - `49D6` = the check code
3. The server damages the message, for example `HELLO` becomes `HEZLO`.
4. Client 2 calculates a new check code from the damaged message and compares it with `49D6`.
5. The two codes are different, so Client 2 prints:

```
Received Data       : HEZLO
Method              : CRC16
Sent Check Bits     : 49D6
Computed Check Bits : 92B1
Status              : DATA CORRUPTED
```

If the codes match, it prints `DATA CORRECT`.

## The 5 Check Methods

| Choice | Method | How it works (simple) |
|---|---|---|
| 1 | Parity | Adds 1 bit so the number of 1s in the data is even |
| 2 | 2D Parity | Same idea, but for every row and every column of bits |
| 3 | CRC16 | Math (division) on the data that gives a 4-character code |
| 4 | Hamming | Extra bits that can **find and fix** a single wrong bit |
| 5 | Checksum | Adds the data together in 16-bit pieces and flips the result |

Check codes for `HELLO`:

| Method | Code |
|---|---|
| Parity | `0` |
| 2D Parity | `01111:01000010` |
| CRC16 | `49D6` |
| Hamming | `101110101010101011101011101111` |
| Checksum | `1C6E` |

## The 7 Error Types (Server)

When you start `server.py`, choose a number:

| Choice | Error | Example |
|---|---|---|
| 1 | Flip one bit | `HELLO` → `HEMLO` |
| 2 | Replace a character | `HELLO` → `HEZLO` |
| 3 | Delete a character | `HELLO` → `HELO` |
| 4 | Insert a character | `HELLO` → `HEaLLO` |
| 5 | Swap two neighbors | `HELLO` → `HLELO` |
| 6 | Flip several bits | `HELLO` → `@EHLO` |
| 7 | Burst: ruin 3 to 8 characters in a row | `HELLO` → `H#9!x` |
| 0 | Pick a random error every time | |
| 8 | No error (message stays the same) | |

## Try These Tests

Always send `HELLO`.

| Server choice | Method | What you should see |
|---|---|---|
| 8 (no error) | any | `DATA CORRECT` |
| 1 (flip bit) | CRC16 | `DATA CORRUPTED` |
| 1 (flip bit) | Hamming | `DATA CORRUPTED`, then `Corrected Data : HELLO` |
| 5 (swap) | Parity | `DATA CORRECT` (the error was missed, because swapping does not change the number of 1s) |
| 7 (burst) | CRC16 | `DATA CORRUPTED` |

## Which Method Is Best?

- **Parity**: simple, but misses many errors.
- **2D Parity**: better than parity, but can still miss some.
- **CRC16**: very reliable at detecting errors.
- **Hamming**: the only one that can also **fix** an error (one wrong bit per block).
- **Checksum**: simple, but weaker than CRC.

## Files

| File | What it does |
|---|---|
| `client1.py` | Sender |
| `server.py` | Damages the message |
| `client2.py` | Receiver and checker |
| `methods.py` | All 5 check methods (used by both clients) |

## Rules and Problems

- The message must be **English letters, numbers and symbols (ASCII)**, and must **not** contain `|`.
- **"Python was not found"**: install Python from python.org and tick **Add python.exe to PATH**.
- **"Address already in use"**: close old windows of the server or Client 2 and try again.
- **"Client 2 is not running!"**: start `client2.py` first.

---
