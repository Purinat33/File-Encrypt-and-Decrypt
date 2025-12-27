import os
import base64
import csv
from pathlib import Path
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES


FILE_NAME = 'authenticate.csv'


# For storage
KDF = "scrypt"
N = 2**16
r = 8
p = 1

AEAD = 'AES-GCM'


def encrypt(file_path, pwd):
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
    # file_to_read = input("File Path: ")
    file_to_read = Path(file_path)

    if not file_to_read.exists():
        print("File doesn't exist. Exiting...")
        return

    # A better way to save space: Save ciphertext to a separate file and reference only the name
    encrypted_dir = Path("encrypted")
    encrypted_dir.mkdir(parents=True, exist_ok=True)

    raw_file_name = file_to_read.name  # just the basename, OS-safe
    ciphertext_file_path = (
        encrypted_dir / f"{raw_file_name}_encrypted.enc").resolve()
    # ciphertext_file_path is a Path object; use str(ciphertext_file_path) if needed

    # Check CSV for existing same filename
    with open(FILE_NAME, 'r', encoding='utf-8', newline='') as f:
        csv_file = csv.reader(f, delimiter=',')
        for row in csv_file:
            if not row or row[0] == "kdf":
                continue
            if str(file_to_read.resolve()) == row[-1]:
                print("File of that name already exists. Aborting ... ")
                return

    with open(file_to_read, 'rb') as f:
        file = f.read()

    # Do everything else
    # password_str = (input("Input Password here: "))
    password_str = pwd
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

    with open(ciphertext_file_path, 'w', encoding='utf-8') as f:
        f.write(ciphertext_b64.decode())

    # Write to CSV
    with open(FILE_NAME, 'a', newline='', encoding='utf-8') as f:
        csv_ = csv.writer(f)
        csv_.writerow(
            [KDF, N, r, p, salt_b64.decode(), AEAD, nonce_b64.decode(),
             str(ciphertext_file_path), tag_b64.decode(), str(file_to_read.resolve())]
        )
        
    return str(ciphertext_file_path)


def decrypt(file_path, pwd):
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
    ciphertext_file_path = Path(file_path)

    if not ciphertext_file_path.exists():
        print(f"Encrypted file not found: {ciphertext_file_path}")
        return

    # 2. https://stackoverflow.com/questions/26082360/python-searching-csv-and-return-entire-row
    matched_row = []
    with open(FILE_NAME, 'r', encoding='utf-8', newline='') as f:
        csv_file = csv.reader(f, delimiter=',')
        for row in csv_file:
            if not row or row[0] == "kdf":   # skip empty/header
                continue

            ciphertext_enc_in_csv = row[7]   # ciphertext_enc column
            csv_enc_path = Path(ciphertext_enc_in_csv)

            if (str(ciphertext_file_path.resolve()) == str(csv_enc_path.resolve())) or (ciphertext_file_path.name == csv_enc_path.name):
                matched_row = row
                break

    if not matched_row:
        print("No matching record found in authenticate.csv for that .enc file")
        return

    # 3. Unpack and fetch
    _, nn_raw, rr_raw, pp_raw, salt_b64, _, nonce_b64, ciphertext_enc_file_name, tag_b64, file_name = matched_row
    with open(ciphertext_enc_file_name, 'r', encoding='utf-8') as f:
        ciphertext_base64 = f.read().strip()

    nn = int(nn_raw)
    rr = int(rr_raw)
    pp = int(pp_raw)

    salt = base64.b64decode(salt_b64.encode())
    nonce = base64.b64decode(nonce_b64.encode())
    tag = base64.b64decode(tag_b64.encode())
    ciphertext = base64.b64decode(ciphertext_base64.encode())

    password_raw = pwd
    password = password_raw.encode()
    key = scrypt(password, salt, 16, N=nn, r=rr, p=pp)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Decryption
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
    except ValueError:
        raise ValueError("Key Error or Message is Corrupted")

    # Write plaintext
    decrypted_dir = Path('decrypted')
    decrypted_dir.mkdir(parents=True, exist_ok=True)

    out_name = Path(file_path).name
    out_path = (decrypted_dir / out_name).resolve()

    with open(out_path, 'wb') as f:
        f.write(plaintext)

    # Return output path so GUI can show it
    return str(out_path)
