"""
============================================================
  main.py — The Main Program (Entry Point)
============================================================

This is the file you RUN to start the program.
It displays a menu and connects all the other modules together.

BEGINNER CONCEPT: What is a "main" file?
-----------------------------------------
In a multi-file Python project, one file acts as the "hub"
that imports and uses all the other files. This is main.py.

Think of it like a restaurant:
  main.py      -> the waiter (takes orders, coordinates)
  key_manager  -> the vault (stores the key/recipes)
  encryptor    -> the chef for text dishes
  file_handler -> the chef for file dishes

HOW TO RUN THIS PROGRAM:
  1. Open your terminal
  2. Navigate to this folder: cd encryption_tool
  3. Run: python main.py
"""

# -- Standard Library Imports -----------------------------
import os
# os: Used for clearing the terminal screen (nice UX touch)
# and checking paths

import sys
# sys: Gives access to system-level things, like exiting the
# program cleanly with sys.exit()

import logging
# logging: Logs events to a file so we have a record

# -- Our Own Modules (Local Imports) ----------------------
# These import classes from the other files we created.
# 'from file import Class' means: go to that file, grab that class.
from key_manager import KeyManager
from encryptor import Encryptor
from file_handler import FileHandler


# -- Configure Logging -------------------------------------
# This sets up logging to BOTH the screen AND a log file.
# Helpful for debugging — you can review what happened later.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        # FileHandler writes logs to a file
        logging.FileHandler("encryption_tool.log"),
        # StreamHandler prints logs to the terminal
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# -- Visual Helpers ----------------------------------------
# ANSI color codes — these make terminal text colorful!
# \033[Xm  where X is the color code
# These work on Mac, Linux, and modern Windows terminals.
class Color:
    CYAN    = "\033[96m"   # Bright cyan — headers
    GREEN   = "\033[92m"   # Green — success messages
    YELLOW  = "\033[93m"   # Yellow — prompts / warnings
    RED     = "\033[91m"   # Red — errors
    BOLD    = "\033[1m"    # Bold text
    RESET   = "\033[0m"    # Reset to default color
    DIM     = "\033[2m"    # Dim/grey text


def cprint(text: str, color: str = Color.RESET):
    """Print text in a specific color."""
    print(f"{color}{text}{Color.RESET}")


def clear_screen():
    """Clears the terminal for a clean look."""
    # 'cls' = Windows command, 'clear' = Mac/Linux command
    # os.name == 'nt' means we're on Windows (NT = Windows NT)
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    """Prints the app's decorative header."""
    clear_screen()
    cprint("=" * 58, Color.CYAN)
    cprint("   ***  SECURE ENCRYPTION TOOL  ***", Color.BOLD)
    cprint("   Built with Python + cryptography library", Color.DIM)
    cprint("=" * 58, Color.CYAN)
    print()


def print_menu():
    """Prints the main menu options."""
    cprint("  MAIN MENU", Color.BOLD)
    cprint("  " + "-" * 40, Color.DIM)
    print("  [1]  Generate a new encryption key")
    print("  [2]  Encrypt a text message")
    print("  [3]  Decrypt a text message")
    print("  [4]  Encrypt a file")
    print("  [5]  Decrypt a file")
    print("  [6]  List saved keys")
    print("  [7]  Help & explanations")
    print("  [0]  Exit")
    cprint("  " + "-" * 40, Color.DIM)


def prompt(message: str) -> str:
    """Ask the user for input. Returns their answer as a string."""
    # input() pauses the program and waits for the user to type.
    # The message is displayed as a prompt so they know what to enter.
    return input(f"{Color.YELLOW}{message}{Color.RESET}").strip()
    # .strip() removes leading/trailing whitespace from their input
    # (handles accidental spaces or newlines)


def success(msg: str):
    cprint(f"\n  [OK]  {msg}", Color.GREEN)


def error(msg: str):
    cprint(f"\n  [ERROR]  {msg}", Color.RED)


def info(msg: str):
    cprint(f"\n  [INFO]   {msg}", Color.CYAN)


def pause():
    """Wait for the user to press Enter before continuing."""
    input(f"\n{Color.DIM}  Press Enter to return to menu...{Color.RESET}")


# ==========================================================
#  FEATURE FUNCTIONS - Each menu option is its own function
# ==========================================================

def feature_generate_key(km: KeyManager):
    """
    Menu option 1: Generate and save a new encryption key.
    km: a KeyManager object passed in from main()
    """
    print_banner()
    cprint("  KEY: GENERATE NEW KEY", Color.BOLD)
    print()

    # Generate the key
    key = km.generate_key()

    # Show the user a preview of the key
    # The key is bytes; .decode() makes it a printable string
    key_preview = key.decode("utf-8")[:20] + "..."
    info(f"Key generated: {key_preview}")

    # Ask what to name the key file
    print()
    name = prompt("  Enter a name for this key file (e.g., mykey): ").strip()

    # Validate: don't allow empty names
    if not name:
        error("Key name cannot be empty.")
        pause()
        return

    # Add .key extension if not already there
    if not name.endswith(".key"):
        name += ".key"

    # Save the key
    try:
        path = km.save_key(key, filename=name)
        success(f"Key saved to: {path}")
        cprint("\n  !!! IMPORTANT: Back up this file!", Color.YELLOW)
        cprint("  Without it, your encrypted data cannot be recovered.", Color.YELLOW)
    except Exception as e:
        error(f"Failed to save key: {e}")

    pause()


