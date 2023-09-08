'''
Created on Aug 15, 2023

@author: cristeacodrin
'''
import os
from Business.operator import Operator

class OfflineOperator(Operator):
    
    __CHUNK_SIZE = 100
    
    def __init__(self):
        pass
    
    def get_file_size(self, file_path:str) -> int:
        """
        Gets the file size based on the file path
            :param file_path: A string representing the file's path 
            :return: An integer with :
                -> value > 0 - representing the file size
                -> value = -1 - the file_path is not a file
                -> value = -2 - the file_path is invalid 
        """
        if not os.path.exists(file_path):
            return -2
        if not os.path.isfile(file_path):
            return -1
        size = os.path.getsize(file_path)
        return size
    
    def get_file_chunks(self, file_path:str, nr_chunks:int) -> list:
        """
        Gets a list file's chuncks located at filr_path
            :param file_path: A string representing the file's path 
            :param nr_chunks: An integer representing the number of chunks that needs to be extracted
            :return: A list of content file's chunks or empty list if the file_path is invalid
        """
        file_size = self.get_file_size(file_path)
        # if the file does not exist, then no chunks 
        if file_size <= 0:
            return []
        chunks = []
        # if the file size is less then the minimum size of chunks, then the chunk's size shrinks,
        # and the whole file is split into chunks
        if file_size <= nr_chunks * self.__CHUNK_SIZE:
            with open(file_path, 'rb') as file:
                bytes_per_chunk = file_size // nr_chunks
                remaining_chunks = nr_chunks
                
                while remaining_chunks > 0:
                    # Read a chunk of data
                    chunk_data = file.read(bytes_per_chunk)
                    if not chunk_data: # unlikely case but possible
                        break  # End of file
        
                    # Append the chunk to the list
                    chunks.append(chunk_data)
                    remaining_chunks -= 1
        # otherwise nothing changes
        else:
            with open(file_path, 'rb') as file:
                bytes_per_chunk = file_size // nr_chunks
                remaining_chunks = nr_chunks
                
                # one chunk is reserved for the one of the file
                while remaining_chunks > 1:
                    # Read a chunk of data
                    chunk_data = file.read(self.__CHUNK_SIZE)
                    if not chunk_data: # unlikely case but possible
                        break  # End of file
        
                    # Append the chunk to the list
                    chunks.append(chunk_data)
                    remaining_chunks -= 1
        
                    # Seek to the next position to distribute chunks evenly
                    if remaining_chunks > 1:
                        next_position = file.tell() - self.__CHUNK_SIZE + bytes_per_chunk
                        file.seek(next_position)
                
                # get the chunk at the end of the file
                next_position = file_size - self.__CHUNK_SIZE 
                file.seek(next_position)
                chunk_data = file.read(self.__CHUNK_SIZE)
                chunks.append(chunk_data)
        return chunks 
    
    def get_dir_size(self, dir_path:str) -> int:
        """
        Gets the directory size based on the directory's path
            :param dir_path: A string representing the directory's path 
            :return: An integer with :
                -> value > 0 - representing the directory size
                -> value = -1 - the dir_path is not a directory
                -> value = -2 - the dir_path is invalid
        """
        if not os.path.exists(dir_path):
            return -2
        if not os.path.isdir(dir_path):
            return -1
        size = 0 
        stack = [dir_path]
        while stack:
            current_dir = stack.pop()
            # for each subdirectory get its size of the file size
            for item in os.listdir(current_dir):
                item_path = os.path.join(current_dir, item)
                if os.path.isfile(item_path):
                    size += os.path.getsize(item_path)
                elif os.path.isdir(item_path):
                    stack.append(item_path)
        return size
    
    def get_file_name_from_path(self, file_path:str) -> str:
        """
        Gets the file name based on it's path
            :param file_path: A string representing the file's path
            :return: The name of the directory
        """
        file_name = os.path.basename(file_path)
        return file_name
    
    def get_directory_name_from_path(self, dir_path:str) -> str:
        """
        Gets the directory name based on it's path
            :param dir_path: A string representing the directory's path
            :return: The name of the file
        """
        dir_name = os.path.basename(dir_path)
        return dir_name
    
    def get_content_of_directory(self, directory_path) -> tuple:
        """
        Get the files and subdirectories of the directory
            :param directory_path: A string representing the directory's path
            :return: A 2 elements tuple (files, subdirectories)  
        """
        files, dirs = [], []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                files.append(item_path)
            elif os.path.isdir(item_path):
                dirs.append(item_path)
        return files, dirs
