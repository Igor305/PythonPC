import pc_logging
import sensorDHT
import advertisement
import models
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from interface import Ui_MainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from ping3 import ping

import requests
import socket
import time
import sys
import os

# Create application
app = QtWidgets.QApplication(sys.argv)

# Init
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

# Logic

pathImg = "/home/pi/PricePython/"

# QThead For ProgressBar

class ProgressBarWorker(QThread):

    change_value = pyqtSignal(float)

    def __init__(ui):
        super(ProgressBarWorker,ui).__init__()
        ui.progress = 103
        ui.isFixCount = False
        ui.isStart = True

    def run(ui):
        while True:
            if(ui.isStart == True):
                ui.isStart = False
                ui.progress = 0

            if (ui.isFixCount == True):
                ui.isFixCount = False
                ui.progress = 103

            if (ui.progress > 0 and ui.progress < 105):
                time.sleep(0.08)
                ui.progress -= 1
                ui.change_value.emit(ui.progress)

            if (ui.progress == 0 or ui.progress == 105):
                ui.progress = 105
                advertising()
                time.sleep(1)

    def fixCount(ui):
        ui.isFixCount = True

# Get System Info

def getInfo():

    deviceName = socket.gethostname()
    ui.deviceName.setText("Имя устройства: " + deviceName)

    if (deviceName != "Avrora"):
        name = deviceName.split('-P')
        stock = name[0]
        ui.apiDeviceNumbers = name[1]

        stock = stock[1:len(stock)]

        while(stock.find('0') == 0):
            stock = stock[1:len(stock)]

        ui.apiStock = stock
        ui.apiDevice = deviceName

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ui.ip = s.getsockname()[0]
        ui.ipAddress.setText("Ip Address: " + str(ui.ip))

    except OSError:
        ui.ipAddress.setText("Ip Address: ")
        ui.statusEthernet = False

    ipAddressStatic = open("/etc/dhcpcd.conf", "r")
    for s in ipAddressStatic:
        if "static routers" in s:
            break
        if "static ip_address=" in s:
            ui.ipAddressStatic.setText("Стат. IP-адрес: " + s[19:-4])

    ui.version.setText("Версия: " + ui.actualVersion)

    numberOS = open("/etc/os-release","r")
    for s in numberOS:
        if "VERSION_ID=" in s:
            ui.numberOS.setText("Номер OS: " + s[12:-2])

    temperatureCPU = open("/sys/class/thermal/thermal_zone0/temp", "r")
    temperatureCPU = str(round(float(temperatureCPU.read())/1000))
    ui.temperatureCPU.setText("Температура CPU: " + temperatureCPU)

    serialNumbers = open("/proc/cpuinfo", "r")
    for s in serialNumbers:
        if "Serial" in s:
            ui.serial.setText("Serial: " + s[10:])

    sensorDHTdata = (0,0)
    while sensorDHTdata == (0,0) :
        sensorDHTdata = sensorDHT.getSensorData()

    ui.temperatureOut.setText(f"Температура внеш.: {sensorDHTdata[0]:.1f}")
    ui.humidity.setText(f"Влажность: {sensorDHTdata[1]:.1f}")

    if (os.path.exists("/etc/deviceCaseNum.conf")):
        numberBody = open("/etc/deviceCaseNum.conf", "r")
        ui.apiNumberBody = numberBody.read()
        ui.numberBody.setText("Номер корпуса: " + ui.apiNumberBody)
        numberBody.close()
    else:
        numberBody = open("/etc/deviceCaseNum.conf", "w")
        numberBody.write(ui.apiNumberBody)
        numberBody.close()

# Change File Config

def changeConfig():

    os.system("sudo hostnamectl set-hostname " + ui.actualDeviceName)

    newIp = open ("Ip.conf", "w")

    minitempIp = ui.tempIp[0 : ui.tempIp.rfind('.')]

    ip = "hostname\n" + " clientid\n" + " persistent\n" + " option rapid_commit\n" + " option domain_name_servers, domain_name, domain_search, host_name\n" + " option classless_static_routes\n" + " option ntp_servers\n" + " option interface_mtu\n" + " require dhcp_server_identifier\n" + "  slaac private\n" + " nohook lookup-hostname\n" + " profile static_eth0\n" + " static ip_address=" + ui.tempIp +"/24\n" + " static routers=" + minitempIp + "\n" + "static domain_name_servers=172.17.64.24 172.17.64.24\n" + " interface eth0\n" + " fallback static_eth0hostname\n"

    newIp.write(ip)
    newIp.close()

    Ip = open ("/etc/dhcpcd.conf", "w")
    Ip.write(ip)
    Ip.close()

    nBody = open ("/etc/deviceCaseNum.conf", "w")
    nBody.write(ui.tempNumberBody)
    nBody.close()

    nBody = open ("deviceCaseNum.conf", "w")
    nBody.write(ui.tempNumberBody)
    nBody.close()

# BarcodeReset

