from logging import captureWarnings
import pc_logging
import sensorDHT

from genericpath import exists
from PyQt5 import QtCore, QtGui, QtWidgets
from adafruit_platformdetect import board
from interface import Ui_MainWindow
from PyQt5.QtCore import QLine, QLineF, QThread, pyqtSignal
from datetime import date, datetime
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
        ui.isStop = False

    def run(ui):
        while True:
       
            if (ui.isStop == True):
                ui.isStop = False
                ui.progress = 103
                ui.run()
         
            if (ui.progress == 0):
                ui.wait()

            if (ui.progress > 0):
                time.sleep(0.08)
                ui.progress -= 1
                ui.change_value.emit(ui.progress)

    def stop(ui):
        ui.isStop = True

# Get System Info

def getInfo():
    
    deviceName = socket.gethostname()
    ui.deviceName.setText("Имя устройства: " + deviceName)

    if (deviceName != "Avrora"):   
        name = deviceName.split('-P')    
        stock = name[0]
        device = name[1]

        stock = stock[1:len(stock)]

        while(stock.find('0') == 0):
            stock = stock[1:len(stock)]

        ui.apiStock = stock
        ui.apiDevice = device
    
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

    serial = open("/proc/cpuinfo", "r")
    for s in serial:
        if "Serial" in s:
            ui.serial.setText("Serial: " + s[10:])

    sensorDHTdata = sensorDHT.getSensorData()

    ui.temperatureOut.setText(f"Температура внеш.: {sensorDHTdata[0]:.1f}")
    ui.humidity.setText(f"Влажность: {sensorDHTdata[1]:.1f}") 
    
    if (os.path.exists("deviceCaseNum.conf")):
        numberBody = open("deviceCaseNum.conf", "r")
        ui.apiNumberBody = numberBody.read()
        ui.numberBody.setText("Номер корпуса: " + ui.apiNumberBody)
        numberBody.close()
    else:
        numberBody = open("deviceCaseNum.conf", "w")
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

    nBody = open ("deviceCaseNum.conf", "w")
    nBody.write(ui.tempNumberBody)
    nBody.close()

# When barcode textChanged

def sync_lineEdit(barcode):
    ui.countRel = 0
    ui.progressBarWorker.stop()
    ui.progressBarThread.start() 

    hideForms() 

    if(barcode == "" and ui.statusConfig <= 0):   

        advertising()

    if(barcode != ""):

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
    ui.progressBarWorker.stop()
    ui.progressBarThread.start()  
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
                actualNumberShop = "a000" + str(ui.tempNumberShop)
            elif (int(ui.tempNumberShop) >= 10 and int(ui.tempNumberShop) < 100):
                actualNumberShop = "a00" + str(ui.tempNumberShop)
            elif (int(ui.tempNumberShop) >= 100 and int(ui.tempNumberShop) < 1000):
                actualNumberShop = "a0" + str(ui.tempNumberShop)
            elif (int(ui.tempNumberShop) >= 1000):
                actualNumberShop = "a" + str(ui.tempNumberShop)

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
            ui.timeEmp.setText("робочого дня зафіксовано о " + current_time)

            ui.nameEmp.setGeometry(QtCore.QRect(0, 150, 1024, 200))
            ui.statusEmp.setGeometry(QtCore.QRect(0, 310, 1024, 200))
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

        elif (len(barcode) > 12):

            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/productBack_dark.jpg"))
            art = 'http://' + ui.apiAddress + '/artex?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode=' + barcode + '&source=' + str(ui.source)
            km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode=' + barcode + '&source=' + str(ui.source)
            rel = 'http://' + ui.apiAddress + '/rel?key='+ ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode=' + barcode + '&source=' + str(ui.source)
            getProductInfo(art, km, rel, barcode)

        # Check Code

        elif(len(barcode) <= 12):

            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/productBack_dark.jpg"))
            art = 'http://' + ui.apiAddress + '/artex?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
            km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
            rel = 'http://' + ui.apiAddress + '/rel?key='+ ui.apiKey + '&stock' + ui.apiStock + '&device=' + ui.apiDevice + '&code=' + barcode + '&source=' + str(ui.source)
            getProductInfo(art, km, rel, barcode)

