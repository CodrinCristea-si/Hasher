'''
Created on Aug 11, 2023

@author: cristeacodrin
'''
import sys
import os

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from UI.offline_gui import OfflineWindowGUI


class Window(QWidget):
    __RESOURCE_PATH = os.getcwd() + "/resources/"
    __RESOURCE_IMAGES_PATH = __RESOURCE_PATH + "images/"
    __RESOURCE_STYLE_PATH = __RESOURCE_PATH + "css/"

    def __init__(self):
        """
        Draw the main popup for connection
        """
        
        # check if the style files and images are available and reachable
        try:
            self.__check_for_available_resources_files()
        except Exception as ex:
            msg = QMessageBox()
            msg.setWindowTitle("Unable to start Hasher")
            msg.setText(str(ex))
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
            return
        super().__init__()

        # set the main window
        self.setWindowTitle("Hasher")
        self.setGeometry(100, 100, 400, 300)
        
        #load the style file
        with open(self.__RESOURCE_STYLE_PATH + "popup_connect.css", "r") as f:
            stylesheet = f.read()
            self.setStyleSheet(stylesheet)
        
        #create the main widget(scene)
        # central_widget = QWidget(self)
        # self.setCentralWidget(central_widget)
        
        # menu layout
        vbox = QVBoxLayout()

        # load the hasher logo
        pixmap = QPixmap(self.__RESOURCE_IMAGES_PATH + "hasher-logo.png")  
        image_label = QLabel(self)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(pixmap)
        vbox.addWidget(image_label)
        
        # Online section
        
        # put the google option
        button_google = QPushButton("Connect with", self)
        google_logo_pixmap = QPixmap(self.__RESOURCE_IMAGES_PATH + "Google_Logo.png")
        google_logo_icon = QIcon(google_logo_pixmap)
        button_google.setIcon(google_logo_icon)
        button_google.setProperty("class", "option_button")
        button_google.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        button_google.clicked.connect(self.__handle_google_option)
        vbox.addWidget(button_google)

        # put the onedrive option
        button_one_drive = QPushButton("Connect with", self)
        one_drive_pixmap = QPixmap(self.__RESOURCE_IMAGES_PATH + "Microsoft_Office_OneDrive_Logo.png")
        one_drive_icon = QIcon(one_drive_pixmap)
        button_one_drive.setIcon(one_drive_icon)
        button_one_drive.setProperty("class", "option_button")
        button_one_drive.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        button_one_drive.clicked.connect(self.__handle_onedrive_option)
        vbox.addWidget(button_one_drive)

        # Separator between online and offline section
        
        label = QLabel("—————————————————— or ——————————————————", self)
        label.setProperty("class", "label_separator")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        vbox.addWidget(label)

        # Offline section

        # put the offline option
        button_offline = QPushButton("Offline", self)
        button_offline.setProperty("class", "option_button")
        button_offline.clicked.connect(self.__handle_offline_option)
        vbox.addWidget(button_offline)

        # central_widget.setLayout(vbox)
        self.setLayout(vbox)

    def __check_for_available_resources_files(self):
        """
        Check if the required resource files like images and css style files are reachable
        :raise: Exception for the first file that cannot be loaded  
        """
        required_files = [
            self.__RESOURCE_IMAGES_PATH + "hasher-logo.png",
            self.__RESOURCE_IMAGES_PATH + "Google_Logo.png",
            self.__RESOURCE_IMAGES_PATH + "Microsoft_Office_OneDrive_Logo.png",
            self.__RESOURCE_STYLE_PATH + "popup_connect.css",
        ]
        for file in required_files:
            if not os.path.exists(file):
                raise Exception("Cannot load the file: " + file)
            try:
                f = open(file,"r")
                f.close()
            except:
                raise Exception("Cannot load the file: " + file)

    def __handle_google_option(self):
        msg = QMessageBox()
        msg.setWindowTitle("Feature not available")
        msg.setText("This feature is not available")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def __handle_onedrive_option(self):
        msg = QMessageBox()
        msg.setWindowTitle("Feature not available")
        msg.setText("This feature is not available")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def __handle_offline_option(self):
        #self.close()
        #app = QApplication(sys.argv)
        self.hide()
        self.offline_window = OfflineWindowGUI()
        self.offline_window.show()
        #sys.exit(app.exec())
        
        #self.close()
        # msg = QMessageBox()
        # msg.setWindowTitle("Feature not available")
        # msg.setText("This feature is not available")
        # msg.setIcon(QMessageBox.Icon.Information)
        # msg.exec()
    
    # def _createMenu(self):
    #     menu = self.menuBar().addMenu("&Menu")
    #     menu.addAction("&Exit", self.close)
    #
    # def _createToolBar(self):
    #     tools = QToolBar()
    #     tools.addAction("Exit", self.close)
    #     self.addToolBar(tools)
    #
    # def _createStatusBar(self):
    #     status = QStatusBar()
    #     status.showMessage("I'm the Status Bar")
    #     self.setStatusBar(status)

if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
    
