import subprocess
from smartphone import Smartphone as smartphone

def get_smartphones():
    smartphones = []
    sub = subprocess.Popen("platform-tools/adb devices", stdout=subprocess.PIPE)
    str = sub.communicate()[0].decode("utf-8").split("\n")
    sub.kill()
    for line in str:
        tmp = line.split("\t")
        if len(tmp) == 2:
            smartphones.append(smartphone(tmp[0], tmp[1].replace("\r", "")))
    return smartphones