# Info For product 

def getProductInfo(art, km, rel, barcode):
    
        # Get related products
       # try:
            response = requests.get(rel).json()
            if(len(response) > 0):
                ui.countRel = len(response)
                ui.rels = response
            
            getProduct(art,km)
            '''
        except Exception:  

            try:
                getCard(barcode)          
                
            except Exception:

                hideForms()
                ui.image.setPixmap(QtGui.QPixmap(pathImg + "img/resources/merchandiserError.png")) 
                ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))
            '''
# Get info product  

def getProduct(art,km):
    ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1017, 20))

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

    ui.peneee = QLine()
    ui.peneee.setLine(32,23,220,250)
    print(ui.peneee.isNull())
    print(priceOldBonus)
    print(bonusDateFrom)
    print(bonusDateTo)

    if (name == None):
        raise Exception('name == None')

    strBarcode = strCode = strQty = strKm = ""

    if (barcode != None) : strBarcode = str(barcode)     
    if (code != None) : strCode = str(code)    
    if (qty != None) : strQty= str(qty)    

    priceStr = str("%.0f" % price)
    penny = str("%.0f" % ((price%1) * 100))
    
    if (penny == "0"):
        penny = "00"
    
    if (priceOld != None):
        priceOldStr = str("%.0f" % priceOld)
        pennyOld = str("%.0f" % ((priceOld%1) * 100) )

        if (pennyOld == "0"):
            pennyOld = "00"
        
    try:
        km = getKM(km)
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

    if (priceOld != None):
        ui.priceOld.setText(priceOldStr)
        ui.priceOldPenny.setText(pennyOld)
        ui.priceOldCurrency.setText("грн")
        ui.priceOld.setGeometry(QtCore.QRect(130, 10, 300, 130))
        ui.priceOldPenny.setGeometry(QtCore.QRect(440, 30, 200, 50))
        ui.priceOldCurrency.setGeometry(QtCore.QRect(430, 30, 200, 150))
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
    ui.name.setGeometry(QtCore.QRect(40, 380, 450, 120)) 
    font.setPointSize(140)
    font.setBold(True)
    font.setWeight(75)
    ui.price.setFont(font)  
    font.setPointSize(65)
    font.setBold(True)
    font.setWeight(75)
    ui.pricePenny.setFont(font) 
    font.setPointSize(55)
    ui.priceCurrency.setFont(font) 
    ui.priceCurrency.setStyleSheet("color: rgb(255, 238, 0);")

    ui.price.setGeometry(QtCore.QRect(0, 140, 370, 300))
    ui.pricePenny.setGeometry(QtCore.QRect(370, 110, 200, 200))
    ui.priceCurrency.setGeometry(QtCore.QRect(370, 190, 200, 200))

    try:
        path = getImage(str(code))

        ui.productImage.setStyleSheet(f"border-radius:15px; border-image: url({path}img/temp/temp_image.jpg) 0 0 0 0 stretch stretch;")   
        ui.productImage.setGeometry(QtCore.QRect(530, 25, 470, 545))
  
    except Exception:
        ui.productImage.setPixmap(QtGui.QPixmap(pathImg + "img/resources/noImage.jpg")) 

# Get KM
def getKM(km):

    response = requests.get(km)
    pc_logging.writeResponseToLog(response.url,response.elapsed.total_seconds())
    response = response.json()

    responseKM = response["KM"]
    km = str(responseKM["Id"])

    return(km)

# Get image product

def getImage(code):

    image  = 'http://' + ui.apiAddress + '/img?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + code + '&sticker=1&source=' + str(ui.source)

    responseImage = requests.get(image)           
    pc_logging.writeResponseToLog(responseImage.url,responseImage.elapsed.total_seconds())

    file = open(pathImg + "img/temp/temp_image.jpg", "wb")
    file.write(responseImage.content)
    file.close()

    return pathImg

# Get Card Info

