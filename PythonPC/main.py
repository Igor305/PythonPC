from PyQt5 import QtCore, QtGui, QtWidgets
from interface import Ui_MainWindow
from PyQt5.QtCore import QEvent, QThread, pyqtSignal
from datetime import datetime
from ping3 import ping, verbose_ping

import socket
import requests 
import sys
import time
import os

# Create application
app = QtWidgets.QApplication(sys.argv)

# Init
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

# Logic

# QThead For ProgressBar

class ProgressBarWorker(QThread):   
    
    change_value = pyqtSignal(float)

    def __init__(ui):
        super(ProgressBarWorker,ui).__init__()
        ui.progress = 100
        ui.isStop = False

    def run(ui):
        while True:
            time.sleep(0.08)
            ui.progress -= 1
            ui.change_value.emit(ui.progress)
            
            if (ui.isStop == True):
                ui.isStop = False
                ui.progress = 105
                ui.run()
            
            if (ui.progress == 0):
                ui.wait()

    def stop(ui):
        ui.isStop = True
   
# Get System Info

def getInfo():
    
    deviceName = socket.gethostname()
    ui.deviceName.setText("Имя устройства: " + deviceName)
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        ui.ipAddress.setText("Ip Address: " + str(ip)) 

    except OSError:
        ui.ipAddress.setText("Ip Address: ") 
        ui.statusEthernet = False

    ipAddressStatic = open("/etc/dhcpcd.conf", "r")
    for s in ipAddressStatic:
        if "static routers" in s:
            break
        if "static ip_address=" in s:
            ui.ipAddressStatic.setText("Стат. IP-адрес: " + s[19:-4])

    ui.version.setText("Версия: Beta-test")

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

    ui.temperatureOut.setText("Температура внеш.: ")
    ui.humidity.setText("Влажность: ")

    if (os.path.exists("/etc/deviceCaseNum.conf")):
        numberBody = open("/etc/deviceCaseNum.conf", "r")
        ui.apiDevice = numberBody.read()
        ui.numberBody.setText("Номер корпуса: " + ui.apiDevice)
    else:
        numberBody = open("/etc/deviceCaseNum.conf", "w")
        numberBody.write(ui.apiDevice)
        numberBody.close()
    
# Change File Config

def changeConfig():
    
    os.system("sudo hostnamectl set-hostname " + ui.actualDeviceName)

    Ip = open ("/etc/dhcpcd.conf", "r")

    newIp = open ("Ip.conf", "w")

    ip =""
    minitempIp = ui.tempIp[0 : ui.tempIp.rfind('.')] 

    lines = Ip.readlines()
   
    for line in lines:     

            if not line:
                break

            elif(line.find(" static ip_address") == 0):            
                ip += " static ip_address=" + ui.tempIp + "/24\n"

            elif(line.find(" static routers") == 0):
                ip += " static routers=" + minitempIp + ".1\n"

            else:
                ip += line

    Ip.close()
    newIp.write(ip)
    newIp.close()

    Ip = open ("/etc/dhcpcd.conf", "w")
    Ip.write(ip)

    '''
    numberBody = open("/etc/deviceCaseNum.conf", "w")
    numberBody.write(ui.tempNumberBody)
    numberBody.close()
    '''
# When barcode textChanged

def sync_lineEdit():

    barcode = ui.barcode.text() 

    if(ui.progressBarThread.isRunning()):
        ui.progressBarWorker.stop()    

    ui.progressBarThread.start()    
    hideForms()

    if (barcode != ""):    
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/manualInputBc_dark.png"))
        ui.barcode.setGeometry(QtCore.QRect(40, 245, 800, 70))
        ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1013, 20))

# When Press Enter

