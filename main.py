import os
import csv
import base64
from gui import App
from utils import *

HEADER = """
--------------- <> ---------------
File Encryptor/Decryptor by Purinat33
--------------- <> ---------------
"""


def create_table():
    """
    This function will create, if not exists, the authentication table CSV file.
    The file will store only the salt, nonce, and ciphertext. No plaintext password will not be stored.
    Mimicking a database but simple

    Structure:

    1. KDF Algorithm
    2. KDF-N,
    3. KDF-R,
    4. KDF-P
    5. Salt
    6. AEAD Algorithm
    7. Nonce
    8. Ciphertext Path
    9. Tag (From the AES Crypto Library)
    10. Original File Name
    """

    # https://www.geeksforgeeks.org/python/working-csv-files-python/
    if os.path.exists(FILE_NAME):
        return

    fields = ['kdf', 'n', 'r', 'p', 'salt',
              'aead', 'nonce', 'ciphertext_enc', 'tag', 'filename']
    with open(FILE_NAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)


def main_menu():
    """Display the main page and get a user input"""
    print(HEADER)
    choice = int(input("Encrypt (1), Decrypt (2) or Exit (3): "))
    return choice


def execute_mode(choice):
    if choice == 1:
        encrypt()
    else:
        decrypt()


def main():
    # Check if the authentication table exists
    create_table()
    # while True:
    #     choice = main_menu()
    #     if choice > 3:
    #         print("Wrong Choice")
    #     else:
    #         break

    # if choice == 3:
    #     print("Goodbye")
    #     return

    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
