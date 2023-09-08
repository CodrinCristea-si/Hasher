'''
Created on Aug 15, 2023

@author: cristeacodrin
'''

from abc import ABC

class Operator(ABC):
    
    def get_file_size(self, file_path:str) -> int:
        """
        Gets the file size based on the file path
            :param file_path: A string representing the file path 
            :return: An integer with :
                -> value > 0 - representing the file size
                -> value = -1 - the file_path is not a file
                -> value = -2 - the file_path is invalid 
        """
        raise NotImplementedError("Function call from interface")
    
    def get_file_chunks(self, file_path:str, nr_chunks:int) -> list:
        """
        Gets a list file's chuncks located at filr_path
            :param file_path: A string representing the file path 
            :param nr_chunks: An integer representing the number of chunks that needs to be extracted
            :return: A list of content file's chunks or empty list if the file_path is invalid
        """
        raise NotImplementedError("Function call from interface")
    
    def get_dir_size(self, dir_path:str) -> int:
        """
        Gets the directory size based on the directory's path
            :param dir_path: A string representing the directory's path 
            :return: An integer with :
                -> value > 0 - representing the directory size
                -> value = -1 - the dir_path is not a directory
                -> value = -2 - the dir_path is invalid
        """
        raise NotImplementedError("Function call from interface")
    
    def get_file_name_from_path(self, file_path:str) -> str:
        """
        Gets the file name based on it's path
            :param file_path: A string representing the file's path
            :return: The name of the directory
        """
        raise NotImplementedError("Function call from interface")
    
    def get_directory_name_from_path(self, dir_path:str) -> str:
        """
        Gets the directory name based on it's path
            :param dir_path: A string representing the directory's path
            :return: The name of the file
        """
        raise NotImplementedError("Function call from interface")
    
    def get_content_of_directory(self, directory_path) -> tuple:
        """
        Get the files and subdirectories of the directory
            :param directory_path: A string representing the directory's path
            :return: A 2 elements tuple (files, subdirectories)  
        """
        raise NotImplementedError("Function call from interface")
    