def barcodePressedEnter():
    barcode = ui.barcode.text() 

    # Mode Config

    if (ui.statusConfig == 1):  
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        ui.configTitle.setText("Настройки")

        if (int(barcode) < 0 or int(barcode) == 100 ):
            ui.configText.setText("Отскануйте номер магазину")
            ui.configValue.setText("Номер магазину повинен бути більше 0, не 100")
            ui.configValue.setGeometry(QtCore.QRect(0, 350, 1024, 100))
        else:
            ui.configText.setText("Отскануйте номер прайсчекера")
            ui.statusConfig = 2   
            ui.tempNumberShop = barcode
            print("Номер магазина = " + barcode)

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (ui.statusConfig == 2):  
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))      

        ui.configTitle.setText("Настройки")

        if (int(barcode) < 0):
            ui.configText.setText("Отскануйте номер прайсчекера")
            ui.configValue.setText("Номер прайсчекера повинен бути більше 0")
            ui.configValue.setGeometry(QtCore.QRect(0, 350, 1024, 100))
        else:
            ui.configText.setText("Отскануйте IP-адрес")
            ui.statusConfig = 3
            ui.tempNumberPC = barcode
            print("Номер прайсчекера = " + barcode)

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (ui.statusConfig == 3):  
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))      
        ui.statusConfig = 4
        ui.configTitle.setText("Настройки")
        ui.configText.setText("Отскануйте номер корпуса")

        ui.tempIp = barcode
        print("IP-адрес = " + barcode)

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (ui.statusConfig == 4):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))       
        ui.statusConfig = 5
        ui.configTitle.setText("Настройки")
        ui.configText.setText("Збережіть зміни або відмініть")

        ui.tempNumberBody = barcode
        print("Номер корпуса = " + barcode)

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (ui.statusConfig == 5):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))       
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

            os.system("sudo reboot")

        elif (barcode == "772211004"):
            ui.configText.setText("Настройки відмінені")
            ui.statusConfig = 0
        else:
            ui.configText.setText("Збережіть зміни або відмініть")
            ui.configValue.setText("Неправильний штрихкод")
            ui.configValue.setGeometry(QtCore.QRect(0, 350, 1024, 100))
            
        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    elif (barcode == ""):
        print("")

    # Mode viewing info 

    elif (barcode == "772211001"):
        getInfo()
        ui.barcode.setText("")
        ui.statusConfig = -1
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        ui.progressBar.setGeometry(QtCore.QRect(3, 575, 1013, 20))
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
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        
        ui.configTitle.setText("Настройки")
        ui.configText.setText("Отскануйте номер магазину")

        ui.configTitle.setGeometry(QtCore.QRect(0, 60, 1024, 100))
        ui.configText.setGeometry(QtCore.QRect(0, 200, 1024, 100))

    # Mode Reset 

    elif (barcode == "BarcodeReset"):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        print("Сброс")

    # Check Employment

    elif (barcode.find("ent") == False and ui.statusEthernet == True and ui.failConnenct == False):    
        try: 
            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/employeeInfo.png"))

            emp = 'http://' + ui.apiAddress + '/emp_info?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode='
            emp += barcode

            response = requests.get(emp).text
            print(response)
            responseMini1 = response.replace('{"Id":', '')
            idStr = responseMini1[0:responseMini1.index(',')]
            responseMini2 = responseMini1.replace(idStr + ',"Barcode":"','')
            barcodeStr = responseMini2[0:responseMini2.index('",')]
            responseMini3 = responseMini2.replace(barcodeStr + '","Name":"','')
            nameEmp = responseMini3[0:responseMini3.index('",')]
            responseMini4 = responseMini3.replace(nameEmp + '","State":','')
            state = responseMini4[0:responseMini4.index('}')]

            ui.nameEmp.setWordWrap(True)
            ui.nameEmp.setText(nameEmp)

            if(state == "0"):
                ui.statusEmp.setText("кінець")
            elif(state == "1"):
                ui.statusEmp.setText("початок")
            
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            ui.timeEmp.setText("робочого дня зафіксовано о " + current_time)

            ui.nameEmp.setGeometry(QtCore.QRect(0, 150, 1024, 200))
            ui.statusEmp.setGeometry(QtCore.QRect(0, 310, 1024, 200))
            ui.timeEmp.setGeometry(QtCore.QRect(0, 380, 1024, 200))

        except Exception:

            ui.barcodeText.setGeometry(QtCore.QRect(40, 550, 0, 0))
            ui.barcodeValue.setGeometry(QtCore.QRect(80, 550, 0, 0))
            ui.amountText.setGeometry(QtCore.QRect(290, 550, 0, 0))
            ui.amountValue.setGeometry(QtCore.QRect(370, 550, 0, 0))
            ui.codeText.setGeometry(QtCore.QRect(420, 550, 0, 0))
            ui.codeValue.setGeometry(QtCore.QRect(460, 550, 0, 0))
            ui.name.setGeometry(QtCore.QRect(80, 320, 0, 0))
            ui.price.setGeometry(QtCore.QRect(250, 200, 0, 0))

            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/merchandiserError.png"))          

    else:

        # Check Barcode

        if ui.statusEthernet == False or ui.failConnenct == True:

            if ui.statusEthernet == False:

                hideForms()
                ui.barcode.setText("")
                ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/error_server_dark.jpg"))

            elif ui.failConnenct == True:

                hideForms()
                ui.barcode.setText("")
                ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/Offline_dark_2.jpg"))

        elif (len(barcode) > 12):

            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/productBack_dark.jpg"))
            art = 'http://' + ui.apiAddress + '/art?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&barcode='
            art += barcode
            response = requests.get(art)
            getProductInfo(art,barcode)

        # Check Code

        elif(len(barcode) <= 12):

            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/productBack_dark.jpg"))
            art = 'http://' + ui.apiAddress + '/art?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code=' 
            art += barcode +'&source=1'
            getProductInfo(art,barcode)

