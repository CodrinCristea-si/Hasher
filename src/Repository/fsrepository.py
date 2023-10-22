'''
Created on Sep 27, 2023

@author: cristeacodrin
'''
import os
from enum import Enum
from Repository.fsitem import *


class FsSessionType(Enum):
    NOT_STARTED = 0
    STARTED = 1
    ENDED = 2


class FSRepository:
    __STORAGE_ITEM_FILE = "fs_analysis.temp"
    __STORAGE_ITEM_FILE_AUX = "fs_analysis_aux.temp"
    __STORAGE_CHILD_FILE = "fs_child.temp"
    __ITEM_CURRENT_ID = 1000
    __ITEM_SEPARATOR_FILE = b'%-2a0~%'

    def __init__(self):
        self.__fs_item_child = {}
        self.__session_stage = FsSessionType.NOT_STARTED
    
    def __write_item_to_file(self, file_handler, item_bitarray:bytes) -> None:
        file_handler.write(item_bitarray + self.__ITEM_SEPARATOR_FILE)
    
    def __save_item_to_file(self, item: FsItem) -> int:
        """
        Save the FsItem object to the storage file
            :param item: An FsItem object
            :return: An integer representing status code: 0 - everything went great, everything else is an error
        """
        with open(self.__STORAGE_ITEM_FILE, "ab") as file:
            #item_bitarray =  pickle.dumps(item)
            item_bitarray = FsItemFormatter.write_bytes(item)
            #print(len(item_bitarray), len(item_bitarray + b'\n'))
            self.__write_item_to_file(file, item_bitarray)
        return 0
    
    def __read_item_from_file(self, file_handler):
        item_bitarray = b''
        potential_separator = [ b'0' for _ in range(len(self.__ITEM_SEPARATOR_FILE)) ]
        while True:
            byte_el = file_handler.read(1)
            #print(byte_el)
            if byte_el == b'' or byte_el is None: # eof
                break
            # to check if separator is reached a buffer with null element is used and is filled with the last len(self.__ITEM_SEPARATOR_FILE) 
            # elements from the current read sequence as shown 0000000 -> 000000% -> 00000%- -> 0000%-2 -> ... -> %-2a0~%
            # if the last len(self.__ITEM_SEPARATOR_FILE) elements that have been read is the actual separator then an item has been read 
            potential_separator += byte_el
            potential_separator = potential_separator[1:]
            if potential_separator == self.__ITEM_SEPARATOR_FILE or potential_separator == [ el for el in self.__ITEM_SEPARATOR_FILE]:
                break
            item_bitarray += byte_el
        # the final bytearray is composed of item bytes +__ITEM_SEPARATOR_FILE bytes - 1 ( -1 because its then clear the separator has been reached
        item_bitarray = item_bitarray[:len(item_bitarray) - len(self.__ITEM_SEPARATOR_FILE) + 1]
        return item_bitarray
    
    def read_item_from_file(self, file_handler):
        return self.__read_item_from_file(file_handler)
    
    def __load_item_generic(self, property_key:any, property_value:any) -> FsItem|None:
        """
        Load an FsItem object from the storage file by its id
            :param item_id: The id of the required object
            :return: The corresponding FsItem object or None if there is no object with that id
        """
        item = None
        with open(self.__STORAGE_ITEM_FILE, "rb") as file:
            #item_bitarray =  file.readline()[:-1] # remove the \n
            item_bitarray = self.__read_item_from_file(file)
            while item_bitarray != "" and item_bitarray != b'' and item_bitarray is not None:
                #item_read = pickle.loads(item_bitarray)
                item_read = FsItemFormatter.read_bytes(item_bitarray)
                if getattr(item_read,property_key, None) == property_value:
                    item = item_read
                    break
                item_bitarray = self.__read_item_from_file(file)
        return item

    def __load_items_generic(self, property_key:any, property_values:list) -> list:
        # create a dictionary with found items 
        items_found_dict = {}
        for i_value in property_values:
            items_found_dict[i_value] = None
        item = None
        to_found = len(property_values) # in case we find all items
        with open(self.__STORAGE_ITEM_FILE, "rb") as file:
            #item_bitarray =  file.readline()[:-1] # remove the \n
            item_bitarray = self.__read_item_from_file(file)
            while item_bitarray != "" and item_bitarray != b'' and item_bitarray is not None:
                #item_read = pickle.loads(item_bitarray)
                item_read = FsItemFormatter.read_bytes(item_bitarray)
                if getattr(item_read,property_key, None) in property_values:
                    items_found_dict[getattr(item_read,property_key, None)] = item_read
                    to_found -= 1 
                    if to_found <= 0:
                        break
                item_bitarray = self.__read_item_from_file(file) 
        items_to_return = []
        for i_value in property_values:
            items_to_return.append(items_found_dict.get(i_value)) 
        return items_to_return

    def load_item_by_id(self, item_id:int) :
        """
        Load an FsItem object from the storage file by its id
            :param item_id: The id of the required object
            :return: The corresponding FsItem object or None if there is no object with that id
        """
        return self.__load_item_generic("item_id", item_id)

    def load_items_by_id(self, items_id:list) -> list:
        """
        Load a list of FsItem objects from the storage file with a list of ids
            :param items_id: Id list for the required objects
            :return: A list of FsItem objects that could contain some None values depending if the object with a specific id exists
                Each id from the items_id on the X position will have a corresponding FsItem object or None on the X position on the returned list
        """
        return self.__load_items_generic("item_id", items_id)
    
    def load_items_by_parent_id(self, parent_id):
        items_found = []
        with open(self.__STORAGE_ITEM_FILE, "rb") as file:
            #item_bitarray =  file.readline()[:-1] # remove the \n
            item_bitarray = self.__read_item_from_file(file)
            while item_bitarray != "" and item_bitarray != b'' and item_bitarray is not None:
                #item_read = pickle.loads(item_bitarray)
                item_read = FsItemFormatter.read_bytes(item_bitarray)
                if item_read.parent_id == parent_id:
                    items_found.append(item_read)
                item_bitarray = self.__read_item_from_file(file) 
        return items_found
    
    def load_item_by_path(self, item_path:str) -> FsItem|None:
        """
        Load an FsItem object from the storage file by its path
            :param item_id: The path of the required object
            :return: The corresponding FsItem object or None if there is no object with that path
        """
        return self.__load_item_generic("item_path", item_path)
    
    def add_fs_item(self, name:str, type:ItemType, parent_id:int, size:int, last_modified:str, path:str = "") -> int:
        """
        Add a file system item to the repository
            :param name: The name of the item (a string item)
            :param type: The type of the item (an ItemType object)
            :param parent_id: The id of the item's parent (an integer value)
            :param size: The size of the item ( an integer value)
            :param last_modified: The last time since the object has been modified ( a string object)
            :return: The id of the created item 
        """
        # create new FsItem element
        item = FsItem(self.__ITEM_CURRENT_ID, name, type, parent_id, size, last_modified, False, path)
        self.__ITEM_CURRENT_ID += 1

        # add child to parent
        if self.__fs_item_child.get(parent_id) is None:
            self.__fs_item_child[parent_id] = []
        self.__fs_item_child[parent_id].append(item)
            
        # save item to file
        self.__save_item_to_file(item)
        return item.item_id
    
    def begin_session(self):
        """
        This function creates a new storage session. The previous storage files are cleared.
            :return: A status error. 0 - all ok, -1 - there is an existing session
        """
        if not self.__check_if_can_start_new_session():
            return -1
        self.__ITEM_CURRENT_ID = 1000
        self.__fs_item_child = {}
        with open(self.__STORAGE_ITEM_FILE, "w") as file:
            file.write("")
        with open(self.__STORAGE_CHILD_FILE, "w") as file:
            file.write("")
        self.__session_stage = FsSessionType.STARTED
        return 0
        
    def __save_child_to_file(self):
        """
        Save the children list ton a storage file 
        """
        with open(self.__STORAGE_CHILD_FILE, "w") as file:
            for i_id in self.__fs_item_child.keys():
                for child in self.__fs_item_child.get(i_id):
                    file.write(str(i_id) + ":" + str(child) + "\n")
    
    def is_session_ended(self) -> bool:
        """
        Check if the current storage session is ended
            :return: True if the current session has been ended, False otherwise 
        """
        return self.__session_stage == FsSessionType.ENDED
    
    def __check_if_can_start_new_session(self) -> bool:
        """
        Check if the current storage session can be started
            :return: True if the current session can be started, False otherwise 
        """
        return not self.__session_stage == FsSessionType.STARTED # cannot start the same session twice
    
    def __check_if_can_end_session(self) -> bool:
        """
        Check if the current storage session can be ended
            :return: True if the current session has been ended, False otherwise 
        """
        return self.__session_stage == FsSessionType.STARTED # cannot end the a not started session
        
    def end_session(self) -> int:
        """
        End the current storage session
            :return: A status error. 0 - all ok, -1 - the session is not started
        """
        if not self.__check_if_can_end_session():
            return -1
        self.__save_child_to_file()
        self.__fs_item_child = {}
        self.__session_stage = FsSessionType.ENDED
        return 0
    
    def mark_all_duplicates(self, duplicates_path:list) -> int:
        if duplicates_path is None:
            return -1
        items_found = []
        with open(self.__STORAGE_ITEM_FILE, "rb") as file:
            with open(self.__STORAGE_ITEM_FILE_AUX, "wb") as file_aux:
                item_bitarray = self.__read_item_from_file(file)
                while item_bitarray != "" and item_bitarray != b'' and item_bitarray is not None:
                    #item_read = pickle.loads(item_bitarray)
                    item_read = FsItemFormatter.read_bytes(item_bitarray)
                    if item_read.item_path in duplicates_path:
                        item_read.is_duplicate = True
                    item_bitarray = FsItemFormatter.write_bytes(item_read)
                    self.__write_item_to_file(file_aux, item_bitarray)
                    item_bitarray = self.__read_item_from_file(file) 
        os.remove(self.__STORAGE_ITEM_FILE)
        os.rename(self.__STORAGE_ITEM_FILE_AUX, self.__STORAGE_ITEM_FILE)
        return 0
    

        