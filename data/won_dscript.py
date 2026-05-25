'''
This script automatically downloads and formats
Won et al. data to be processed from its original
source:
    https://springernature.figshare.com/collections/EEG_Dataset_for_RSVP_and_P300_Speller_Brain-Computer_Interfaces/5769449/1

Please note Springer Nature may change its API any moment,
so this script may eventually stop working :$

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 22/05/2026
'''


import os
import re
import requests
from tqdm import tqdm

URL = "https://api.figshare.com/v2/collections/5769449/articles?page_size=70"
CHUNK_SIZE = 1024  # 1 KB
FILE_PATTERN = re.compile(".*\\.mat")

def extract_number(s):
    m = re.search(r'\d+', s)
    return int(m.group()) if m else None

if __name__ == "__main__":
    resp = requests.get(URL)

    for i in resp.json():
        isite = requests.get(i["url_public_api"]).json()
        files = isite["files"]
        for f in files:
            name = f["name"]
            dsite = f["download_url"]

            if re.match(FILE_PATTERN, name) is None:
                continue

            print(name)
            print("\t" + dsite)
            parentdir = f"OriginalDataWon/subject{extract_number(name)}/"
            os.makedirs(parentdir, exist_ok=True)

            with requests.get(dsite, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                with open(parentdir + name, "wb") as f, tqdm(
                
                    total=total, unit='B', unit_scale=True, unit_divisor=1024
                ) as bar:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        if not chunk:
                            continue
                        f.write(chunk)
                        bar.update(len(chunk))

                print("\tDownloaded successfully")