def barcodeReset():

    ui.actualDeviceName = "Avrora"
    os.system("sudo hostnamectl set-hostname " + ui.actualDeviceName)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]

    except OSError:
        ui.ipAddress.setText("Ip Address: ")
        ui.statusEthernet = False

    ui.tempIp = ip

    newIp = open ("Ip.conf", "w")

    minitempIp = ui.tempIp[0 : ui.tempIp.rfind('.')]

    ip = "hostname\n" + " clientid\n" + " persistent\n" + " option rapid_commit\n" + " option domain_name_servers, domain_name, domain_search, host_name\n" + " option classless_static_routes\n" + " option ntp_servers\n" + " option interface_mtu\n" + " require dhcp_server_identifier\n" + "  slaac private\n" + " nohook lookup-hostname\n" + " profile static_eth0\n" + " static ip_address=" + ui.tempIp +"/24\n" + " static routers=" + minitempIp + "\n" + "static domain_name_servers=172.17.64.24 172.17.64.24\n" + " interface eth0\n" + " fallback static_eth0hostname\n"

    newIp.write(ip)
    newIp.close()

    Ip = open ("/etc/dhcpcd.conf", "w")
    Ip.write(ip)
    Ip.close()

    ui.tempNumberBody = "0000"

    nBody = open ("/etc/deviceCaseNum.conf", "w")
    nBody.write(ui.tempNumberBody)
    nBody.close()

    nBody = open ("deviceCaseNum.conf", "w")
    nBody.write(ui.tempNumberBody)
    nBody.close()

# When barcode textChanged

def sync_lineEdit():
    ui.progressBar.setValue(105)
    ui.countRel = 0
    ui.progressBarWorker.fixCount()

    hideForms()

    ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/manualInputBc_dark.png"))
    ui.barcode.setGeometry(QtCore.QRect(40, 245, 800, 70))

    ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))

# When Press Enter

