'''
Created on Aug 13, 2023

@author: cristeacodrin
'''
import sys
import os
from Utils.secure_debugging import enable_debug_mode

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
    QSpacerItem, 
    QGridLayout,
    QFileDialog,
    QStyle,
    QStyledItemDelegate
)
#from PySide6.QtWidgets import QFileSystemModel

from PyQt6.QtGui import QPixmap, QIcon, QFileSystemModel, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal

from Business.offline_controller import OfflineController
from UI.ui_item import UIItemType, UIItem

class CustomDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.isValid():
            item = index.model().itemFromIndex(index)
            if item is not None:
                text = item.text()
                icon = item.icon()
                x_offset = option.rect.left() + 30  # Adjust the spacing as needed
                y_offset = option.rect.top() + 10   # Adjust the vertical positioning

                painter.drawPixmap(x_offset - 30, y_offset - 5, icon.pixmap(16, 16))  # Draw the icon
                painter.drawText(x_offset, y_offset, text)  # Draw the text



class OfflineWindowGUI(QWidget):
    def __init__(self):
        """
        Draw the main popup for connection
        """
        #self.__current_target = "/Users/cristeacodrin/eclipse-workspace/Hasher/src/testing/simulation_ffline_hasher" # default should be /
        self.__current_target = "/Users/cristeacodrin/eclipse-workspace/Hasher/src/testing/small_scale/by_content"
        self.__current_status = "UP TO DATE"
        self.__dups_list = []
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
        #central_widget = QWidget(self)
        #self.setCentralWidget(central_widget) 
        
        # menu layout
        vbox = QVBoxLayout()
        


        target_hbox = QHBoxLayout()
        target_label = QLabel("Current target:", self)
        self.__target_input = QLineEdit()
        self.__target_input.setText(self.__current_target)
        button_change_target = QPushButton("Change Target", self)
        button_change_target.clicked.connect(self.browse_target)
        
        # self.__target_path_changed = pyqtSignal(str)
        # self.__target_path_changed.connect(self.update_target_path)
        
        target_hbox.addWidget(target_label)
        target_hbox.addWidget(self.__target_input)
        target_hbox.addWidget(button_change_target)
        vbox.addLayout(target_hbox)
        
        
        content_vbox = QVBoxLayout()

        content_label = QLabel("Target Content:")
        self.__content_tree_view = QTreeView()

        # Set up a QFileSystemModel to display the directory content in the tree view
        self.__content_file_system_model = QFileSystemModel()
        self.__content_file_system_model.setRootPath(self.__current_target)
        self.__content_tree_view.setModel(self.__content_file_system_model)
        self.__content_tree_view.setRootIndex(self.__content_file_system_model.index(self.__current_target))

        # Hide other columns and show only the name column (0)
        for col in range(self.__content_file_system_model.columnCount()):
            if col != 0:
                self.__content_tree_view.setColumnHidden(col, True)

        content_vbox.addWidget(content_label)
        content_vbox.addWidget(self.__content_tree_view)
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
        
                # Set up a QFileSystemModel to display the directory content in the tree view
        # duplicate_file_system_model = QFileSystemModel()
        # root_path = self.__current_target  # Replace with the desired directory path
        # duplicate_file_system_model.setRootPath(root_path)
        # duplicate_tree_view.setModel(duplicate_file_system_model)
        # duplicate_tree_view.setRootIndex(duplicate_file_system_model.index(root_path))
        
        self.__duplicate_tree_view = QTreeView()

        self.__model_dups = QStandardItemModel()
        self.__duplicate_tree_view.setModel(self.__model_dups)
        # delegate = CustomDelegate()
        # self.__duplicate_tree_view.setItemDelegate(delegate)
        self.__duplicate_tree_view.clicked.connect(self.__update_dups_list_children)

        # custom_paths = [
        #     "/Applications/ArmGNUToolchain/12.2.mpacbti-rel1/arm-none-eabi/bin",
        #     "/Library/Audio/Apple Loops/Apple/01 Hip Hop/Afloat Beat.caf"
        # ]
        #self.__update_list_dups([])
        duplicate_vbox.addWidget(self.__duplicate_tree_view)
        vbox.addLayout(duplicate_vbox)
        
        action_grid = QGridLayout()
        
        check_duplicates_content_button = QPushButton("Check Duplicates by Content", self)
        check_duplicates_content_button.clicked.connect(self.handle_check_cups_by_content)
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

        #central_widget.setLayout(vbox)
        self.setLayout(vbox)
    
    def browse_target(self):
        #options = QFileDialog.ShowDirsOnly
        dialog = QFileDialog(self)
        #dialog.setFileMode(QFileDialog.Option.ShowDirsOnly)
        directory_path = QFileDialog.getExistingDirectory(self, "Open Directory", "", options = QFileDialog.Option.ShowDirsOnly)
        self.__current_target = directory_path
        self.update_target_path(directory_path)
    
    def update_target_path(self, new_target_path):
        self.__target_input.setText(new_target_path)
        self.__content_file_system_model.setRootPath(self.__current_target)
        self.__content_tree_view.setRootIndex(self.__content_file_system_model.index(self.__current_target))
    
    def __create_standard_item_from_ui_item(self, ui_item:UIItem):
        standard_item = QStandardItem(ui_item.item_name)
        pixmap_icon = None
        if ui_item.item_type == UIItemType.DIRECTORY:
            pixmap_icon = QStyle.StandardPixmap.SP_DirIcon
        elif ui_item.item_type == UIItemType.SYMLINK:
            pixmap_icon = QStyle.StandardPixmap.SP_FileLinkIcon
        else:
            pixmap_icon = QStyle.StandardPixmap.SP_FileIcon
        icon = self.style().standardIcon(pixmap_icon)
        standard_item.setIcon(icon)
        standard_item.setData(ui_item, Qt.ItemDataRole.UserRole)
        return standard_item
    
    def __load_duplicates_for_std_item(self, item_model: QStandardItem):
        cont =  OfflineController()
        ui_item = item_model.data(Qt.ItemDataRole.UserRole)
        dups_childs = cont.load_duplicates_for_target_by_id(ui_item.item_id)
        dups_childs_item = []
        for ui_item in dups_childs:
            item = self.__create_standard_item_from_ui_item(ui_item)
            dups_childs_item.append(item)
        item_model.appendRow(dups_childs_item)
    
    def __update_dups_list_children(self, index):
        cont =  OfflineController()
        #print(index.row(), index.column(), index.parent_id())
        if not index.isValid(): 
            return
        clicked_item_model = self.__model_dups.itemFromIndex(index)
        clicked_ui_item = clicked_item_model.data(Qt.ItemDataRole.UserRole)
        if clicked_ui_item.item_type == UIItemType.DIRECTORY:
            if not clicked_item_model.hasChildren():
                dups_childs = cont.load_duplicates_for_target_by_id(clicked_ui_item.item_id)
                dups_childs_item = []
                for ui_item in dups_childs:
                    item = self.__create_standard_item_from_ui_item(ui_item)
                    if ui_item.item_type == UIItemType.DIRECTORY:
                        self.__load_duplicates_for_std_item(item)
                    dups_childs_item.append(item)
                clicked_item_model.appendRow(dups_childs_item)
            else:
                clicked_item_model.removeRows(0, clicked_item_model.rowCount())
                self.__load_duplicates_for_std_item(clicked_item_model)
            # how_many_children = clicked_item_model.rowCount()
            # self.__model_dups.removeRows(0, how_many_children, clicked_item_model.index())
        
        
    # def __update_list_dups(self,list_items:list):
    #     self.__model_dups = QStandardItemModel()
    #     self.__dups_list = list_items
    #     for el in self.__dups_list:
    #         print(el.item_id, el.item_rank)
    #     self.__duplicate_tree_view.setModel(self.__model_dups)
    #     for ui_item in list_items:
    #         item = self.__create_standard_item_from_ui_item(ui_item)
    #         self.__model_dups.appendRow(item)

    def __print_data_list(self, data, tab_level, file_handle = None):
        for el in data:
            tab_level_str = "".join(["   " for _ in range(tab_level)])
            item = el[0]
            childs = el[1]
            if item.is_duplicate:
                    str_to_print = tab_level_str + "- %s (%d) !*!"%(item.item_name,item.item_size)
            else:
                str_to_print = tab_level_str + "- %s (%d)"%(item.item_name,item.item_size)
            if file_handle is not None:
                file_handle.write(str_to_print+"\n")
            print(str_to_print)
            self.__print_data_list(childs, tab_level+1, file_handle)

    def handle_check_cups_by_content(self):
        self.__model_dups.clear()
        cont =  OfflineController()
        cont.check_duplicates_by_content(self.__current_target)
        dups_items = cont.load_duplicates_for_target(self.__current_target)
        for ui_item in dups_items:
            item = self.__create_standard_item_from_ui_item(ui_item)
            self.__load_duplicates_for_std_item(item)
            self.__model_dups.appendRow(item)
            
        dups = cont.get_all_duplicates()
        for el in dups:
            print(el)
        
        data = cont.get_graph_representation()
        
        if data == [] or data is None:
            print("empty data")
        else:
            print(len(data))
            with open("graph.txt","w") as file:
                self.__print_data_list(data, 0,file)
        print("done")

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

class TestOfflineWindowGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        window = OfflineWindowGUI()
        self.setCentralWidget(window)

if __name__ == "__main__":
    enable_debug_mode()
    app = QApplication(sys.argv)
    window = TestOfflineWindowGUI()
    window.show()
    sys.exit(app.exec())
    
