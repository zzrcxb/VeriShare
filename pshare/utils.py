import os

from pwShare.settings import DATA_PATH
from random import sample
from hashlib import sha1 as hash_method


def passwd_generator(length):
    charset = list(range(48, 58)) + list(range(65, 91)) + list(range(97, 122))
    passwd = ''
    for i in range(length):
        passwd += chr(sample(charset, 1)[0])
    return passwd


def save_file(file):
    h_obj = hash_method()
    list(map(h_obj.update, file.chunks()))
    hash_value = h_obj.hexdigest()
    fst = hash_value[:2]
    scd = hash_value[2:4]
    path = os.path.join(DATA_PATH, fst, scd)
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, hash_value), 'wb') as f:
        list(map(f.write, file.chunks()))

    return hash_value
