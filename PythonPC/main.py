from PyQt5 import QtCore, QtGui, QtWidgets
from interface import Ui_MainWindow
from PyQt5.QtCore import QEvent, QThread, pyqtSignal
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
class AdvertisingWorker(QThread):

    change_image = pyqtSignal()

    def run(ui):
       
        timing = time.time()
        while True:
              if time.time() - timing > 8.0:
                timing = time.time()
                ui.change_image = (QtGui.QPixmap("PythonPC/img/advertise/133.Episode.png"))
                print(ui.change_image)

class ProgressBarWorker(QThread):   
    
    change_image = pyqtSignal()
    change_value = pyqtSignal(float)

    def run(ui):
        progress = 100
        while progress != 0:
            time.sleep(0.01)
            progress -= 1
            ui.change_value.emit(progress)
            if (progress == 0):    
                print(progress)
                ui.change_image = QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg")
"""        
def getInfo():
    deviceName = open("/etc/hostname", "r")
    ui.deviceName.setText("Имя устройства: " + deviceName.read())
    
    ipAddress = os.system("hostname -I")
    ui.ipAddress.setText("Ip Address: " + ipAddress)  

    ipAddressStatic = open("/etc/dhcpcd.conf", "r")
    for s in ipAddressStatic:
        if "# It is possible to fall back to a static IP if DHCP fails:" in s:
            break
        if "#static ip_address=" in s:
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
    ui.numberBody.setText("Номер корпуса: ")
"""
def sync_lineEdit():
    barcode = ui.barcode.text() 
    print(barcode)

    ui.barcodeText.setGeometry(QtCore.QRect(40, 550, 0, 0))
    ui.barcodeValue.setGeometry(QtCore.QRect(80, 550, 0, 0))
    ui.amountText.setGeometry(QtCore.QRect(290, 550, 0, 0))
    ui.amountValue.setGeometry(QtCore.QRect(370, 550, 0, 0))
    ui.codeText.setGeometry(QtCore.QRect(420, 550, 0, 0))
    ui.codeValue.setGeometry(QtCore.QRect(460, 550, 0, 0))
    ui.name.setGeometry(QtCore.QRect(80, 320, 0, 0))
    ui.price.setGeometry(QtCore.QRect(250, 200, 0, 0))
    ui.nameCard.setGeometry(QtCore.QRect(120, 180, 800, 0))
    ui.bonus.setGeometry(QtCore.QRect(0, 210, 1024, 0))

    if (barcode != ""):    
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/manualInputBc_dark.png"))
        ui.barcode.setGeometry(QtCore.QRect(40, 245, 800, 70))
        ui.progressBar.setGeometry(QtCore.QRect(10, 575, 1041, 15))

    ui.progressBarThread.start() 
    ui.progressBarThread.quit()      

def barcodePressedEnter():

    barcode = ui.barcode.text() 

    if (barcode == ""):
        print("Ты чего")

    elif (barcode == "772211001"):
        ui.barcode.setText("")
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.progressBar.setGeometry(QtCore.QRect(10, 570, 1041, 23))
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

    elif (barcode == "772211002"):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        print("Задать настройки")

    elif (barcode == "772211003"):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        print("Сохранить настройки")
    
    elif (barcode == "772211004"):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        print("Не сохранять настройки")

    elif (barcode == "BarcodeReset"):
        ui.barcode.setText("")
        ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
        ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/systemInfo_dark.jpg"))
        print("Сброс")

    elif (barcode.find("ent") == False):
        emp = 'http://mpce03.avrora.lan/emp_info?key=39fa302c1a6b40e19020b376c9becb3b&stock=236&device=DeviceName&barcode='
        emp += barcode
        response = requests.get(emp)
        print(response.text)

    else:
        if (len(barcode) > 12):
            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/productBack_dark.jpg"))
            art = 'http://mpce03.avrora.lan/art?key=39fa302c1a6b40e19020b376c9becb3b&stock=235&device=DeviceName&barcode='
            art += barcode
            response = requests.get(art)
            getProductInfo(art,barcode)

        elif(len(barcode) <= 12):
            ui.barcode.setText("")
            ui.barcode.setGeometry(QtCore.QRect(70, 245, 0, 0))
            ui.image.setPixmap(QtGui.QPixmap("PythonPC/img/resources/productBack_dark.jpg"))
            art = 'http://mpce04.avrora.lan/art?key=39fa302c1a6b40e19020b376c9becb3b&stock=235&device=DeviceName&code=' 
            art += barcode +'&source=1'
            getProductInfo(art,barcode)


