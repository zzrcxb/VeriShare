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