def barcodePressedEnter():

    if (ui.barcode.text() != ""):
        hideForms()

    if (ui.isLineEdit):
        ui.source = 1
    if (ui.isLineEdit == False):
        ui.source = 2

    ui.isLineEdit = False

    ui.countRel = 0
    ui.barcodeCopy = ''
    ui.progressBarWorker.fixCount()
    barcode = ui.barcode.text()

    # Mode Config

    if (ui.statusConfig == 1):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.configTitle.setText("Настройки")

        if (int(barcode) < 0 or int(barcode) == 100 ):
            ui.configText.setText("Отскануйте номер магазину")
            ui.configValue.setText("Номер магазину повинен бути більше 0, не 100")
            ui.configValue.setGeometry(QtCore.QRect(0, 350, 1024, 100))
        else:
            ui.configText.setText("Отскануйте номер прайсчекера")
            ui.statusConfig = 2
            ui.tempNumberShop = barcode

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (ui.statusConfig == 2):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))

        ui.configTitle.setText("Настройки")

        if (int(barcode) < 0):
            ui.configText.setText("Отскануйте номер прайсчекера")
            ui.configValue.setText("Номер прайсчекера повинен бути більше 0")
            ui.configValue.setGeometry(QtCore.QRect(0, 350, 1024, 100))
        else:
            ui.configText.setText("Отскануйте IP-адрес")
            ui.statusConfig = 3
            ui.tempNumberPC = barcode

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (ui.statusConfig == 3):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.statusConfig = 4
        ui.configTitle.setText("Настройки")
        ui.configText.setText("Отскануйте номер корпуса")

        ui.tempIp = barcode

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (ui.statusConfig == 4):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.statusConfig = 5
        ui.configTitle.setText("Настройки")
        ui.configText.setText("Збережіть зміни або відмініть")

        ui.tempNumberBody = barcode

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (ui.statusConfig == 5):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.configTitle.setText("Настройки")

        if (barcode == "772211003"):
            ui.configText.setText("Настройки збережені")
            ui.statusConfig = 0
            actualNumberShop = ""
            if (int(ui.tempNumberShop) < 10):
                actualNumberShop = "A000" + str(ui.tempNumberShop)
            elif (int(ui.tempNumberShop) >= 10 and int(ui.tempNumberShop) < 100):
                actualNumberShop = "A00" + str(ui.tempNumberShop)
            elif (int(ui.tempNumberShop) >= 100 and int(ui.tempNumberShop) < 1000):
                actualNumberShop = "A0" + str(ui.tempNumberShop)
            elif (int(ui.tempNumberShop) >= 1000):
                actualNumberShop = "A" + str(ui.tempNumberShop)

            ui.actualDeviceName = actualNumberShop + "-P" + ui.tempNumberPC

            changeConfig()
            pc_logging.writeInfo("ChangeConfig | Store number:"+ ui.tempNumberShop + " | Price checker number:" + ui.tempNumberPC + " | IP address:" + ui.tempIp + " | Body number:" + ui.tempNumberBody)
            os.system("sudo reboot")

        elif (barcode == "772211004"):
            ui.configText.setText("Настройки відмінені")
            ui.statusConfig = 0
            ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))
        else:
            ui.configText.setText("Збережіть зміни або відмініть")
            ui.configValue.setText("Неправильний штрихкод")
            ui.configValue.setGeometry(QtCore.QRect(0, 350, 1024, 100))

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (barcode == ""):
        return

    # Mode viewing info

    elif (barcode == "772211001"):
        getInfo()
        ui.barcode.setText("")
        ui.statusConfig = -1
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.deviceName.setGeometry(QtCore.QRect(70, 50, 700, 30))
        ui.ipAddress.setGeometry(QtCore.QRect(70, 160, 700, 30))
        ui.ipAddressStatic.setGeometry(QtCore.QRect(70, 270, 700, 30))
        ui.version.setGeometry(QtCore.QRect(70, 380, 700, 30))
        ui.numberOS.setGeometry(QtCore.QRect(70, 490, 700, 30))
        ui.temperatureCPU.setGeometry(QtCore.QRect(600, 50, 700, 30))
        ui.serial.setGeometry(QtCore.QRect(600, 160, 700, 30))
        ui.temperatureOut.setGeometry(QtCore.QRect(600, 270, 700, 30))
        ui.humidity.setGeometry(QtCore.QRect(600, 380, 700, 30))
        ui.numberBody.setGeometry(QtCore.QRect(600, 490, 700, 30))

    # Mode Config

    elif (barcode == "772211002"):
        ui.statusConfig = 1
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))

        ui.configTitle.setText("Настройки")
        ui.configText.setText("Отскануйте номер магазину")

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    # Mode Reset

    elif (barcode == "BarcodeReset"):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))

        barcodeReset()
        pc_logging.writeInfo("BarcodeReset | Store number:235 | Price checker number:DeviceNumber | Body number:0000")
        os.system("sudo reboot")

    # Check Employment

    elif (barcode.find("ent") == False and ui.statusEthernet == True and ui.failConnenct == False):
        try:
            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))
            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/employeeInfo.png"))

            emp = 'http://' + ui.apiAddress + '/emp_reg?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode=' + barcode + '&source=' + str(ui.source)

            try:
                response = requests.get(emp, timeout = 0.5)
                pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

            except Exception:
                changeMpce()
                emp = 'http://' + ui.apiAddress + '/emp_reg?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode=' + barcode + '&source=' + str(ui.source)
                response = requests.get(emp)
                pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

            response = response.json()

            name = response["Name"]
            state = response["State"]

            if (name == None):
                raise Exception('name == None')

            ui.nameEmp.setWordWrap(True)
            ui.nameEmp.setText(name)

            if(state == 0):
                ui.statusEmp.setText("кінець")
            elif(state == 1):
                ui.statusEmp.setText("початок")

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            ui.timeEmp.setText("час зафіксовано о " + current_time)

            ui.nameEmp.setGeometry(QtCore.QRect(0, 150, 1024, 200))
            ##ui.statusEmp.setGeometry(QtCore.QRect(0, 310, 1024, 200))
            ui.timeEmp.setGeometry(QtCore.QRect(0, 380, 1024, 200))

        except Exception:

            ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))
            ui.barcodeText.setGeometry(QtCore.QRect(40, 550, 0, 0))
            ui.barcodeValue.setGeometry(QtCore.QRect(80, 550, 0, 0))
            ui.amountText.setGeometry(QtCore.QRect(290, 550, 0, 0))
            ui.amountValue.setGeometry(QtCore.QRect(370, 550, 0, 0))
            ui.codeValue.setGeometry(QtCore.QRect(460, 550, 0, 0))
            ui.name.setGeometry(QtCore.QRect(80, 320, 0, 0))
            ui.price.setGeometry(QtCore.QRect(250, 200, 0, 0))

            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/merchandiserError.png"))

    else:

        # Check Barcode

        if ui.statusEthernet == False or ui.failConnenct == True:

            if ui.statusEthernet == False:

                hideForms()
                ui.barcode.setText("")
                ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/error_server_dark.jpg"))

            elif ui.failConnenct == True:

                hideForms()
                ui.barcode.setText("")
                ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/Offline_dark_2.jpg"))

        elif (len(barcode) > 6):

            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/productBack_dark.jpg"))
            art = 'http://' + ui.apiAddress + '/artex?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode=' + barcode + '&source=' + str(ui.source)
            km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode=' + barcode + '&source=' + str(ui.source)
            rel = 'http://' + ui.apiAddress + '/rel?key='+ ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode=' + barcode + '&source=' + str(ui.source)
            getProductInfo(art, km, rel, barcode)

        # Check Code

        elif(len(barcode) <= 6):

            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/productBack_dark.jpg"))
            art = 'http://' + ui.apiAddress + '/artex?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
            km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
            rel = 'http://' + ui.apiAddress + '/rel?key='+ ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
            getProductInfo(art, km, rel, barcode)

# Info For product

def getProductInfo(art, km, rel, barcode):

        # Get related products
        try:
            try:
                response = requests.get(rel, timeout = 0.5)
                pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

            except Exception:
                changeMpce()
                art = 'http://' + ui.apiAddress + '/artex?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
                km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
                rel = 'http://' + ui.apiAddress + '/rel?key='+ ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
                response = requests.get(rel)
                pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

            response = response.json()

            if(len(response) > 0):
                ui.countRel = len(response)
                ui.rels = response
                ui.rels.reverse()

            getProduct(art,km,barcode)

        except Exception:
            try:
                getCard(barcode)

            except Exception:

                hideForms()
                ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/merchandiserError.png"))
                ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))

# Get info product

