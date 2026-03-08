"""
============================================================
  file_handler.py — File Encryption & Decryption Engine
============================================================

BEGINNER CONCEPT: Encrypting Files vs Text
-------------------------------------------
Encrypting a FILE is basically the same as encrypting text —
we read the file's bytes, encrypt them, and write a new file.

The difference:
- Text encryption: we deal with strings (human-readable)
- File encryption: we deal with raw bytes (could be a PDF,
  image, video, or any binary data)

ENCRYPTED FILE FORMAT:
We save encrypted files with a ".enc" extension so we know
they've been encrypted. Example:
  photo.jpg → photo.jpg.enc  (encrypted)
  photo.jpg.enc → photo.jpg  (decrypted, restored)

SECURITY BEST PRACTICE:
After encrypting a sensitive file, you should securely DELETE
the original (use a proper shredder utility, not just trash).
Simply deleting a file leaves the data recoverable!
"""

# ── Imports ──────────────────────────────────────────────
from cryptography.fernet import Fernet, InvalidToken
# Same encryption engine used for text

import os
# os: For file path operations, checking file existence,
# getting file sizes, etc.

import logging

logger = logging.getLogger(__name__)

# File extension for encrypted files (our convention)
ENCRYPTED_EXTENSION = ".enc"


# ── FileHandler Class ─────────────────────────────────────
class FileHandler:
    """
    Encrypts and decrypts files of any type.

    Works with: .txt, .pdf, .jpg, .png, .docx, .mp3 — anything!
    The content is just bytes; encryption doesn't care about format.
    """

    def __init__(self, key: bytes):
        """
        key: The encryption key (bytes from KeyManager)
        """
        self.key = key
        # Create the Fernet cipher (same as in Encryptor)
        self.cipher = Fernet(key)
        logger.info("FileHandler initialized.")

    # ── Encrypt File ──────────────────────────────────────
    def encrypt_file(self, input_path: str, output_path: str = None) -> str:
        """
        Encrypts a file and saves the result.

        input_path:  Path to the file you want to encrypt.
                     Example: "documents/report.pdf"

        output_path: Where to save the encrypted file.
                     If None, appends ".enc" to the input path.
                     Example: "documents/report.pdf.enc"

        Returns: The path where the encrypted file was saved.

        WHAT ARE PATHS?
        A "path" is the address of a file on your computer.
        "documents/report.pdf" means: in the "documents" folder,
        find the file called "report.pdf".
        """
        # Validate: does the input file actually exist?
        if not os.path.exists(input_path):
            logger.error(f"File not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: '{input_path}'")

        # If no output path was given, create one by adding ".enc"
        if output_path is None:
            output_path = input_path + ENCRYPTED_EXTENSION

        # Get the file size for logging (os.path.getsize returns bytes)
        file_size = os.path.getsize(input_path)
        logger.info(f"Encrypting '{input_path}' ({file_size} bytes)...")

        # ── Read the original file ────────────────────────
        # "rb" = read binary — reads the raw bytes of ANY file type
        # We use 'with' so the file is always closed, even on error
        with open(input_path, "rb") as f:
            original_data = f.read()  # Read ALL bytes at once
        # original_data is now a bytes object like: b'\x89PNG\r\n...'

        # ── Encrypt the bytes ─────────────────────────────
        # Fernet encrypts bytes just as well as text bytes.
        # The math doesn't know or care what kind of file this is.
        encrypted_data = self.cipher.encrypt(original_data)

        # ── Write the encrypted file ──────────────────────
        # "wb" = write binary — write raw bytes to file
        with open(output_path, "wb") as f:
            f.write(encrypted_data)

        logger.info(
            f"File encrypted successfully.\n"
            f"  Original:  {input_path} ({file_size:,} bytes)\n"
            f"  Encrypted: {output_path} ({os.path.getsize(output_path):,} bytes)"
        )
        return output_path

    # ── Decrypt File ──────────────────────────────────────
    def decrypt_file(self, input_path: str, output_path: str = None) -> str:
        """
        Decrypts an encrypted file and restores the original.

        input_path:  Path to the encrypted file (e.g., "report.pdf.enc")
        output_path: Where to save the decrypted file.
                     If None, removes the ".enc" extension.

        Returns: The path where the decrypted file was saved.
        """
        # Validate input
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Encrypted file not found: '{input_path}'")

        # If no output path given, strip the ".enc" extension
        if output_path is None:
            if input_path.endswith(ENCRYPTED_EXTENSION):
                # Remove the last 4 characters (".enc")
                output_path = input_path[: -len(ENCRYPTED_EXTENSION)]
            else:
                # If it doesn't end in .enc, add "_decrypted" to name
                # os.path.splitext splits "photo.jpg" → ("photo", ".jpg")
                base, ext = os.path.splitext(input_path)
                output_path = base + "_decrypted" + ext

        logger.info(f"Decrypting '{input_path}'...")

        # ── Read the encrypted file ───────────────────────
        with open(input_path, "rb") as f:
            encrypted_data = f.read()

        # ── Decrypt the bytes ─────────────────────────────
        try:
            original_data = self.cipher.decrypt(encrypted_data)
        except InvalidToken:
            logger.error("File decryption failed — wrong key or corrupted file.")
            raise ValueError(
                "File decryption failed!\n"
                "  • Make sure you're using the SAME key used to encrypt\n"
                "  • Make sure the file hasn't been modified since encryption"
            )

        # ── Write the restored file ───────────────────────
        with open(output_path, "wb") as f:
            f.write(original_data)

        logger.info(
            f"File decrypted successfully.\n"
            f"  Encrypted: {input_path}\n"
            f"  Restored:  {output_path} ({os.path.getsize(output_path):,} bytes)"
        )
        return output_path

    # ── Utility: Get File Info ─────────────────────────────
    @staticmethod
    def get_file_info(path: str) -> dict:
        """
        Returns basic information about a file.
        @staticmethod: doesn't need 'self', just a helper.
        Returns a dict (dictionary) — like a labeled box of values.
        """
        if not os.path.exists(path):
            return {"exists": False}

        size = os.path.getsize(path)  # Size in bytes

        # Format size for human readability
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 ** 2:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / 1024**2:.1f} MB"

        return {
            "exists": True,
            "size_bytes": size,
            "size_human": size_str,
            # os.path.basename gets just the filename from a full path
            "filename": os.path.basename(path),
            # os.path.abspath gives the full absolute path
            "full_path": os.path.abspath(path),
        }
