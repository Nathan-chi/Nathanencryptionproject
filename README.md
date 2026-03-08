# 🔐 Secure Encryption Tool
### A Beginner-Friendly Python Encryption Project

---

## What This Project Does

This tool lets you **encrypt and decrypt** text messages and files using industry-standard cryptography. Think of it like a digital lockbox — only someone with the right key can open it.

---

## Project Structure

```
encryption_tool/
│
├── main.py           ← Run this file to start the program
├── key_manager.py    ← Generates and stores encryption keys
├── encryptor.py      ← Encrypts/decrypts text messages
├── file_handler.py   ← Encrypts/decrypts files (PDF, images, etc.)
├── README.md         ← This file
│
└── keys/             ← Created automatically when you run the program
    └── *.key files   ← Your encryption keys are stored here
```

---

## How to Install & Run

### Step 1 — Make sure Python is installed
```bash
python --version
# Should show Python 3.8 or higher
```

### Step 2 — Install the required library
```bash
pip install cryptography
```

### Step 3 — Run the program
```bash
cd encryption_tool
python main.py
```

You'll see a colorful menu like this:
```
══════════════════════════════════════════════════════
   🔐  SECURE ENCRYPTION TOOL  🔐
══════════════════════════════════════════════════════

  MAIN MENU
  ────────────────────────────────────────
  [1]  Generate a new encryption key
  [2]  Encrypt a text message
  [3]  Decrypt a text message
  [4]  Encrypt a file
  [5]  Decrypt a file
  [6]  List saved keys
  [7]  Help & explanations
  [0]  Exit
```

---

## Step-by-Step Usage Guide

### 🔑 First Time: Generate a Key
1. Press `1` and hit Enter
2. Give your key a name (e.g., `mykey`)
3. Your key is saved to `keys/mykey.key`
4. **Back this file up somewhere safe — without it, your data is gone forever**

### ✉️ Encrypt a Message
1. Press `2`
2. Select your key (press `1` if you only have one)
3. Type your secret message
4. Copy the long encrypted output — it's safe to share

### 🔓 Decrypt a Message
1. Press `3`
2. Select the SAME key used to encrypt
3. Paste the encrypted text
4. Your original message appears

### 📁 Encrypt a File
1. Press `4`
2. Select your key
3. Enter the file path (e.g., `documents/secret.pdf`)
4. An encrypted copy is created (`secret.pdf.enc`)

### 📂 Decrypt a File
1. Press `5`
2. Select the SAME key
3. Enter the `.enc` file path
4. Your original file is restored

---

## Understanding the Code

### `key_manager.py` — The Key Vault
- **Generates** cryptographically secure random keys using `Fernet.generate_key()`
- **Saves** keys to `.key` files in a `keys/` directory
- **Loads** keys back from disk when needed

### `encryptor.py` — The Text Cipher
- **Encrypts** strings by converting them to bytes, running AES encryption, returning base64
- **Decrypts** by reversing the process — base64 decode → AES decrypt → UTF-8 string
- Raises helpful `ValueError` messages if the wrong key is used

### `file_handler.py` — The File Vault
- Works exactly like encryptor but reads/writes **binary files** instead of strings
- Appends `.enc` to encrypted files, strips it when decrypting
- Shows file sizes and handles any file type

### `main.py` — The Interface
- Draws the menu and handles user input
- Calls the right module for each menu option
- Handles errors gracefully so the program never crashes rudely

---

## Key Concepts Explained

### What is Encryption?
Encryption is a mathematical process that transforms readable data ("plaintext") into unreadable scrambled data ("ciphertext"). Only someone with the correct key can reverse it.

### What Algorithm Is Used?
**Fernet** (from the `cryptography` library), which uses:
- **AES-128** — Advanced Encryption Standard, 128-bit key
- **CBC mode** — each data block is chained to the previous
- **HMAC-SHA256** — detects tampering (if anyone modifies your encrypted data, decryption will fail)

### What Is a Key?
32 random bytes (256 bits), base64-encoded. Generated using hardware-sourced randomness from the operating system. There are 2^256 possible keys — more than atoms in the universe.

### What Is base64?
A way to represent binary data (bytes) as printable ASCII text. Encrypted data is raw bytes; base64 makes it safe to copy/paste, email, or store in text files.

---

## Security Best Practices

| Do ✅ | Don't ❌ |
|-------|---------|
| Back up your `.key` file in multiple places | Share your key over email or chat |
| Use a different key for different purposes | Hardcode keys in your Python code |
| Delete originals after encrypting sensitive files | Commit `.key` files to GitHub |
| Store keys outside your project directory | Use the same key forever without rotation |

---

## Suggested Improvements (Learning Challenges)

Once you understand the basics, try these:

1. **Password-Protected Keys** — Encrypt the key file itself with a password using `cryptography.hazmat.primitives.kdf.pbkdf2`
2. **Key Rotation** — Re-encrypt all files when you generate a new key
3. **GUI Interface** — Build a graphical interface with `tkinter` or `PySimpleGUI`
4. **Asymmetric Encryption** — Use RSA key pairs so a sender can encrypt without knowing the receiver's private key
5. **Secure File Deletion** — Overwrite the original file with zeros before deleting
6. **Compression** — Compress files before encrypting for smaller `.enc` files
7. **Multiple Recipients** — Encrypt the same file for multiple key holders

---

## Dependencies

| Library | Purpose | Install |
|---------|---------|---------|
| `cryptography` | AES encryption via Fernet | `pip install cryptography` |
| `os` | File system operations | Built into Python |
| `base64` | Binary-to-text encoding | Built into Python |
| `logging` | Event logging | Built into Python |
| `sys` | Program exit | Built into Python |

---

## License

This project is for educational purposes. Use it to learn — then build something even better!