def getProductInfo(art,barcode):
    try:
        response = requests.get(art).text
        print (response)
        responseMini1 = response.replace('{"Barcode":"' ,'')
        barcodeStr = responseMini1[0:responseMini1.index('",')]
        responseMini2 = responseMini1.replace(barcodeStr + '","Id":','')
        idStr = responseMini2[0:responseMini2.index(',')]
        responseMini3 = responseMini2.replace(idStr + ',"Name":"','')
        nameStr = responseMini3[0:responseMini3.index('",')]
        responseMini4 = responseMini3.replace(nameStr + '","Price":','')
        priceStr = responseMini4[0:responseMini4.index(',')]
        responseMini5 = responseMini4.replace(priceStr + ',"PriceOld":','')
        priceOldStr = responseMini5[0:responseMini5.index(",")]
        responseMini6 = responseMini5.replace(priceOldStr + ',"Qty":','')
        qtyStr = responseMini6[0:responseMini6.index('}')]

        ui.barcodeText.setText("Ш/К:")
        ui.barcodeValue.setText(barcodeStr)
        ui.amountText.setText("Кількість:")
        ui.amountValue.setText(qtyStr)
        ui.codeText.setText("Код:")
        ui.codeValue.setText(idStr)
        ui.name.setText(nameStr)
        ui.price.setText(priceStr)

        ui.barcodeText.setGeometry(QtCore.QRect(40, 550, 80, 20))
        ui.barcodeValue.setGeometry(QtCore.QRect(80, 550, 200, 20))
        ui.amountText.setGeometry(QtCore.QRect(290, 550, 100, 20))
        ui.amountValue.setGeometry(QtCore.QRect(370, 550, 80, 20))
        ui.codeText.setGeometry(QtCore.QRect(420, 550, 80, 20))
        ui.codeValue.setGeometry(QtCore.QRect(460, 550, 80, 20))
        ui.name.setGeometry(QtCore.QRect(80, 320, 400, 200))
        ui.price.setGeometry(QtCore.QRect(250, 200, 80, 20))

    except Exception:

        try:
            card = 'http://mpce04.avrora.lan/card?key=39fa302c1a6b40e19020b376c9becb3b&stock=235&device=DeviceName&card='
            card += barcode + '&source=1'
            responseCard = requests.get(card).text
            print(responseCard)

            responseMini1Card = responseCard.replace('{"Bonus":' ,'')
            bonusStr = responseMini1Card[0:responseMini1Card.index(',')]
            responseMini2Card = responseMini1Card.replace(bonusStr + ',"Id":"' ,'')
            idStr = responseMini2Card[0:responseMini2Card.index('",')]
            responseMini3Card = responseMini2Card.replace(idStr + '","Name":"' ,'')
            nameStrCard = responseMini3Card[0:responseMini3Card.index('"}')]
            
            ui.nameCard.setText(nameStrCard + ', на Вашому рахунку')
            ui.bonus.setText(bonusStr)

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
            

#getInfo()
ui.advertisingWorker = AdvertisingWorker()
ui.advertisingThread = QThread()
ui.advertisingWorker.moveToThread(ui.advertisingThread)
ui.advertisingWorker.change_image.connect(ui.image.setPixmap)
print(ui.image.setPixmap)
ui.advertisingThread.started.connect(ui.advertisingWorker.run)
#ui.advertisingThread.start()
ui.barcode.textChanged.connect(sync_lineEdit)
ui.barcode.returnPressed.connect(barcodePressedEnter)
ui.progressBarWorker = ProgressBarWorker()
ui.progressBarThread = QThread()
ui.progressBarWorker.moveToThread(ui.progressBarThread)       
ui.progressBarWorker.change_value.connect(ui.progressBar.setValue)
ui.progressBarWorker.change_image.connect(ui.image.pixmap)
print(ui.progressBarWorker.change_image)
print(ui.image.pixmap)
ui.progressBarThread.started.connect(ui.progressBarWorker.run) 


# Run
sys.exit(app.exec_())
