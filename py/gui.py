import sys
import os
import requests
import time

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox
from PyQt5.uic import loadUi

from screener import Ui_MainWindow

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    total_size = pyqtSignal(int)

    def download_historical_data(self):
        url = "http://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"
        self.download(url, "historical/companyfacts.zip", 1200000000)

    def download_stock_prices(self):
        url = "https://www.sec.gov/files/company_tickers.json"
        self.download(url, "json/company_tickers.json", 900000)

    def download(self, url, filename, total_size):

        headers = {'User-agent': "jmq@hotmail.com"}
        response = requests.get(url, headers=headers, stream=True)
        print("total size is " + str(total_size))
        self.total_size.emit(total_size)

        block_size = 32 * 1024
        
        current_size = 0
    
        with open(filename, "wb") as tickers:
            for data in response.iter_content(block_size):
                current_size += len(data)
                self.progress.emit(current_size)
                tickers.write(data)
        
        print("current size is " + str(current_size))

        self.progress.emit(total_size)
        self.finished.emit()
        

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.create_directories()

        self.setup_actions()
        #self.connectSignalsSlots()
        #self.actionAbout.triggered.connect(self.about)

    """
    def connectSignalsSlots(self):
        self.action_Exit.triggered.connect(self.close)
        self.action_Find_Replace.triggered.connect(self.findAndReplace)
        self.action_About.triggered.connect(self.about)

    def findAndReplace(self):
        dialog = FindReplaceDialog(self)
        dialog.exec()

    """
    def about(self):
        QMessageBox.about(
            self,
            "About Sample Editor",
            "<p>A sample text editor app built with:</p>"
            "<p>- PyQt</p>"
            "<p>- Qt Designer</p>"
            "<p>- Python</p>",
        )

    def create_directories(self):
        dirs = ["json", "historical"]
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

    def jmqdownload_company_tickers(self):
        pass

    def setup_actions(self):
        self.actionAbout.triggered.connect(self.software_info)
        self.actionDownload_Historical_Data.triggered.connect(self.download_historical)
        self.actionDownload_Stock_Prices.triggered.connect(self.download_prices)

    def software_info(self):
        QMessageBox.about(self, "StockScreener", "v0.1")

    def download_prices(self):
        self.progressBar.setValue(0)

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.download_stock_prices)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.total_size.connect(self.update_progress_bar_range)

        self.thread.start()
     
    def download_historical(self, func):
        self.progressBar.setValue(0)

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.download_historical_data)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.total_size.connect(self.update_progress_bar_range)

        self.thread.start()
       
    def update_progress_bar(self, value):
        self.progressBar.setValue(value)

    def update_progress_bar_range(self, range):
        self.progressBar.setRange(0, range)

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
