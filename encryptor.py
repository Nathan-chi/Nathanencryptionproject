"""
============================================================
  encryptor.py — Text Encryption & Decryption Engine
============================================================

BEGINNER CONCEPT: How Does Encryption Work?
--------------------------------------------
Encryption transforms readable text ("plaintext") into
scrambled gibberish ("ciphertext") using a mathematical
algorithm + a key.

Example:
  Plaintext:  "Hello, World!"
  Key:        (secret random bytes)
  Ciphertext: "gAAAAABl3xK9M2...z8=" (unreadable)

Only someone with THE SAME KEY can reverse the process
(decryption) and get back "Hello, World!".

This uses SYMMETRIC encryption — same key for both
encrypting and decrypting. It's fast and secure for
personal use or when both parties share the key.

Algorithm Used: AES-128-CBC (via Fernet)
- AES = Advanced Encryption Standard
- 128-bit key = 3.4 × 10³⁸ possible keys (unbreakable by brute force)
- CBC = Cipher Block Chaining (each block of data affects the next)
- Fernet also adds HMAC authentication to detect tampering
"""

# ── Imports ──────────────────────────────────────────────
from cryptography.fernet import Fernet, InvalidToken
# Fernet: Our encryption engine
# InvalidToken: The error Fernet raises when decryption fails
# (wrong key, corrupted data, or tampered message)

import base64
# base64: Converts binary (bytes) to ASCII-safe text.
# Encrypted data is raw bytes — base64 makes it safe to
# copy/paste, store in text files, or send via email.

import logging

logger = logging.getLogger(__name__)


# ── Encryptor Class ───────────────────────────────────────
class Encryptor:
    """
    Encrypts and decrypts text messages using a Fernet key.

    Usage:
        enc = Encryptor(key)
        ciphertext = enc.encrypt_text("my secret")
        plaintext  = enc.decrypt_text(ciphertext)
    """

    def __init__(self, key: bytes):
        """
        Constructor — sets up the encryptor with a specific key.

        key: The encryption key (bytes from KeyManager).

        WHAT IS self?
        'self' refers to THIS specific object. When you create
        multiple Encryptor objects with different keys, 'self'
        keeps each object's data separate.
        """
        # Store the key on the object for use by encrypt/decrypt
        self.key = key

        # Create a Fernet object — this is the actual cipher engine.
        # It validates the key format and prepares the algorithm.
        # If the key is invalid, this will raise an error immediately.
        self.cipher = Fernet(key)

        logger.info("Encryptor initialized with provided key.")

    # ── Encrypt Text ──────────────────────────────────────
    def encrypt_text(self, plaintext: str) -> str:
        """
        Encrypts a plain text string.

        plaintext: The message you want to protect (a string).
        Returns:   The encrypted message as a base64 string
                   (safe to copy, store, or send anywhere).

        Step-by-step what happens internally:
        1. Convert the string to bytes (UTF-8 encoding)
        2. Generate a random IV (Initialization Vector) — makes
           the same message encrypt differently each time
        3. AES-encrypt the bytes using the key + IV
        4. HMAC-sign the result (proves it hasn't been tampered with)
        5. base64-encode everything into a printable string
        """
        # Type check — make sure the user passed a string, not bytes
        if not isinstance(plaintext, str):
            raise TypeError("plaintext must be a string (str).")

        # Convert the string to bytes.
        # All encryption works on bytes, not strings.
        # UTF-8 supports all characters including emojis and unicode.
        plaintext_bytes = plaintext.encode("utf-8")

        # Encrypt! The cipher does all the hard math for us.
        # Returns bytes — the raw encrypted data.
        encrypted_bytes = self.cipher.encrypt(plaintext_bytes)

        # Convert the encrypted bytes to a regular string.
        # .decode("utf-8") turns bytes → string
        # The result looks like: "gAAAAABl3xK9M2..."
        encrypted_str = encrypted_bytes.decode("utf-8")

        logger.info(f"Text encrypted. Original length: {len(plaintext)} chars.")
        return encrypted_str

    # ── Decrypt Text ──────────────────────────────────────
    def decrypt_text(self, encrypted_text: str) -> str:
        """
        Decrypts a previously encrypted string.

        encrypted_text: The encrypted string (from encrypt_text).
        Returns:        The original plain text message.

        Raises:
            ValueError — if the key is wrong or data is corrupted
        """
        if not isinstance(encrypted_text, str):
            raise TypeError("encrypted_text must be a string (str).")

        # Convert the encrypted string back to bytes for Fernet
        encrypted_bytes = encrypted_text.encode("utf-8")

        # Try to decrypt. Wrap in try/except to handle failures
        # gracefully instead of crashing with a scary traceback.
        try:
            # Fernet.decrypt() does:
            # 1. Verify the HMAC signature (proves data is intact)
            # 2. Decode the base64
            # 3. AES-decrypt the bytes
            # 4. Return the original plaintext bytes
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)

        except InvalidToken:
            # InvalidToken means one of:
            # - Wrong key was used
            # - The encrypted text was corrupted/modified
            # - The text wasn't encrypted with Fernet at all
            logger.error("Decryption failed — wrong key or corrupted data.")
            raise ValueError(
                "Decryption failed. Possible causes:\n"
                "  1. Wrong encryption key\n"
                "  2. The encrypted text was modified\n"
                "  3. This text wasn't encrypted with this tool"
            )

        # Convert the decrypted bytes back to a string
        plaintext = decrypted_bytes.decode("utf-8")

        logger.info(f"Text decrypted successfully. Length: {len(plaintext)} chars.")
        return plaintext

    # ── Utility: Preview Encrypted Text ───────────────────
    @staticmethod
    def preview(text: str, length: int = 40) -> str:
        """
        Returns a short preview of long text for display.
        @staticmethod means this method doesn't need 'self' —
        it's a helper function that lives inside the class.
        """
        if len(text) > length:
            return text[:length] + "..."
        return text
