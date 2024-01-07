'''
Created on Aug 15, 2023

@author: cristeacodrin
'''
import ijson
import json
import os
from enum import Enum
from multiprocessing import Lock


class ItemCodifier(Enum):
        ITEM_LOCATION_CODE = "path"
        ITEM_HASH_CODE = "hash"
        ITEM_SIZE_CODE = "size"
        ITEM_DUPLICATES_CODE = "duplicates"
        RESULTS_CODE = "results"

class DuplicateRepository:
    __STORAGE_FILE = "offline_storage.json"
    __ITEM_REPR = {
        ItemCodifier.ITEM_LOCATION_CODE:"",
        ItemCodifier.ITEM_HASH_CODE:"",
        ItemCodifier.ITEM_SIZE_CODE:"",
        ItemCodifier.ITEM_DUPLICATES_CODE:[]
        }
    
    def __init__(self) -> None:
        """
        Nothing to add yet
        """
        self.__mutex_progress = Lock() # thread safe lock for some methods
    
    def __create_data_item(self, data_location:str, data_size:int, data_hash:str) -> dict:
        """
        Creates a data json item for a specific entity defined by these parameters:
            :param data_location: - string object representing the path location of the object 
            :param data_size: - int object representing the size of the object 
            :param data_hase: - string object representing the hash id of the object 
            :return: A dictionary object representing the item representation (__ITEM_REPR)
        """
        return {
            ItemCodifier.ITEM_LOCATION_CODE.value: data_location,
            ItemCodifier.ITEM_HASH_CODE.value: data_hash,
            ItemCodifier.ITEM_SIZE_CODE.value: data_size,
            ItemCodifier.ITEM_DUPLICATES_CODE.value:[]
        }
    
    def __create_json_results(self) -> dict:
        """
        Returns the json content model of the storage file  
        """
        return {
            ItemCodifier.RESULTS_CODE.value: []
            }
        
    
    def begin_session(self) -> None:
        """
        This function prepares the storage file for processing ( creation and preparation of the internal model)
        This function is marked as not thread safe
        """
        # if no storage file then create one
        if not os.path.exists(self.__STORAGE_FILE):
            with open(self.__STORAGE_FILE, "w") as file:
                file.write("")
        # save the internal json results model
        with open(self.__STORAGE_FILE, "w") as file:
            results = self.__create_json_results()
            results = json.dumps(results)
            file.write(results)
    #
    # def __check_if_storage_file_exists(self):
    #     if not os.path.exists(self.__STORAGE_FILE):
    #         os.
    
    def add_data(self, data_location:str, data_size:int, data_hash:str) -> int:
        """
        This function adds an entry/object defined by the parameters to the storage file
            :param data_location: - string object representing the path location of the object 
            :param data_size: - int object representing the size of the object 
            :param data_hase: - string object representing the hash id of the object 
            :return: A status code with the following definition
                -> 0 - the object has not been saved
                -> 1 - the object has been added as a duplicate
                -> 2 - the object has been added as new entry
        This function is marked as thread safe
        """
        status_return = 0 # not saved
        added = False
        self.__mutex_progress.acquire()
        if os.path.getsize(self.__STORAGE_FILE) > 0:
            try:
                with open(self.__STORAGE_FILE, "r") as storage_file:
                    objects_generator = ijson.items(storage_file, ItemCodifier.RESULTS_CODE.value + ".item")
                    # Create a new JSON file for writing the modified data
                    with open("temp_" + self.__STORAGE_FILE, "w") as modified_file:
                        modified_file.write('{ "' + ItemCodifier.RESULTS_CODE.value + '": [')
                        is_first_element = True # needed so that the first entity should not start with ","
                        # Write the initial part of the JSON file until the target array is encountered
                        for item in objects_generator:
                            if item.get(ItemCodifier.ITEM_HASH_CODE.value) == data_hash:
                                item.get(ItemCodifier.ITEM_DUPLICATES_CODE.value).append(data_location)
                                added = True
                                status_return = 1 # duplicate
                            item_json_repr = json.dumps(item)
                            if is_first_element:
                                modified_file.write(item_json_repr)
                                is_first_element = False
                            else:
                                modified_file.write(",\n" + item_json_repr)
                        if not added: # if no duplicates where found then crate a separate entity
                            item = self.__create_data_item(data_location, data_size, data_hash)
                            item_json_repr = json.dumps(item)
                            if is_first_element:
                                modified_file.write(item_json_repr)
                                is_first_element = False
                            else:
                                modified_file.write(",\n" +item_json_repr)
                            status_return = 2 # separate entity
                        modified_file.write("]}\n")
                os.remove(self.__STORAGE_FILE)
                os.rename("temp_" + self.__STORAGE_FILE, self.__STORAGE_FILE)
            except Exception as e:
                print(e)
        else:
            # if there is no storage file then create it and populate it with the first entity
            try:
                with open(self.__STORAGE_FILE, "w") as modified_file:
                    modified_file.write('{ "' + ItemCodifier.RESULTS_CODE.value + '": [')
                    item = self.__create_data_item(data_location, data_size, data_hash)
                    print(item)
                    item_json_repr = json.dumps(item)
                    print(item_json_repr)
                    modified_file.write(item_json_repr)
                    modified_file.write("] }\n")
            except Exception as e:
                print(e)
        self.__mutex_progress.release()
        return status_return
        
    def get_hash_for_entity(self, data_location:str) -> str | None:
        """
        Gets the hash id for an entity by its location
            :param data_location: - string object representing the path location of the object 
            :return: A string object representing the hash id of the object 
        This function is marked as thread safe
        """
        hash_ent = None
        self.__mutex_progress.acquire()
        if os.path.getsize(self.__STORAGE_FILE) > 0:     
            # if there is something in the file then parse it, find the object and get it's hash
            with open(self.__STORAGE_FILE, "r") as storage_file:
                objects_generator = ijson.items(storage_file, ItemCodifier.RESULTS_CODE.value + ".item")
                for item in objects_generator:
                    if item.get(ItemCodifier.ITEM_LOCATION_CODE.value) == data_location:
                        hash_ent = item.get(ItemCodifier.ITEM_HASH_CODE.value)
                        break
        self.__mutex_progress.release()
        return hash_ent
    
    def get_all_duplicates_full_path(self) -> list:
        """
        Gets the absolute path for all duplicates
            :return: A list of strings containing the full/ absolute path for each duplicate
        """
        full_paths = []
        self.__mutex_progress.acquire()
        if os.path.getsize(self.__STORAGE_FILE) > 0:     
            # if there is something in the file then parse it, find the object and get it's hash
            with open(self.__STORAGE_FILE, "r") as storage_file:
                objects_generator = ijson.items(storage_file, ItemCodifier.RESULTS_CODE.value + ".item")
                for item in objects_generator:
                    full_paths += item.get(ItemCodifier.ITEM_DUPLICATES_CODE.value)
        self.__mutex_progress.release()
        return full_paths
        