# Info For product 

def getProductInfo(art,barcode):
    try:

        response = requests.get(art).text
        print (response)
        responseMini1 = response.replace('{"Barcode":' ,'')

        if (responseMini1[0] == '"'):

            responseMini1NotNull = responseMini1[1:]
            barcodeStr = responseMini1NotNull[0:responseMini1NotNull.index('",')]
            responseMini2 = responseMini1NotNull.replace(barcodeStr + '","Id":','')

        elif (responseMini1[0] != '"'):

            barcodeStr = responseMini1[0:responseMini1.index(',')]
            responseMini2 = responseMini1.replace(barcodeStr + ',"Id":','')
        idStr = responseMini2[0:responseMini2.index(',')]
        responseMini3 = responseMini2.replace(idStr + ',"Name":"','')
        nameStr = responseMini3[0:responseMini3.index('",')]
        responseMini4 = responseMini3.replace(nameStr + '","Price":','')
        priceStr = responseMini4[0:responseMini4.index(',')]
        responseMini5 = responseMini4.replace(priceStr + ',"PriceOld":','')
        priceOldStr = responseMini5[0:responseMini5.index(",")]
        responseMini6 = responseMini5.replace(priceOldStr + ',"Qty":','')
        qtyStr = responseMini6[0:responseMini6.index('}')]

        priceFloat = float(priceStr)
        price = str("%.0f" % priceFloat)
        penny = str("%.0f" % ((priceFloat%1) * 100) )

        if (penny == "0"):
            penny = "00"

        if (priceOldStr != "null"):
            priceOldFloat = float(priceOldStr)
            priceOld = str("%.0f" % priceOldFloat)
            pennyOld = str("%.0f" % ((priceOldFloat%1) * 100) )

            if (pennyOld == "0"):
                pennyOld = "00"

        ui.barcodeText.setText("Ш/К:")
        ui.barcodeValue.setText(barcodeStr)
        ui.amountText.setText("Кількість:")
        ui.amountValue.setText(qtyStr)
        ui.codeText.setText("Код:")
        ui.codeValue.setText(idStr)
        ui.name.setText(nameStr)
        ui.price.setText(price)
        ui.pricePenny.setText(penny)
        ui.priceCurrency.setText("грн")
        
        
        if (priceOldStr != "null"):
            ui.priceOld.setText(priceOld)
            ui.priceOldPenny.setText(pennyOld)
            ui.priceOldCurrency.setText("грн")
            
            if (priceOldFloat < 10):
                ui.priceOld.setGeometry(QtCore.QRect(350, 30, 100, 100))
                ui.priceOldPenny.setGeometry(QtCore.QRect(440, 30, 200, 50))
                ui.priceOldCurrency.setGeometry(QtCore.QRect(430, 30, 200, 150))

            elif (priceOldFloat < 100):
                ui.priceOld.setGeometry(QtCore.QRect(270, 30, 250, 100))
                ui.priceOldPenny.setGeometry(QtCore.QRect(440, 30, 200, 50))
                ui.priceOldCurrency.setGeometry(QtCore.QRect(430, 30, 200, 150))

            elif (priceOldFloat >= 100):
                ui.priceOld.setGeometry(QtCore.QRect(180, 30, 250, 100))
                ui.priceOldPenny.setGeometry(QtCore.QRect(440, 30, 200, 50))
                ui.priceOldCurrency.setGeometry(QtCore.QRect(430, 30, 200, 150))

        ui.barcodeText.setGeometry(QtCore.QRect(40, 550, 80, 20))
        ui.barcodeValue.setGeometry(QtCore.QRect(80, 550, 200, 20))
        ui.amountText.setGeometry(QtCore.QRect(270, 550, 100, 20))
        ui.amountValue.setGeometry(QtCore.QRect(350, 550, 80, 20))
        ui.codeText.setGeometry(QtCore.QRect(400, 550, 80, 20))
        ui.codeValue.setGeometry(QtCore.QRect(440, 550, 80, 20))
        ui.name.setWordWrap(True)
        ui.name.setGeometry(QtCore.QRect(40, 380, 450, 150))     
        
        if (priceFloat < 10):
            ui.price.setGeometry(QtCore.QRect(0, 100, 450, 300))
            ui.pricePenny.setGeometry(QtCore.QRect(300, 120, 200, 200))
            ui.priceCurrency.setGeometry(QtCore.QRect(300, 190, 200, 200))
        elif (priceFloat < 100):

            ui.price.setGeometry(QtCore.QRect(0, 100, 450, 300))
            ui.pricePenny.setGeometry(QtCore.QRect(350, 120, 200, 200))
            ui.priceCurrency.setGeometry(QtCore.QRect(350, 190, 200, 200))  
        elif (priceFloat >= 100):   

            ui.price.setGeometry(QtCore.QRect(0, 100, 400, 300))
            ui.pricePenny.setGeometry(QtCore.QRect(380, 120, 200, 200))
            ui.priceCurrency.setGeometry(QtCore.QRect(380, 190, 200, 200))

        # Get image product

        try:
            image  = 'http://' + ui.apiAddress + '/img?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&code='
            image += idStr + '&sticker=1'
            
            responseImage = requests.get(image)
            
            print(responseImage.url)
            file = open("PythonPC/img/temp/temp_image.jpg", "wb")
            file.write(responseImage.content)
            file.close()

            ui.productImage.setStyleSheet("border-radius:15px; border-image: url(PythonPC/img/temp/temp_image.jpg) 0 0 0 0 stretch stretch;")
            
            ui.productImage.setGeometry(QtCore.QRect(530, 25, 470, 545))
                
        except Exception:
            ui.productImage.setPixmap(QtGui.QPixmap("PythonPC/img/resources/noImage.jpg"))         
    
         
    except Exception:

        # Check Card

        try:
            card = 'http://' + ui.apiAddress + '/card?key='+ ui.apiKey +'&stock='+ ui.apiStock + '&device=' + ui.apiDevice + '&card='
            card += barcode + '&source=1'
            responseCard = requests.get(card).text
            print(responseCard)

            responseMini1Card = responseCard.replace('{"Bonus":' ,'')
            bonusStr = responseMini1Card[0:responseMini1Card.index(',')]
            responseMini2Card = responseMini1Card.replace(bonusStr + ',"Id":"' ,'')
            idStr = responseMini2Card[0:responseMini2Card.index('",')]
            responseMini3Card = responseMini2Card.replace(idStr + '","Name":"' ,'')
            nameStrCard = responseMini3Card[0:responseMini3Card.index('"}')]

            bonus = int(bonusStr)
            cash = bonus / 100
            penny = bonus % 100
            
            ui.nameCard.setText(nameStrCard + ', на Вашому рахунку')
            ui.bonus.setText(str("%.0f" % cash) + "." + str(penny))

            ui.nameCard.setGeometry(QtCore.QRect(120, 180, 800, 60))
            ui.bonus.setGeometry(QtCore.QRect(0, 210, 1024, 400))

            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/dCardBack_dark.jpg"))          
            
        except Exception:

            ui.barcodeText.setGeometry(QtCore.QRect(40, 550, 0, 0))
            ui.barcodeValue.setGeometry(QtCore.QRect(80, 550, 0, 0))
            ui.amountText.setGeometry(QtCore.QRect(290, 550, 0, 0))
            ui.amountValue.setGeometry(QtCore.QRect(370, 550, 0, 0))
            ui.codeText.setGeometry(QtCore.QRect(420, 550, 0, 0))
            ui.codeValue.setGeometry(QtCore.QRect(460, 550, 0, 0))
            ui.name.setGeometry(QtCore.QRect(80, 320, 0, 0))
            ui.price.setGeometry(QtCore.QRect(250, 200, 0, 0))

            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/merchandiserError.png"))

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

            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/error_server_dark.jpg"))

    if ui.statusEthernet == True:

        barcode = ui.barcode.text() 

        if pingMpce03 == None and pingMpce04 == None or pingMpce03 == False and pingMpce04 == False:
            ui.failConnenct = True 
        
        elif pingMpce04 == False or None:
            ui.apiAddress = mpce03
        
        elif pingMpce03 == False or None:
            ui.apiAddress = mpce04

        elif pingMpce03 < pingMpce04:
            ui.apiAddress = mpce03

        elif pingMpce04 < pingMpce03:     
            ui.apiAddress = mpce04

        if (ui.progressBar.value() < 1):
            ui.barcode.setText("") 
            ui.statusConfig = 0

        if (ui.failConnenct == True and ui.statusConfig == 0 and len(barcode) < 1):

            hideForms()

            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/Offline_dark_2.jpg"))

