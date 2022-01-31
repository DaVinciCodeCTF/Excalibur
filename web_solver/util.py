try:
    import re
    import requests
except Exception as e:
    raise ImportError("finder.py -> " + str(e))

BACKUP_EXTENSIONS = [".backup", ".bck", ".old", ".save", ".bak", ".sav", "~", ".copy", ".old", ".tmp", ".txt",
                     ".back", ".bkp", ".bac", ".tar", ".gz", ".tar.gz", ".zip", ".rar"]


def get_domain(url):
    res = re.findall(r"(https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&=]*)",
                     url)
    if len(res) == 0:
        return None

    return res[0][0] + "/"


def get_get_parameters_from_url(url):
    return re.findall(r"[?&]([^= ]*)", url)


def remove_all_get_parameters_in_url(url):
    return re.findall(r"https?://[^?]*", url)[0]


def extract_url(text):
    urls = re.findall(r"(https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b"
                     r"[-a-zA-Z0-9()@:%_+.~#?&/=]*)", text)

    if len(urls) == 0:
        urls = re.findall(r"\w+\.\w+\.\w+\.\w+:[0-9]+", text)
        if len(urls) == 0:
            return None

    return urls[0][0]

def check_if_up(url):
    return requests.get(url).status_code == 200


def is_backup(url):
    backup = False
    for b in BACKUP_EXTENSIONS:
        if url.endswith(b):
            backup = True
    return backup


def is_successful_requests(response_code, raw_data_size, base_url):
    # Condition à changer !
    return (str(response_code)[0] == "2" and raw_data_size != 0) or \
           base_url[-9:] == ".404-page"
