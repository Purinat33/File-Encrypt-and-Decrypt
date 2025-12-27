import os
import csv
import base64
from tkinter import *
from tkinter import ttk
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
    with open(FILE_NAME, 'w', newline='') as f:
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

    # A better way to save space: Save ciphertext to a separate file and reference only the name
    file_to_read_stripped = file_to_read.split('/')
    raw_file_name = file_to_read_stripped[-1]
    ciphertext_file_path = f"./encrypted/{raw_file_name}_encrypted.enc"

    # Check CSV for existing same filename
    f = open(FILE_NAME, 'r')
    csv_file = csv.reader(f, delimiter=',')
    for row in csv_file:
        if not row:
            continue
        if file_to_read == row[-1]:
            print("File of that name already exists. Aborting ... ")
            f.close()
            return
    f.close()

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

    with open(ciphertext_file_path, 'w+') as f:
        f.write(ciphertext_b64.decode())

    # Write to CSV
    with open(FILE_NAME, 'a', newline='') as f:
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

    # 1.
    file_to_read = input("File to decrypt (No path): ")
    ciphertext_file_path = f"./encrypted/{file_to_read}_encrypted.enc"

    if not os.path.exists(ciphertext_file_path):
        print(f"Encrypted file for {file_to_read} not found. Exiting")
        return

    # 2. https://stackoverflow.com/questions/26082360/python-searching-csv-and-return-entire-row
    f = open(FILE_NAME, 'r')
    csv_file = csv.reader(f, delimiter=',')
    matched_row = []
    for row in csv_file:
        if not row:
            continue
        if file_to_read == row[-1]:
            matched_row = row

    if matched_row == []:
        f.close()
        return
    f.close()

    # 3. Unpack and fetch

    _, nn_raw, rr_raw, pp_raw, salt_b64, _, nonce_b64, ciphertext_enc_file_name, tag_b64, file_name = matched_row
    with open(ciphertext_enc_file_name, 'r') as f:
        ciphertext_base64 = f.readline()

    nn = int(nn_raw)
    rr = int(rr_raw)
    pp = int(pp_raw)

    salt = base64.b64decode(salt_b64.encode())
    nonce = base64.b64decode(nonce_b64.encode())
    tag = base64.b64decode(tag_b64.encode())
    ciphertext = base64.b64decode(ciphertext_base64.encode())

    password_raw = input("Input Decryption Password: ")
    password = password_raw.encode()
    key = scrypt(password, salt, 16, N=nn, r=rr, p=pp)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Decryption
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
        print("Data is Authentic")
        # Write plaintext
        with open(f'./decrypted/{file_name}', 'wb') as f:
            f.write(plaintext)

        # Delete the encrypted file
        os.remove(ciphertext_file_path)

        # Delete the corresponding row from the csv
        # Save every row except the matching row
        # The opposite of the previous loop
        f = open(f"{FILE_NAME}", 'r')
        f_temp = open(f"{FILE_NAME}_temp.csv", 'w')
        csv_file = csv.reader(f, delimiter=',')
        temp_csv_file = csv.writer(f_temp, delimiter=',')

        for row in csv_file:
            if not row:
                continue
            if file_to_read == row[-1]:
                continue
            temp_csv_file.writerow(row)

        f.close()
        f_temp.close()

        # Now delete the old one and make the temp one the new one
        os.remove(FILE_NAME)
        os.rename(f"{FILE_NAME}_temp.csv", FILE_NAME)

    except ValueError:
        print("Key Error or Message is Corrupted")


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
    choice = 0
    
    
    
    execute_mode(choice)


if __name__ == '__main__':
    main()