def advertising ():
    
    if (ui.progressBar.value() < 1 and ui.failConnenct == False and ui.statusEthernet == True):
        ui.barcode.setText("")

        hideForms() 

        for root, dirs, files in os.walk("PythonPC/img/advertise"): 
            for filename in files:                          
                ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/advertise/" + files[ui.countAdvertising]))
        
        if( ui.secondAdvertising == 8):
            ui.secondAdvertising = 0
            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/advertise/" + files[ui.countAdvertising]))
            ui.countAdvertising +=1

        if (ui.countAdvertising > len(files)-1 ):
            ui.countAdvertising = 0

        ui.secondAdvertising += 1

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
    ui.codeText.setGeometry(QtCore.QRect(420, 550, 0, 0))
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

def timerCheckPing():

    checkPing()
    ui.timerCheckPing = QtCore.QTimer()
    ui.timerCheckPing.timeout.connect(checkPing)
    ui.timerCheckPing.start(1000)

def timerAdvertising():

    ui.timerAdvertising = QtCore.QTimer()
    ui.timerAdvertising.timeout.connect(advertising)
    ui.timerAdvertising.start(1000)

ui.statusEthernet = True
ui.statusConfig = 0
ui.countAdvertising = 0
ui.secondAdvertising = 8
ui.apiKey="39fa302c1a6b40e19020b376c9becb3b"
ui.apiStock="235"
ui.apiDevice="0000"

timerCheckPing()
timerAdvertising()
getInfo()
MainWindow.showMaximized()
#MainWindow.setWindowFlags(QtCore.Qt.CustomizeWindowHint)       
ui.barcode.textChanged.connect(sync_lineEdit)
ui.barcode.returnPressed.connect(barcodePressedEnter)
ui.progressBarWorker = ProgressBarWorker()
ui.progressBarThread = QThread()
ui.progressBarWorker.moveToThread(ui.progressBarThread)       
ui.progressBarWorker.change_value.connect(ui.progressBar.setValue)
ui.progressBarThread.started.connect(ui.progressBarWorker.run) 

# Run
sys.exit(app.exec_())