def feature_encrypt_text(km: KeyManager):
    """Menu option 2: Encrypt a text message."""
    print_banner()
    cprint("  TEXT: ENCRYPT TEXT", Color.BOLD)
    print()

    # Step 1: Load a key
    key = _select_key(km)
    if key is None:
        return

    # Step 2: Get the text to encrypt
    print()
    plaintext = prompt("  Enter the text to encrypt:\n  > ")
    if not plaintext:
        error("No text entered.")
        pause()
        return

    # Step 3: Encrypt
    try:
        enc = Encryptor(key)
        ciphertext = enc.encrypt_text(plaintext)

        print()
        success("Text encrypted successfully!")
        print()
        cprint("  ENCRYPTED OUTPUT (copy everything below):", Color.CYAN)
        cprint("  " + "-" * 50, Color.DIM)
        # Print the ciphertext — this is what the user shares/stores
        print(f"  {ciphertext}")
        cprint("  " + "-" * 50, Color.DIM)
        cprint("  !!! Store this WITH your key file to decrypt later.", Color.YELLOW)

    except Exception as e:
        error(f"Encryption failed: {e}")

    pause()


def feature_decrypt_text(km: KeyManager):
    """Menu option 3: Decrypt an encrypted text message."""
    print_banner()
    cprint("  TEXT: DECRYPT TEXT", Color.BOLD)
    print()

    # Step 1: Load the key (must be same key used to encrypt)
    key = _select_key(km)
    if key is None:
        return

    # Step 2: Get the encrypted text
    print()
    ciphertext = prompt("  Paste the encrypted text:\n  > ")
    if not ciphertext:
        error("No text entered.")
        pause()
        return

    # Step 3: Decrypt
    try:
        enc = Encryptor(key)
        plaintext = enc.decrypt_text(ciphertext)

        print()
        success("Decryption successful!")
        print()
        cprint("  ORIGINAL MESSAGE:", Color.CYAN)
        cprint("  " + "-" * 50, Color.DIM)
        print(f"  {plaintext}")
        cprint("  " + "-" * 50, Color.DIM)

    except ValueError as e:
        # Our custom error from Encryptor — user-friendly message
        error(str(e))
    except Exception as e:
        error(f"Unexpected error: {e}")

    pause()


def feature_encrypt_file(km: KeyManager):
    """Menu option 4: Encrypt a file."""
    print_banner()
    cprint("  FILE: ENCRYPT FILE", Color.BOLD)
    print()

    # Step 1: Load key
    key = _select_key(km)
    if key is None:
        return

    # Step 2: Get file path
    print()
    filepath = prompt("  Enter the path to the file to encrypt:\n  > ")
    if not filepath:
        error("No path entered.")
        pause()
        return

    # Step 3: Encrypt
    try:
        fh = FileHandler(key)

        # Show file info before encrypting
        info_data = FileHandler.get_file_info(filepath)
        if not info_data["exists"]:
            error(f"File not found: '{filepath}'")
            pause()
            return

        info(f"File: {info_data['filename']}  |  Size: {info_data['size_human']}")

        # Confirm before proceeding
        confirm = prompt("\n  Encrypt this file? (y/n): ").lower()
        if confirm != "y":
            info("Cancelled.")
            pause()
            return

        output_path = fh.encrypt_file(filepath)

        success(f"File encrypted!")
        print(f"  [Output]  Encrypted file saved as: {output_path}")
        cprint("\n  TIP: The original file still exists.", Color.YELLOW)
        cprint("  Delete it manually if you want it gone.", Color.YELLOW)

    except FileNotFoundError as e:
        error(str(e))
    except Exception as e:
        error(f"Encryption error: {e}")

    pause()


def feature_decrypt_file(km: KeyManager):
    """Menu option 5: Decrypt an encrypted file."""
    print_banner()
    cprint("  FILE: DECRYPT FILE", Color.BOLD)
    print()

    key = _select_key(km)
    if key is None:
        return

    print()
    filepath = prompt("  Enter the path to the encrypted file (.enc):\n  > ")
    if not filepath:
        error("No path entered.")
        pause()
        return

    try:
        fh = FileHandler(key)
        output_path = fh.decrypt_file(filepath)
        success(f"File decrypted!")
        print(f"  [Output]  Restored file saved as: {output_path}")

    except FileNotFoundError as e:
        error(str(e))
    except ValueError as e:
        error(str(e))
    except Exception as e:
        error(f"Decryption error: {e}")

    pause()