def getCard(barcode):

    card = 'http://' + ui.apiAddress + '/card?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&card=' + barcode + '&source=' + str(ui.source)

    responseCard = requests.get(card)     
    pc_logging.writeResponseToLog(responseCard.url,responseCard.elapsed.total_seconds())
    responseCard = responseCard.json()   

    bonus = responseCard["Bonus"]
    cash = int(bonus / 100)
    penny = bonus % 100

    name = responseCard["Name"]
    ui.nameCard.setText(name + ', на Вашому рахунку')
    ui.bonus.setText(str(cash) + "," + str(penny))

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
        ui.progressBarWorker.stop()
        ui.progressBarThread.start()
    
        code = str(ui.rels[ui.countRel-1])

        art = 'http://' + ui.apiAddress + '/art?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + code +'&source=3'
        km ='http://' + ui.apiAddress + '/category?key=' + ui.apiKey + '&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' + code +'&source=3'

        km = getKM(km)

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

            ui.productImageRel.setStyleSheet(f"border-radius:15px; border-image: url({path}img/temp/temp_image.jpg) 0 0 0 0 stretch stretch;")   
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

def checkPing():

    # Confirm API server
    mpce03 = "mpce03.avrora.lan"
    mpce04 = "mpce04.avrora.lan"
    
    pingMpce03 = ping(mpce03)
    pingMpce04 = ping(mpce04)

    ui.failConnenct = False

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

def checkInput():
    barcode = ui.barcode.text()
    length = len(barcode) - len(ui.barcodeCopy)

    if (length == 0):    
        return

    if (length <= 10 and length > 0):
        ui.isLineEdit = True
        sync_lineEdit(barcode)
    
    ui.barcodeCopy = barcode

def checkProgressBar():

    if (ui.progressBar.value() < 1 and ui.countRel < 1 and ui.statusConfig <= 0):
        advertising()
    if (ui.progressBar.value() < 1 and ui.countRel > 0):
        related()

def advertising ():
    
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

def backspace():

    length = len(ui.barcode.text()) - len(ui.barcodeCopy)

    if (length < 0):
        ui.progressBarWorker.stop()

    if (ui.barcode.text() == "" and ui.statusConfig <= 0):
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

def checkUpdate():
    try:
        time = datetime.now() 
        imgs =[]
        filenames = "" 

        for root, dirs, files in os.walk(pathImg + "img/advertise"):
                for filename in files:                          
                    imgs.append(filename)
        imgs.sort()

        for filename in imgs:                          
                filenames += filename

        info = f"http://10.13.153.10/api/price/getVersion?version={ui.actualVersion}&ip={ui.ip}&stock={ui.apiStock}&device={ui.apiDevice}&numberBody={ui.apiNumberBody}&images={filenames}&dateTime={time}"

        requests.get(info)  

    except:
        print('error actualVersion')
        
def timerCheckInput():

    ui.timerCheckInput = QtCore.QTimer()
    ui.timerCheckInput.timeout.connect(checkInput)
    ui.timerCheckInput.start(300)

def timerCheckProgressBar():

    ui.timerCheckProgressBar = QtCore.QTimer()
    ui.timerCheckProgressBar.timeout.connect(checkProgressBar)
    ui.timerCheckProgressBar.start(1000)

def timerCheckPing():

    checkPing()
    ui.timerCheckPing = QtCore.QTimer()
    ui.timerCheckPing.timeout.connect(checkPing)
    ui.timerCheckPing.start(60000)

def timerTemperatureAndHumidity():

    ui.timerTemperatureAndHumidity = QtCore.QTimer()
    ui.timerTemperatureAndHumidity.timeout.connect(lambda: sensorDHT.getTemperatureAndHumidity(ui.apiStock))
    ui.timerTemperatureAndHumidity.start(300000)

def timerCheckUpdate():

    ui.timerCheckUpdate = QtCore.QTimer()
    ui.timerCheckUpdate.timeout.connect(checkUpdate)
    ui.timerCheckUpdate.start(120000)
    
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
ui.actualVersion="1.0.0.0"

pc_logging.createLogs()
pc_logging.writeInfo('Starting')
getInfo()
timerCheckInput()
timerCheckProgressBar()
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

# Run
sys.exit(app.exec_())