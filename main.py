import os
import secrets
import csv
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

FILE_NAME = 'authenticate.csv'

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

    1. KDF Algorithm|parameters
    2. Salt
    3. AEAD Algorithm
    4. Nonce
    5. Ciphertext
    """

    # https://www.geeksforgeeks.org/python/working-csv-files-python/
    if os.path.exists(FILE_NAME):
        return

    fields = ['kdf', 'salt', 'aead', 'nonce', 'ciphertext']
    with open(FILE_NAME, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(fields)


def main_menu():
    """Display the main page and get a user input"""
    print(HEADER)
    choice = int(input("Encrypt (1), Decrypt (2) or Exit (3): "))
    return choice


def main():
    # Check if the authentication table
    create_table()
    while True:
        choice = main_menu()
        if choice > 3:
            print("Wrong Choice")
        else:
            break

    if choice == 3:
        print("Goodbye")
        return


if __name__ == '__main__':
    main()
