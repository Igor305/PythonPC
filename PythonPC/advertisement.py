import hashlib
import os

pathAdvertise = "/home/pi/PricePython/img/advertise"

def getListHash():
    try:
        listHash = "|"
        for root, dirs, files in os.walk(pathAdvertise):
                for filename in files:
                    hash =_md5(f"{pathAdvertise}/{filename}")
                    result = (f"|{filename};{hash}")

                    listHash += result

        if (len(listHash) > 2):
            listHash = listHash[2:]

    except Exception as err:
        print(err)

    return listHash

def _md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()