def getProduct(art,km,barcode):
    ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))

    try:
        response = requests.post(art, timeout = 0.5)
        pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

    except Exception:
        changeMpce()
        art = 'http://' + ui.apiAddress + '/artex?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
        km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
        response = requests.get(art)
        pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

    response = response.json()

    barcode = response["Barcode"]
    code = response["Id"]
    name = response["Name"]
    price = response["Price"]
    priceOld = response["PriceOldSale"]
    priceOldBonus = response["PriceOldBonus"]
    bonusDateFrom = response["BonusDateFrom"]
    bonusDateTo = response["BonusDateTo"]
    qty = int(response["Qty"])

    if (name == None):
        raise Exception('name == None')

    strBarcode = strCode = strQty = strKm = ""

    if (barcode != None) : strBarcode = str(barcode)
    if (code != None) : strCode = str(code)
    if (qty != None) : strQty= str(qty)

    priceStr = str("%.0f" % int(price))
    penny = str("%.0f" % ((price%1) * 100))

    if (penny == "0"):
        penny = "00"

    try:
        km = getKM(km, barcode)
        if (km != None): strKm = str(km)
    except:
        return

    ui.barcodeText.setText("Ш/К:")
    ui.barcodeValue.setText(strBarcode)
    ui.amountText.setText("Кількість:")
    ui.amountValue.setText(strQty)
    ui.codeValue.setText(f"Код:{strCode}")
    ui.keyKTValue.setText(f"Код КТ:{strKm}")
    ui.name.setText(name)
    ui.price.setText(priceStr)
    ui.pricePenny.setText(penny)
    ui.priceCurrency.setText("грн")
    ui.barcodeText.setGeometry(QtCore.QRect(35, 550, 80, 20))
    ui.barcodeValue.setGeometry(QtCore.QRect(90, 550, 200, 20))
    ui.amountText.setGeometry(QtCore.QRect(35, 525, 100, 20))
    ui.amountValue.setGeometry(QtCore.QRect(140, 525, 80, 20))
    ui.codeValue.setGeometry(QtCore.QRect(345, 525, 150, 20))
    ui.keyKTValue.setGeometry(QtCore.QRect(345, 550, 150, 20))
    font = QtGui.QFont()
    font.setPointSize(26)
    font.setBold(False)
    font.setWeight(50)
    ui.name.setFont(font)
    ui.name.setWordWrap(True)
    ui.name.setGeometry(QtCore.QRect(30, 380, 450, 120))
    font.setPointSize(130)
    font.setBold(True)
    font.setWeight(65)
    ui.price.setFont(font)
    font.setPointSize(45)
    font.setBold(True)
    font.setWeight(75)
    ui.pricePenny.setFont(font)
    font.setPointSize(45)
    ui.priceCurrency.setFont(font)
    ui.priceCurrency.setStyleSheet("color: rgb(255, 238, 0);")

    ui.price.setGeometry(QtCore.QRect(0, 120, 370, 300))
    ui.pricePenny.setGeometry(QtCore.QRect(380, 100, 200, 150))
    ui.priceCurrency.setGeometry(QtCore.QRect(380, 180, 200, 150))

    if (priceOldBonus > 0.0 and priceOldBonus != None):

        priceOldStr = str("%.0f" % int(priceOldBonus))
        pennyOld = str("%.0f" % ((priceOldBonus%1) * 100))

        if (pennyOld == "0"):
            pennyOld = "00"

        if (bonusDateFrom != None):
            dateFrom = datetime.strptime(bonusDateFrom, '%Y-%m-%d %H:%M:%S')
            bonusDateFrom = dateFrom.strftime("%d.%m")

        if (bonusDateTo != None):
            dateTo = datetime.strptime(bonusDateTo, '%Y-%m-%d %H:%M:%S')
            bonusDateTo = dateTo.strftime("%d.%m")

        if (bonusDateFrom == None and bonusDateTo == None) : ui.stockFromTo.setText("")
        elif (bonusDateFrom != None and bonusDateTo == None) : ui.stockFromTo.setText(f"з {bonusDateFrom}")
        elif (bonusDateFrom == None and bonusDateTo != None) : ui.stockFromTo.setText(f"по {bonusDateTo}")
        else : ui.stockFromTo.setText(f"з {bonusDateFrom} по {bonusDateTo}")

        ui.stockName.setText("АКЦІЯ")
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(45)
        ui.stockName.setFont(font)
        ui.stockName.setGeometry(QtCore.QRect(20, 20, 300, 80))
        font.setBold(True)
        font.setPointSize(18)
        ui.stockFromTo.setFont(font)
        ui.stockFromTo.setGeometry(QtCore.QRect(20, 80, 300, 70))

        formBonus(priceOldStr,pennyOld)

        ui.lineRed.setPixmap(QtGui.QPixmap(pathImg + "img/resources/lineRed.svg"))
        if (priceOldBonus >= 100.0): ui.lineRed.setGeometry(QtCore.QRect(275, 15, 210, 120))
        elif (priceOldBonus < 100.0 and priceOldBonus >= 10.0): ui.lineRed.setGeometry(QtCore.QRect(310, 20, 210, 100))
        else : ui.lineRed.setGeometry(QtCore.QRect(390, 20, 120, 80))

    elif (priceOld > 0.0 and priceOld != None):

        priceOldStr = str("%.0f" % int(priceOld))
        pennyOld = str("%.0f" % ((priceOld%1) * 100))

        if (pennyOld == "0"):
            pennyOld = "00"

        formBonus(priceOldStr,pennyOld)

        ui.lineWhite.setPixmap(QtGui.QPixmap(pathImg + "img/resources/lineWhite.svg"))
        if (priceOld >= 100.0): ui.lineWhite.setGeometry(QtCore.QRect(275, 15, 210, 120))
        elif (priceOld < 100.0 and priceOld >= 10.0): ui.lineWhite.setGeometry(QtCore.QRect(310, 20, 210, 100))
        else : ui.lineWhite.setGeometry(QtCore.QRect(390, 20, 120, 80))

    try:
        path = getImage(str(code))
        ui.productImage.setStyleSheet(f"border-radius:15px; border-image: url({path}img/temp/temp_image) 0 0 0 0 stretch stretch;")
        ui.productImage.setGeometry(QtCore.QRect(530, 25, 470, 545))

    except Exception:
        ui.productImage.setPixmap(QtGui.QPixmap(pathImg + "img/resources/noImage.jpg"))