def feature_list_keys(km: KeyManager):
    """Menu option 6: Show all saved key files."""
    print_banner()
    cprint("  KEYS: SAVED KEYS", Color.BOLD)
    print()

    keys = km.list_keys()

    if not keys:
        info("No key files found in the 'keys/' folder.")
        info("Use option [1] to generate your first key.")
    else:
        cprint(f"  Found {len(keys)} key(s) in '{km.key_directory}/':", Color.CYAN)
        print()
        # enumerate() gives us a counter (i) alongside each item (k)
        for i, k in enumerate(keys, start=1):
            print(f"    {i}. {k}")

    pause()


def feature_help():
    """Menu option 7: Educational help section."""
    print_banner()
    cprint("  HELP: HOW ENCRYPTION WORKS", Color.BOLD)
    print()

    help_text = """
  WHAT IS ENCRYPTION?
  ------------------------------------------------
  Encryption scrambles your data so only someone
  with the right KEY can read it.

  Like a locked safe: anyone can see the safe, but
  only the person with the combination can open it.

  SYMMETRIC ENCRYPTION (what this tool uses):
  ------------------------------------------------
  - One key encrypts AND decrypts
  - Fast and efficient
  - Best for personal use or when both parties
    already share the key securely

  THE ALGORITHM: AES-128 via Fernet
  ------------------------------------------------
  - AES = Advanced Encryption Standard
  - Used by governments and banks worldwide
  - 128-bit key = 2^128 possibilities
    = 340 undecillion combinations
    = Computationally impossible to brute-force

  WHAT IS A HASH?
  ------------------------------------------------
  A hash is a one-way fingerprint of data.
  - Input: "Hello" -> Output: "185f8db32..."
  - You CANNOT reverse a hash to get the original
  - Used for passwords (store hash, not password)
  - Tiny change in input = completely different hash

  SECURITY BEST PRACTICES:
  ------------------------------------------------
  [YES]  Back up your key file in multiple safe places
  [YES]  Never share your key over email/chat
  [YES]  Use a strong password manager
  [YES]  Securely delete original files after encryption
  [YES]  Use different keys for different purposes
  [NO]   Never hardcode keys into your code
  [NO]   Never commit key files to Git/GitHub
  [NO]   Never use weak passwords as keys
    """
    print(help_text)
    pause()


# -- Private Helper: Select Key ----------------------------
# Functions starting with _ are "private" by convention —
# they're helpers used internally, not called from outside.
def _select_key(km: KeyManager) -> bytes | None:
    """
    Prompts the user to select or enter a key file.
    Returns the key bytes, or None if cancelled/failed.
    """
    keys = km.list_keys()

    if not keys:
        error("No keys found! Generate a key first (option 1).")
        pause()
        return None

    cprint("  Available keys:", Color.CYAN)
    for i, k in enumerate(keys, start=1):
        print(f"    {i}. {k}")
    print(f"    0. Enter custom key filename")
    print()

    choice = prompt("  Select key number (or 0 for custom): ")

    try:
        choice_int = int(choice)
    except ValueError:
        error("Invalid input — enter a number.")
        pause()
        return None

    if choice_int == 0:
        filename = prompt("  Enter key filename: ")
    elif 1 <= choice_int <= len(keys):
        filename = keys[choice_int - 1]
    else:
        error("Invalid selection.")
        pause()
        return None

    try:
        return km.load_key(filename)
    except FileNotFoundError as e:
        error(str(e))
        pause()
        return None


# ==========================================================
#  MAIN FUNCTION - The Program Loop
# ==========================================================

def main():
    """
    The main function — runs the program.

    This is the "event loop": show menu → get input → act → repeat.
    """
    # Create the KeyManager once; all features share it
    km = KeyManager(key_directory="keys")

    # A "while True" loop runs forever until we explicitly break out
    while True:
        print_banner()
        print_menu()
        print()

        choice = prompt("  Enter your choice: ")

        # Match the user's choice to the right feature function
        # Python 3.10+ supports 'match/case' (like switch in other languages)
        # We use if/elif for broader Python version compatibility.
        if choice == "1":
            feature_generate_key(km)

        elif choice == "2":
            feature_encrypt_text(km)

        elif choice == "3":
            feature_decrypt_text(km)

        elif choice == "4":
            feature_encrypt_file(km)

        elif choice == "5":
            feature_decrypt_file(km)

        elif choice == "6":
            feature_list_keys(km)

        elif choice == "7":
            feature_help()

        elif choice == "0":
            print_banner()
            cprint("  Goodbye! Stay secure.", Color.GREEN)
            print()
            # sys.exit(0) = exit program normally (0 = success code)
            sys.exit(0)

        else:
            error("Invalid option. Please enter 0–7.")
            pause()


# -- Entry Point Guard -------------------------------------
# This is a Python convention:
# __name__ == "__main__" is True ONLY when you run this file directly.
# If another file imports main.py, this block is SKIPPED.
# This prevents main() from running accidentally on import.
if __name__ == "__main__":
    main()
