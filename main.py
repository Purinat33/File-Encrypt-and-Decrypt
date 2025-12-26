import os
import secrets
import csv
import base64
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES

FILE_NAME = 'authenticate.csv'

HEADER = """
--------------- <> ---------------
File Encryptor/Decryptor by Purinat33
--------------- <> ---------------
"""

# For storage
KDF = "scrypt"
N = 2**16
r = 8
p = 1

AEAD = 'AES-GCM'


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
    with open(FILE_NAME, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(fields)


def main_menu():
    """Display the main page and get a user input"""
    print(HEADER)
    choice = int(input("Encrypt (1), Decrypt (2) or Exit (3): "))
    return choice


def encrypt():
    """
    Encrypt the File:

    1. User select a file by pasting the filepath
    2. User enter a password
    3. A **salt** is created
    4. A key created from salt and password (Using scrypt KDF)
    5. A **nonce** and **tag** is created using the key (Using AES)
        * The nonce is created automatically using Cryptodome AES
    6. Encrypt the _content_ of the file with the Cipher
    7. Store each content in the CSV
    """
    file_to_read = input("File Path: ")
    if not os.path.exists(file_to_read):
        print("File doesn't exist. Exiting...")
        return

    with open(file_to_read, 'rb') as f:
        file = f.read()

    # Do everything else
    password_str = (input("Input Password here: "))
    password = password_str.encode()
    salt = get_random_bytes(16)
    key = scrypt(password, salt, 16, N=N, r=r, p=p)
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce

    ciphertext, tag = cipher.encrypt_and_digest(file)
    # Storage
    # Convert byte fields into base64
    salt_b64 = base64.b64encode(salt)
    nonce_b64 = base64.b64encode(nonce)
    ciphertext_b64 = base64.b64encode(ciphertext)
    tag_b64 = base64.b64encode(tag)

    # A better way to save space: Save ciphertext to a separate file and reference only the name
    file_to_read_stripped = file_to_read.split('/')
    raw_file_name = file_to_read_stripped[-1]
    ciphertext_file_path = f"./encrypted/{raw_file_name}_encrypted.enc"

    with open(ciphertext_file_path, 'w+') as f:
        f.write(ciphertext_b64.decode())

    # Write to CSV
    with open(FILE_NAME, 'a') as f:
        csv_ = csv.writer(f)
        csv_.writerow(
            [KDF, N, r, p, salt_b64.decode(), AEAD, nonce_b64.decode(),
             ciphertext_file_path, tag_b64.decode(), raw_file_name]  # Keep only the name
        )


def decrypt():
    """
    Decrypt the File
    1. User provide filename to decrypt with no path (e.g. 'hello.txt')
        * We store the encrypted file in format: ./encrypted/{filename}_encrypted.enc
        * So we retrieve it from: ./encrypted/hello.txt_encrypted.enc
    2. Find file name in the csv via the provided filename file and get that line
    3. Fetch N, r, p, salt
    4. User provide the password
    5. Reconstruct **key** with step 3) information
    6. Read ciphertext from step 1)
    7. Attempt a decryption and verification using the nonce, and tag
    """
    
    pass


def execute_mode(choice):
    if choice == 1:
        encrypt()
    else:
        decrypt()


def main():
    # Check if the authentication table exists
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

    execute_mode(choice)


if __name__ == '__main__':
    main()