def formBonus(priceOldStr,pennyOld):

    font = QtGui.QFont()
    ui.priceOld.setText(priceOldStr)
    font.setBold(True)
    font.setPointSize(65)
    ui.priceOld.setFont(font)
    ui.priceOld.setGeometry(QtCore.QRect(150, 30, 300, 100))
    ui.priceOldPenny.setText(pennyOld)
    font.setPointSize(28)
    ui.priceOldPenny.setFont(font)
    ui.priceOldPenny.setGeometry(QtCore.QRect(450, 30, 200, 60))
    ui.priceOldCurrency.setText("грн")
    font.setPointSize(28)
    ui.priceOldCurrency.setFont(font)
    ui.priceOldCurrency.setGeometry(QtCore.QRect(450, 30, 200, 140))
    font.setPointSize(120)
    font.setBold(True)
    font.setWeight(65)
    ui.price.setFont(font)
    ui.price.setGeometry(QtCore.QRect(0, 170, 370, 300))
    font.setPointSize(45)
    font.setBold(True)
    font.setWeight(75)
    ui.pricePenny.setFont(font)
    ui.pricePenny.setGeometry(QtCore.QRect(370, 150, 200, 150))
    font.setPointSize(45)
    ui.priceCurrency.setFont(font)
    ui.priceCurrency.setGeometry(QtCore.QRect(370, 225, 200, 150))

# Get KM
def getKM(km, barcode):

    try:
        response = requests.get(km, timeout = 0.5)
        pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

    except Exception:
        changeMpce()
        km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
        response = requests.get(km)
        pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

    response = response.json()

    responseKM = response["KM"]
    km = str(responseKM["Id"])

    return(km)

# Get image product

def getImage(code):

    image  = 'http://' + ui.apiAddress + '/img?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + code + '&sticker=1&source=' + str(ui.source)

    try:
        responseImage = requests.get(image, timeout = 0.5)
        pc_logging.writeResponseToLog(responseImage.url,responseImage.elapsed.total_seconds())

    except Exception:
        changeMpce()
        image  = 'http://' + ui.apiAddress + '/img?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + code + '&sticker=1&source=' + str(ui.source)
        responseImage = requests.get(image)
        pc_logging.writeResponseToLog(responseImage.url,responseImage.elapsed.total_seconds())

    file = open(pathImg + "img/temp/temp_image", "wb")
    file.write(responseImage.content)
    file.close()

    return pathImg

# Get Card Info

def getCard(barcode):

    card = 'http://' + ui.apiAddress + '/card?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&card=' + barcode + '&source=' + str(ui.source)

    try:
        responseCard = requests.get(card, timeout = 0.5)
        pc_logging.writeResponseToLog(responseCard.url,responseCard.elapsed.total_seconds())

    except Exception:
        changeMpce()
        card = 'http://' + ui.apiAddress + '/card?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&card=' + barcode + '&source=' + str(ui.source)
        responseCard = requests.get(card)
        pc_logging.writeResponseToLog(responseCard.url,responseCard.elapsed.total_seconds())

    responseCard = responseCard.json()

    bonus = responseCard["Bonus"]
    cash = int(bonus / 100)
    penny = bonus % 100

    name = responseCard["Name"]
    ui.nameCard.setText(name + ', на Вашому рахунку')
    ui.bonus.setText(str(cash) + " " + str(penny))

    ui.nameCard.setGeometry(QtCore.QRect(120, 180, 800, 60))
    ui.bonus.setGeometry(QtCore.QRect(0, 210, 1024, 400))

    ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/dCardBack_dark.jpg"))

# Related products

