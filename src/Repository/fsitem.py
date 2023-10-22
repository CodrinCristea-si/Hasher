'''
Created on Oct 17, 2023

@author: cristeacodrin
'''
from __future__ import annotations
from enum import Enum



class ItemType(Enum):
    FILE = 0
    DIRECTORY = 1
    SYMLINK = 2

class FsItem:
    def __init__(self, id_item:int, item_name:str, item_type:ItemType, parent_id:int, item_size:int, last_modified: str, is_duplicate:bool, full_path:str = ""):
        self.__id = id_item # id of the item
        self.__name =  item_name # name of the item
        self.__type = item_type # type of the item (file, directory etc.)
        self.__parent = parent_id # parent id
        self.__size = item_size # item size
        self.__last_modified = last_modified # last time since item was modified
        self.__is_duplicate = is_duplicate # check if item is a duplicate or not
        self.__full_path = full_path # the absolute/relative path to item
    
    @property
    def item_id(self) -> int:
        return self.__id
    @property
    def item_name(self) -> str:
        return self.__name
    @property
    def item_type(self) -> ItemType:
        return self.__type
    @property
    def parent_id(self) -> int:
        return self.__parent
    @property
    def item_size(self) -> int:
        return self.__size
    @property
    def is_duplicate(self) -> bool:
        return self.__is_duplicate
    @property
    def last_modified(self) -> str:
        return self.__last_modified
    @property
    def item_path(self) -> str:
        return self.__full_path
    @is_duplicate.setter
    def is_duplicate(self, value:bool) -> None:
        self.__is_duplicate = value
    
    def __eg__(self, other) -> bool:
        return self.__id == other.item_id and \
             self.__name == other.item_name and \
             self.__type == other.item_type and \
             self.__parent == other.parent_id and \
             self.__size == other.item_size and \
             self.__is_duplicate == other.is_duplicate and \
             self.__last_modified == other.last_modified and \
             self.__full_path == other.item_path
    
    def __ne__(self, other) -> bool:
        return not self.__eg__(other)
    
    def __str__(self):
        return f"FsItem: %s" %(self.__dict__)
    
    def __repr__(self):
        return self.__str__()
    
