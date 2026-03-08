"""
============================================================
  key_manager.py — Encryption Key Generator & Storage
============================================================

BEGINNER CONCEPT: What is an Encryption Key?
---------------------------------------------
Think of an encryption key like a physical key to a padlock.
Without the exact key, you cannot open the lock (decrypt data).

In digital encryption:
- The "key" is a long string of random bytes (random numbers)
- The stronger (more random) the key, the harder it is to guess
- If you lose your key, your encrypted data is GONE forever
- NEVER share your key with anyone you don't trust

This file handles:
1. Generating a strong encryption key
2. Saving the key to disk safely
3. Loading the key back from disk when needed
"""

# ── Imports ──────────────────────────────────────────────
# These are Python "modules" — pre-built tools we borrow.

from cryptography.fernet import Fernet
# Fernet: A ready-made, secure encryption system.
# It uses AES-128 encryption + HMAC authentication internally.
# Think of Fernet as a "secure envelope" system.

import os
# os: Lets us interact with the operating system —
# check if files exist, create directories, etc.

import logging
# logging: A professional way to print messages/errors
# to a file or the screen. Better than plain print() for
# real applications because you can control what gets shown.

# ── Set up logging ────────────────────────────────────────
# This creates a "logger" — a reporter that logs what happens.
# format= defines what each log line looks like:
#   %(asctime)s  → timestamp  e.g. 2024-01-01 10:00:00
#   %(levelname)s → severity  e.g. INFO, WARNING, ERROR
#   %(message)s  → our message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)
# __name__ is a special Python variable — it's the name of
# this file/module. Using it means logs show WHICH file logged.


# ── KeyManager Class ──────────────────────────────────────
# A "class" is a blueprint. KeyManager is our blueprint
# for everything related to keys.
class KeyManager:
    """
    Handles the lifecycle of encryption keys:
    generate → save → load
    """

    def __init__(self, key_directory: str = "keys"):
        """
        __init__ is the "constructor" — it runs automatically
        when you create a KeyManager object.

        key_directory: The folder where we'll save keys.
                       Defaults to a folder called "keys".
        """
        # Store the directory name on the object so all
        # methods in this class can access it via self.
        self.key_directory = key_directory

        # Create the keys folder if it doesn't already exist.
        # exist_ok=True means "don't crash if it already exists"
        os.makedirs(self.key_directory, exist_ok=True)
        logger.info(f"KeyManager ready. Keys folder: '{self.key_directory}'")

    # ── Generate Key ──────────────────────────────────────
    def generate_key(self) -> bytes:
        """
        Generates a brand-new, cryptographically secure key.

        Returns: bytes — the raw key data (32 random bytes,
                 base64-encoded to be printable/saveable)

        SECURITY NOTE:
        Fernet.generate_key() uses os.urandom() under the hood,
        which asks the operating system for TRUE random bytes
        sourced from hardware noise. This is far more secure
        than Python's random module (which is predictable).
        """
        # Ask Fernet to generate a fresh, random 32-byte key.
        key = Fernet.generate_key()

        # Log that we made a new key (don't log the key itself!)
        logger.info("New encryption key generated successfully.")

        # Return the key bytes so the caller can use or save them.
        return key

    # ── Save Key ──────────────────────────────────────────
    def save_key(self, key: bytes, filename: str = "secret.key") -> str:
        """
        Saves the encryption key to a file on disk.

        key:      The key bytes to save.
        filename: The name of the file. Default: "secret.key"
        Returns:  The full path where the key was saved.

        SECURITY BEST PRACTICE:
        - Store key files outside your project directory in real apps
        - Never commit key files to Git (add *.key to .gitignore)
        - Consider encrypting the key file itself with a password
        """
        # Build the full file path: e.g., "keys/secret.key"
        # os.path.join() builds paths correctly on ALL operating
        # systems (Windows uses \, Linux/Mac uses /)
        key_path = os.path.join(self.key_directory, filename)

        # Open the file for writing in binary mode ("wb").
        # "w"  = write mode (overwrites if exists)
        # "b"  = binary mode (keys are raw bytes, not text)
        # The 'with' statement automatically closes the file
        # even if an error occurs — always use 'with' for files!
        with open(key_path, "wb") as key_file:
            key_file.write(key)  # Write the raw key bytes

        logger.info(f"Key saved to: {key_path}")
        # Return the path so the user knows where their key is
        return key_path

    # ── Load Key ──────────────────────────────────────────
    def load_key(self, filename: str = "secret.key") -> bytes:
        """
        Loads an existing key from a file on disk.

        filename: The key file to load. Default: "secret.key"
        Returns:  The key as bytes, ready to use for encryption.

        Raises FileNotFoundError if the key file doesn't exist.
        """
        key_path = os.path.join(self.key_directory, filename)

        # Check if the file actually exists before trying to open it.
        # This gives a clear error message instead of a cryptic crash.
        if not os.path.exists(key_path):
            logger.error(f"Key file not found: {key_path}")
            # 'raise' throws an error that the caller must handle.
            # We attach a helpful message explaining the problem.
            raise FileNotFoundError(
                f"Key file '{key_path}' not found. "
                "Generate and save a key first."
            )

        # Open in binary read mode ("rb") — same reason as above,
        # keys are raw bytes, not human-readable text.
        with open(key_path, "rb") as key_file:
            key = key_file.read()  # Read all bytes from the file

        logger.info(f"Key loaded from: {key_path}")
        return key

    # ── List Saved Keys ───────────────────────────────────
    def list_keys(self) -> list:
        """
        Returns a list of all .key files in the keys directory.
        Useful for letting users pick which key to use.
        """
        # os.listdir() returns all filenames in a directory.
        # We filter with a "list comprehension" — a compact way
        # to build a list using a condition (if f.endswith(".key"))
        keys = [
            f for f in os.listdir(self.key_directory)
            if f.endswith(".key")
        ]
        return keys