def related():

    try:
        hideForms()

        font = QtGui.QFont()
        font.setPointSize(20)
        ui.name.setFont(font)
        ui.name.setGeometry(QtCore.QRect(530, 470, 220, 95))
        font.setPointSize(80)
        font.setBold(True)
        ui.price.setFont(font)
        ui.price.setGeometry(QtCore.QRect(725, 455, 220, 120))
        font.setPointSize(25)
        font.setBold(False)
        ui.pricePenny.setFont(font)
        ui.pricePenny.setGeometry(QtCore.QRect(955, 390, 200, 200))
        font.setPointSize(21)
        ui.priceCurrency.setStyleSheet("color:rgb(255, 255, 255)")
        ui.priceCurrency.setFont(font)
        ui.priceCurrency.setGeometry(QtCore.QRect(950, 445, 200, 200))
        ui.productImage.setGeometry(QtCore.QRect(529, 29, 470, 375))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/companionProdBcDark.png"))
        ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))
        ui.barcodeCopy = ''
        ui.progressBarWorker.fixCount()

        code = str(ui.rels[ui.countRel-1])

        art = 'http://' + ui.apiAddress + '/art?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + code +'&source=3'
        km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + code +'&source=3'

        km = getKM(km,code)

        try:
            response = requests.get(art, timeout = 0.5)
            pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

        except Exception:
            changeMpce()
            art = 'http://' + ui.apiAddress + '/art?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + code +'&source=3'
            response = requests.get(art)
            pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())

        response = response.json()

        name = response["Name"]
        price = response["Price"]

        priceStr = str("%.0f" % price)
        penny = str("%.0f" % ((price%1) * 100))

        if (penny == "0"):
            penny = "00"

        font.setPointSize(20)
        ui.nameRel.setFont(font)
        ui.nameRel.setText(name)
        ui.nameRel.setWordWrap(True)
        ui.nameRel.setGeometry(QtCore.QRect(30, 470, 220, 95))
        font.setPointSize(80)
        font.setBold(True)
        ui.priceRel.setFont(font)
        ui.priceRel.setText(priceStr)
        ui.priceRel.setGeometry(QtCore.QRect(230, 455, 220, 120))
        font.setPointSize(25)
        font.setBold(False)
        ui.pricePennyRel.setFont(font)
        ui.pricePennyRel.setText(penny)
        ui.pricePennyRel.setGeometry(QtCore.QRect(460, 390, 200, 200))
        font.setPointSize(21)
        ui.priceCurrencyRel.setStyleSheet("color:rgb(255, 255, 255)")
        ui.priceCurrencyRel.setFont(font)
        ui.priceCurrencyRel.setText('грн')
        ui.priceCurrencyRel.setGeometry(QtCore.QRect(455, 445, 200, 200))
        font.setPointSize(21)
        font.setBold(True)
        ui.rel.setFont(font)
        ui.rel.setText("КУПУЙ РАЗОМ")
        ui.rel.setGeometry(QtCore.QRect(393, 385, 400, 100))

        try:
            path = getImage(code)

            ui.productImageRel.setStyleSheet(f"border-radius:15px; border-image: url({path}img/temp/temp_image) 0 0 0 0 stretch stretch;")
            ui.productImageRel.setGeometry(QtCore.QRect(29, 29, 470, 375))

        except Exception:
            ui.productImage.setPixmap(QtGui.QPixmap(pathImg + "img/resources/noImage.jpg"))

        ui.countRel -= 1

    except Exception:
        ui.countRel = 0

# Hide all

def hideForms():

    ui.barcode.setGeometry(QtCore.QRect(70, 50, 0, 0))
    ui.progressBar.setGeometry(QtCore.QRect(70, 50, 0, 0))
    ui.deviceName.setGeometry(QtCore.QRect(70, 50, 0, 0))
    ui.ipAddress.setGeometry(QtCore.QRect(70, 160, 0, 0))
    ui.ipAddressStatic.setGeometry(QtCore.QRect(70, 270, 0, 0))
    ui.version.setGeometry(QtCore.QRect(70, 380, 0, 0))
    ui.numberOS.setGeometry(QtCore.QRect(70, 490, 0, 0))
    ui.temperatureCPU.setGeometry(QtCore.QRect(600, 50, 0, 0))
    ui.serial.setGeometry(QtCore.QRect(600, 160, 0, 0))
    ui.temperatureOut.setGeometry(QtCore.QRect(600, 270, 0, 0))
    ui.humidity.setGeometry(QtCore.QRect(600, 380, 0, 0))
    ui.numberBody.setGeometry(QtCore.QRect(600, 490, 0, 0))
    ui.configTitle.setGeometry(QtCore.QRect(0, 60, 0, 0))
    ui.configText.setGeometry(QtCore.QRect(0, 250, 0, 0))
    ui.configValue.setGeometry(QtCore.QRect(0, 60, 0, 0))

    ui.barcodeText.setGeometry(QtCore.QRect(40, 550, 0, 0))
    ui.barcodeValue.setGeometry(QtCore.QRect(80, 550, 0, 0))
    ui.amountText.setGeometry(QtCore.QRect(290, 550, 0, 0))
    ui.amountValue.setGeometry(QtCore.QRect(380, 550, 0, 0))
    ui.codeValue.setGeometry(QtCore.QRect(460, 550, 0, 0))
    ui.name.setGeometry(QtCore.QRect(80, 320, 0, 0))
    ui.price.setGeometry(QtCore.QRect(250, 200, 0, 0))
    ui.nameCard.setGeometry(QtCore.QRect(120, 180, 0, 0))
    ui.bonus.setGeometry(QtCore.QRect(0, 210, 0, 0))
    ui.nameEmp.setGeometry(QtCore.QRect(0, 160, 0, 0))
    ui.statusEmp.setGeometry(QtCore.QRect(0, 320, 0, 0))
    ui.timeEmp.setGeometry(QtCore.QRect(0, 400, 0, 0))
    ui.productImage.setGeometry(QtCore.QRect(530, 30, 0, 0))
    ui.pricePenny.setGeometry(QtCore.QRect(380, 120, 0, 0))
    ui.priceCurrency.setGeometry(QtCore.QRect(380, 190, 0, 0))
    ui.priceOld.setGeometry(QtCore.QRect(180, 30, 0, 0))
    ui.priceOldPenny.setGeometry(QtCore.QRect(440, 30, 0, 0))
    ui.priceOldCurrency.setGeometry(QtCore.QRect(430, 30, 0, 0))
    ui.keyKTValue.setGeometry(QtCore.QRect(430, 30, 0, 0))
    ui.productImageRel.setGeometry(QtCore.QRect(0, 0, 0, 0))
    ui.nameRel.setGeometry(QtCore.QRect(0, 0, 0, 0))
    ui.priceRel.setGeometry(QtCore.QRect(0, 0, 0, 0))
    ui.pricePennyRel.setGeometry(QtCore.QRect(0, 0, 0, 0))
    ui.priceCurrencyRel.setGeometry(QtCore.QRect(0, 0, 0, 0))
    ui.rel.setGeometry(QtCore.QRect(0, 0, 0, 0))
    ui.stockName.setGeometry(QtCore.QRect(0, 0, 0 ,0))
    ui.stockFromTo.setGeometry(QtCore.QRect(0, 0, 0 ,0))
    ui.lineRed.setGeometry(QtCore.QRect(0, 0, 0, 0))
    ui.lineWhite.setGeometry(QtCore.QRect(0, 0, 0, 0))