class FsItemFormatter:
    
    __GENERAL_FORMAT_STRUCT_BYTE_STRING = '<IIIQ%dsBQQ%ds%ds?' # bytes struct packing/unpacking, 3 I for 3 strings
    
    @staticmethod
    def write_bytes(item: FsItem) -> bytes:
        """
        Converts the FsItem objects to a bytes like array
            :param item: the FsItem object to be represented
            :return: A bytes like array which is the little-endian bytes object representation 
        """
        from struct import pack
        len_name_str = len(item.item_name.encode('utf-8'))
        len_last_modified_str = len(item.last_modified.encode('utf-8'))
        len_full_path = len(item.item_path.encode('utf-8'))
        FORMAT_STRUCT_BYTE_STRING = FsItemFormatter.__GENERAL_FORMAT_STRUCT_BYTE_STRING % (len_name_str, len_last_modified_str, len_full_path)
        #print(type(item.item_id), type(item.item_id))
        item_bytes = pack(FORMAT_STRUCT_BYTE_STRING,  # little-endian >
                           len_name_str, # length of the name string unsigned int I
                           len_last_modified_str, # length of the last_modified string unsigned int I
                           len_full_path, # length of the path str unsigned int I
                           item.item_id, # unsigned long long Q
                           item.item_name.encode('utf-8'), # char[] s
                           item.item_type.value, # char B
                           item.parent_id, # unsigned long long Q
                           item.item_size, # unsigned long long Q
                           item.last_modified.encode('utf-8'), # char[] s
                           item.item_path.encode('utf-8'), # char[] s
                           item.is_duplicate # bool ?
                             )
        return item_bytes
    
    @staticmethod
    def read_bytes(item_bytes:bytes) -> FsItem: 
        """
        Converts the bytes array representation of a FsItem object into the object itself
            :param item_bytes: The bytes array representation of a FsItem object
            :return: The object itself
            :raise Exception: For invalid bytes format for the item_bytes
        """
        from struct import unpack
        
        item = None
        len_name_str = int.from_bytes(item_bytes[:4], "little") # length for I (4 bytes)
        len_last_modified_str = int.from_bytes(item_bytes[4:8], "little")
        len_full_path = int.from_bytes(item_bytes[8:12], "little")
        FORMAT_STRUCT_BYTE_STRING = FsItemFormatter.__GENERAL_FORMAT_STRUCT_BYTE_STRING % (len_name_str, len_last_modified_str, len_full_path)
        # try:
        item_props = unpack(FORMAT_STRUCT_BYTE_STRING, item_bytes)
        item = FsItem(item_props[3], # id
                      item_props[4].decode(), # name
                      ItemType(int(item_props[5])), # type
                      item_props[6], # parent id
                      item_props[7], # size
                      item_props[8].decode(), # last modified,
                      item_props[10], # is duplicate
                      item_props[9].decode() # full path
                      )
        # except Exception as e:
        #     print(e)
        return item
    
    """
    In primul rand, in loc sa primim un covor de culoare VERDE 100X200 cm am primit un covor de alta culoare dar aceeasi marime (de culoare maro si este).
In al doilea rand, covorul de culoare VERDE 100x300( asa cum scrie si pe eticheta) in realitate este de fapt  de 100x200 cm in urma unei masurari.
In al treilea rand, in loc sa primesc un covor de culoare ROSIE 100x200 am primit un covor de culoare ROSIE 100x300, diferenta fiind dimensiunile.
Recomandarea mea ar fi sa returnez covorul de culoare MARO si cel de culoare ROSIE 100x300, si sa primesc un covor de culoare VERDE 100x300 (care chiar sa fie de 100x300) si un covor ROSU 100x200. Covorul cu eticheta defecta de culoare VERDE 100x300, care in realitate este de 100x200 il putem pastra deoarece este inclus in comanda initiala.

Doresc sa returnez 2 covoare (cel de culoare MARO si cel de culoare ROSIE 100x300) si sa primesc in schimb alte 2 covoare ( cel de culoare VERDE 100x300 sicel de culoare ROSIE 100x200) pe care trebuia sa le primesc initial.

Buna ziua, mai jos aveti poze cu produsele livrate. In poza cu cele 6 covoare se poate vedea diferenta de nuanta intre cele 2 covoare de culoare VERDE, cele 3 de culoare ROSIE si altul de alta culoare (am mai adaugat inca o poza cu 3 covoare pentru a se putea vedea diferenta de culoare). In alta poza puteti vedea un covor de culoare ROSIE de dimensiune 100x300 in loc de 100x200 cum comandasem initial ( covorul a fost masurat si are intradevar 100x300 dimensiunile). In alte poze gasiti un covor de culoare VERDE care are dimensiunea pe eticheta 100x300, dar in realitate are 100x200 (am pus poze cu masuratorile). In principiu despre acel covor putem spune ca este ok, aveam oricum nevoie de un covor VERDE 100x200, dar tot avem nevoie de un covor de culoare VERDE 100x300. Mai jos voi lista exact ce am primit:ROSU 100x300 (trebuia 100x200)ROSU 100x150 (este ok)ROSU 60x90 (este ok)VERDE 140x215 (este ok)VERDE 100x300( in realitate este 100x200, greseala de eticheta, se accepta ca fiind ok)ALTA CULOARE 100x200 ( nu era in comanda, trebuia VERDE)
Ne lipseste covorul ROSU 100x200 si un covor VERDE 100x300 ( intrucat ala cu eticheta gresita il putem considera ca fiind covorul VERDE 100x200 lipsa). Propun un schimb intre covoarele care ne lipsesc (pentru a se respecta comanda intiala), si covorul ROSU 100x300 si cel de ALTA CULOARE (cele pe care le avem in plus). Sau pastrez covorul ROSU ( desi am unul cu dimensiuni mai mari) si schimbam doar covorul de ALTA CULOARE (care are o dimensiune mai mica decat cea ceruta 100x200) cu cel de culoare VERDE (100x300), deci teoretic n ar trebui sa fie nicio schimbare de pret, adica nu ar mai trebui sa platesc vreo diferenta intrucat toate covoarele sunt de la acelasi producator.

"""
