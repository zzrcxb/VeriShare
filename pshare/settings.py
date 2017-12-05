from pwShare.settings import DATA_PATH, MAX_FILE_SIZE, SITE_KEY


MAX_PASSWD_GEN_TIME = 1

class REFER_PROTECTOR:
    TIME_LIMIT = 1 # min
    ACCESS_LIMIT = 3
    WHITE_LIST = [
        'verishare.org',
        'localhost',
        'apre'
    ]
    BLACK_LIST = []
    records = dict()