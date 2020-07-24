from smartphone import Smartphone
import os
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

if __name__ == '__main__':
    phone = Smartphone("Sony")
    print(phone.getName())

    #os.system("cmd /c adb shell getevent /dev/input/event7")


