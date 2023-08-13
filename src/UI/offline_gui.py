'''
Created on Aug 13, 2023

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
    QMessageBox, 
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QTreeView,
    QSpacerItem, QGridLayout
)
#from PySide6.QtWidgets import QFileSystemModel

from PyQt6.QtGui import QPixmap, QIcon, QFileSystemModel, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt


class OfflineWindowGUI(QMainWindow):
    def __init__(self):
        """
        Draw the main popup for connection
        """
        self.__current_target = "/"
        self.__current_status = "UP TO DATE"
        # check if the style files and images are available and reachable
        # try:
        #     self.__check_for_available_resources_files()
        # except Exception as ex:
        #     msg = QMessageBox()
        #     msg.setWindowTitle("Unable to start Hasher")
        #     msg.setText(str(ex))
        #     msg.setIcon(QMessageBox.Icon.Critical)
        #     msg.exec()
        #     return
        super().__init__()

        # set the main window
        self.setWindowTitle("Hasher Offline")
        self.setGeometry(400, 400, 600, 500)
        
        #load the style file
        # with open(self.__RESOURCE_STYLE_PATH + "popup_connect.css", "r") as f:
        #     stylesheet = f.read()
        #     self.setStyleSheet(stylesheet)
        
        #create the main widget(scene)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget) 
        
        # menu layout
        vbox = QVBoxLayout()


        target_hbox = QHBoxLayout()
        target_label = QLabel("Current target:", self)
        target_input = QLineEdit()
        target_input.setText(self.__current_target)
        button_change_target = QPushButton("Change Target", self)

        target_hbox.addWidget(target_label)
        target_hbox.addWidget(target_input)
        target_hbox.addWidget(button_change_target)
        vbox.addLayout(target_hbox)
        
        
        content_vbox = QVBoxLayout()

        content_label = QLabel("Target Content:")
        content_tree_view = QTreeView()

        # Set up a QFileSystemModel to display the directory content in the tree view
        content_file_system_model = QFileSystemModel()
        content_file_system_model.setRootPath(self.__current_target)
        content_tree_view.setModel(content_file_system_model)
        content_tree_view.setRootIndex(content_file_system_model.index(self.__current_target))

        # Hide other columns and show only the name column (0)
        for col in range(content_file_system_model.columnCount()):
            if col != 0:
                content_tree_view.setColumnHidden(col, True)

        content_vbox.addWidget(content_label)
        content_vbox.addWidget(content_tree_view)
        vbox.addLayout(content_vbox)
        
        duplicate_vbox = QVBoxLayout()
        
        duplicates_label = QLabel("Duplicates:")
        duplicates_label_status = QLabel("Status: " + self.__current_status)
        status_hbox = QHBoxLayout()
        status_hbox.addWidget(duplicates_label)
        label_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        status_hbox.addSpacerItem(label_spacer)
        status_hbox.addWidget(duplicates_label_status)
        duplicate_vbox.addLayout(status_hbox)
        
        duplicate_tree_view = QTreeView()
        # Set up a QFileSystemModel to display the directory content in the tree view
        # duplicate_file_system_model = QFileSystemModel()
        # root_path = self.__current_target  # Replace with the desired directory path
        # duplicate_file_system_model.setRootPath(root_path)
        # duplicate_tree_view.setModel(duplicate_file_system_model)
        # duplicate_tree_view.setRootIndex(duplicate_file_system_model.index(root_path))
        model = QStandardItemModel()
        duplicate_tree_view.setModel(model)

        custom_paths = [
            # "/path/to/custom_directory1",
            # "/path/to/custom_directory2",
            # # Add more custom paths as needed
            "/Applications/ArmGNUToolchain/12.2.mpacbti-rel1/arm-none-eabi/bin",
            "/Library/Audio/Apple Loops/Apple/01 Hip Hop/Afloat Beat.caf"
        ]

        for custom_path in custom_paths:
            item = QStandardItem(custom_path)
            model.appendRow(item)

        duplicate_vbox.addWidget(duplicate_tree_view)
        vbox.addLayout(duplicate_vbox)
        
        action_grid = QGridLayout()
        
        check_duplicates_content_button = QPushButton("Check Duplicates by Content", self)
        action_grid.addWidget(check_duplicates_content_button, 0, 0)
        
        check_duplicates_name_button = QPushButton("Check Duplicates by Name", self)
        action_grid.addWidget(check_duplicates_name_button, 0, 1)
        
        delete_duplicates_button = QPushButton("Delete All Duplicates", self)
        action_grid.addWidget(delete_duplicates_button, 1, 0)
        
        delete_duplicates_selectected_button = QPushButton("Delete Selected Duplicates", self)
        action_grid.addWidget(delete_duplicates_selectected_button, 1, 1)
        
        generate_report_button = QPushButton("Generate Report", self)
        action_grid.addWidget(generate_report_button, 2, 0)
        
        settings_button = QPushButton("Settings", self)
        action_grid.addWidget(settings_button, 2, 1)
        
        vbox.addLayout(action_grid)
        

        # load the hasher logo
        # pixmap = QPixmap(self.__RESOURCE_IMAGES_PATH + "hasher-logo.png")  
        # image_label = QLabel(self)
        # image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # image_label.setPixmap(pixmap)
        # vbox.addWidget(image_label)
        #
        # # Online section
        #
        # # put the google option
        # button_google = QPushButton("Connect with", self)
        # google_logo_pixmap = QPixmap(self.__RESOURCE_IMAGES_PATH + "Google_Logo.png")
        # google_logo_icon = QIcon(google_logo_pixmap)
        # button_google.setIcon(google_logo_icon)
        # button_google.setProperty("class", "option_button")
        # button_google.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        # button_google.clicked.connect(self.__handle_google_option)
        # vbox.addWidget(button_google)
        #
        # # put the onedrive option
        # button_one_drive = QPushButton("Connect with", self)
        # one_drive_pixmap = QPixmap(self.__RESOURCE_IMAGES_PATH + "Microsoft_Office_OneDrive_Logo.png")
        # one_drive_icon = QIcon(one_drive_pixmap)
        # button_one_drive.setIcon(one_drive_icon)
        # button_one_drive.setProperty("class", "option_button")
        # button_one_drive.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        # button_one_drive.clicked.connect(self.__handle_onedrive_option)
        # vbox.addWidget(button_one_drive)
        #
        # # Separator between online and offline section
        #
        # label = QLabel("—————————————————— or ——————————————————", self)
        # label.setProperty("class", "label_separator")
        # label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        # vbox.addWidget(label)
        #
        # # Offline section
        #
        # # put the offline option
        # button_offline = QPushButton("Offline", self)
        # button_offline.setProperty("class", "option_button")
        # button_offline.clicked.connect(self.__handle_offline_option)
        # vbox.addWidget(button_offline)

        central_widget.setLayout(vbox)
        
        
    def _createMenu(self):
        menu = self.menuBar().addMenu("&Menu")
        menu.addAction("&Exit", self.close)
    
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
    window = OfflineWindowGUI()
    window.show()
    sys.exit(app.exec())
    