def checkEthernet():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ui.statusEthernet = True

    except OSError:

        ui.statusEthernet = False
        barcode = ui.barcode.text()

        if (ui.progressBar.value() < 1):
            ui.barcode.setText("")
            ui.statusConfig = 0

        if (ui.statusConfig == 0 and len(barcode) < 1):

            hideForms()

            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/error_server_dark.jpg"))

            pc_logging.writeError("Internet connection error")

def checkPing():

    # Confirm API server
    mpce03 = "mpce03.avrora.lan"
    mpce04 = "mpce04.avrora.lan"

    pingMpce03 = ping(mpce03)
    pingMpce04 = ping(mpce04)

    ui.failConnenct = False

    if ui.statusEthernet == True:

        barcode = ui.barcode.text()

        if pingMpce03 == None and pingMpce04 == None or pingMpce03 == False and pingMpce04 == False:
            ui.failConnenct = True

        elif pingMpce04 == False or pingMpce04 == None:
            ui.apiAddress = mpce03

        elif pingMpce03 == False or pingMpce03 ==  None:
            ui.apiAddress = mpce04

        elif pingMpce03 < pingMpce04:
            ui.apiAddress = mpce03

        elif pingMpce04 < pingMpce03:
            ui.apiAddress = mpce04

        if (ui.failConnenct == True and ui.statusConfig == 0 and len(barcode) < 1):

            hideForms()

            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/Offline_dark_2.jpg"))

            pc_logging.writeError("Servers connection error")

def changeMpce():

    if (ui.apiAddress == "mpce03.avrora.lan"):
        ui.apiAddress = "mpce04.avrora.lan"
        return

    if (ui.apiAddress == "mpce04.avrora.lan"):
        ui.apiAddress = "mpce03.avrora.lan"
        return

def checkInput():

    length = len(ui.barcode.text()) - len(ui.barcodeCopy)
    ui.barcodeCopy = ui.barcode.text()

    if (length <= 4 and length > 0):
        ui.isLineEdit = True
        sync_lineEdit()

def advertising ():

    if (ui.statusConfig <= 0 and ui.countRel < 1):

        if (ui.failConnenct == False and ui.statusEthernet == True ):

            ui.barcode.setText("")
            hideForms()
            try:
                for root, dirs, files in os.walk(pathImg + "img/advertise"):
                        for filename in files:
                            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/advertise/" + files[ui.countAdvertising]))

                if( ui.secondAdvertising == 8):
                    ui.secondAdvertising = 0
                    ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/advertise/" + files[ui.countAdvertising]))
                    ui.countAdvertising +=1

                if (ui.countAdvertising > len(files)-1 ):
                    ui.countAdvertising = 0

                ui.secondAdvertising += 1

            except:
                ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/default_dark.jpg"))

    if (ui.countRel > 0):
        related()

def backspace():

    length = len(ui.barcode.text()) - len(ui.barcodeCopy)

    if (ui.barcode.text() == "" and ui.statusConfig <= 0):
        ui.isLineEdit = False
        advertising()
        return

    if (ui.barcode.text() == "" and ui.statusConfig == 1):
        hideForms()
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.configTitle.setText("Настройки")
        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setText("Отскануйте номер магазину")
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))
        return

    if (ui.barcode.text() == "" and ui.statusConfig == 2):
        hideForms()
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.configTitle.setText("Настройки")
        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setText("Отскануйте номер прайсчекера")
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))
        return

    if (ui.barcode.text() == "" and ui.statusConfig == 3):
        hideForms()
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.configTitle.setText("Настройки")
        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setText("Отскануйте IP-адрес")
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))
        return

    if (ui.barcode.text() == "" and ui.statusConfig == 4):
        hideForms()
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.configTitle.setText("Настройки")
        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setText("Отскануйте номер корпуса")
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))
        return

    if (ui.barcode.text() == "" and ui.statusConfig == 5):
        hideForms()
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/systemInfo_dark.jpg"))
        ui.configTitle.setText("Настройки")
        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setText("Збережіть зміни або відмініть")
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))
        return

