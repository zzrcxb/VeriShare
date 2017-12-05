from pwShare.settings import DATA_PATH, MAX_FILE_SIZE, SITE_KEY

SITE_NAME = "verishare.org"

DOWNLOAD_TP_DFT = {
    'is_bot': False,
    'wrong': False,
}

INDEX_TP_DFT = dict(
    is_bot=False,
    site_key=SITE_KEY,
    greater_max_size=False,
    a_wrong=False,
    p_wrong=False,
)


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