def checkTemperature():
    temperatureCPU = open("/sys/class/thermal/thermal_zone0/temp", "r")
    temperatureCPU = str(round(float(temperatureCPU.read())/1000))

    sensorDHT.getTemperatureAndHumidity(ui.apiStock,ui.apiDeviceNumbers)
    sensorDHT.getTemperatureCPU(ui.apiStock, ui.apiDeviceNumbers,temperatureCPU)

def requestInfoPC():

    try:
        netbiosname1 = socket.gethostname()
        version1 = str(subprocess.check_output('sudo uname -r', shell=True,  universal_newlines=True)).rstrip()
        version1 = version1.replace('+','[+]')
        uptimehrs = str(subprocess.check_output('cat /proc/uptime', shell=True,  universal_newlines=True)).rstrip()
        uptimehrs = str(round(float((uptimehrs.split(' ')[0]))))
        serialno1 = str(subprocess.check_output('sudo cat /proc/cpuinfo | grep Serial | cut -d " " -f 2', shell=True,  universal_newlines=True)).rstrip()
        temperatureCPU = open("/sys/class/thermal/thermal_zone0/temp", "r")
        tempcpu = str(float(temperatureCPU.read())/1000)
        memory =  str(subprocess.check_output("free | awk NR==2'{print $7}'", shell=True,  universal_newlines=True)).rstrip()

        deviceInfo = f'http://{ui.apiAddress}/device_info?key={ui.apiKey}&stock={ui.apiStock}&device={ui.apiDevice}&netbiosname1={netbiosname1}&version1={version1}&version2={ui.actualVersion}&uptimehrs={uptimehrs}&serialno1={serialno1}&serialno2={ui.apiNumberBody}&tempcpu={tempcpu}&memory={memory}'
        print(deviceInfo)
        response = requests.get(deviceInfo, timeout = 1)
        print(response)
        print(response.json())

    except Exception as err:
        print(err)

def checkUpdate():
    try:
        requestInfoPC()
        imageHashs = advertisement.getListHash()
        infoModel = models.InfoModel(ui.actualVersion,ui.ip,ui.apiStock,ui.apiDevice,ui.apiNumberBody,imageHashs)
        post = requests.post("http://price-py-service.avrora.lan/api/price/info", json=infoModel.__dict__)

        pc_logging.writeInfo(f"Check Update {post}")

    except Exception as err:
        print(err)

def timerCheckInput():

    ui.timerCheckInput = QtCore.QTimer()
    ui.timerCheckInput.timeout.connect(checkInput)
    ui.timerCheckInput.start(200)

def timerCheckEthernet():

    ui.timerCheckEthernet = QtCore.QTimer()
    ui.timerCheckEthernet.timeout.connect(checkEthernet)
    ui.timerCheckEthernet.start(1000)

def timerCheckPing():

    checkPing()
    ui.timerCheckPing = QtCore.QTimer()
    ui.timerCheckPing.timeout.connect(checkPing)
    ui.timerCheckPing.start(60000)

def timerTemperatureAndHumidity():
    checkTemperature()
    ui.timerTemperatureAndHumidity = QtCore.QTimer()
    ui.timerTemperatureAndHumidity.timeout.connect(checkTemperature)
    ui.timerTemperatureAndHumidity.start(600000)

def timerCheckUpdate():

    checkUpdate()
    ui.timerCheckUpdate = QtCore.QTimer()
    ui.timerCheckUpdate.timeout.connect(checkUpdate)
    ui.timerCheckUpdate.start(1800000)

ui.statusEthernet = True
ui.statusConfig = 0
ui.countAdvertising = 0
ui.secondAdvertising = 1
ui.barcodeCopy = ''
ui.countRel = 0
ui.rels = []
ui.isLineEdit = False
ui.source = 0

ui.apiKey="39fa302c1a6b40e19020b376c9becb3b"
ui.apiStock="235"
ui.apiDevice="DeviceName"
ui.apiNumberBody="0000"
ui.actualVersion="10.0.0.1"

ui.apiDeviceNumbers = ""

pc_logging.createLogs()
#pc_logging.writeInfo('Starting')
getInfo()
timerCheckInput()
timerCheckEthernet()
timerCheckPing()
timerTemperatureAndHumidity()
timerCheckUpdate()

MainWindow.showMaximized()
ui.barcode.returnPressed.connect(barcodePressedEnter)
ui.barcode.textEdited.connect(backspace)
ui.progressBarWorker = ProgressBarWorker()
ui.progressBarThread = QThread()
ui.progressBarWorker.moveToThread(ui.progressBarThread)
ui.progressBarWorker.change_value.connect(ui.progressBar.setValue)
ui.progressBarThread.started.connect(ui.progressBarWorker.run)
ui.time = time.time()
ui.progressBarThread.start()
# Run
sys.exit(app.exec_())