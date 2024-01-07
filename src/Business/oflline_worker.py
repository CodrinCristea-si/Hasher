'''
Created on Aug 15, 2023

@author: cristeacodrin
'''
from threading import Thread
import sys
import traceback
from multiprocessing import Process, Lock
from enum import Enum
from Utils.algorithm import Algorithm
from functools import partial
from Business.operator import Operator
from Repository.SingletonRepository import SingletonDuplicateRepository
from Repository.SingletonRepository import SingletonFsRepository
from Repository.fsitem import *
from concurrent.futures import ThreadPoolExecutor
from Utils.logger import HasherLogger


class WorkerStatus(Enum):
    INITIALISE = 0
    START =  1
    RUNNING = 2
    FINISH = 3
    SUCCESS = 4
    FAILURE = 5
    STOP = 6


class WorkerJobType(Enum):
    DUPLICATE_FILE_CONTENT = 0 # check file duplicates by content
    DUPLICATE_DIRECTORY_CONTENT = 1 # check directory duplicates by content
    DUPLICATE_FILE_NAME = 2 # check file duplicates by name
    DUPLICATE_DIRECTORY_NAME = 3 # check directory duplicates by name
    ANALYSE_TARGET = 4


class OfflineWorker:
    def __init__(self, operator: Operator, dup_repo: SingletonDuplicateRepository, fs_repo:SingletonFsRepository) -> None:
        """
        OfflineWorker is an object that analyze a specific portion of the the target system. 
        It's primary tasks are creating and counter registries for each file or directory
            :param operator: - An Operator object related to the target system (local or remote system)
            :param repo: - A DuplicateRepository object for file or directory registrations on the local system
        """
        self.__task_list = [] # the list of files or directories that need to be analyzed
        self.__operator = operator # Operator object related to the target system
        self.__dup_repo = dup_repo # DuplicateRepository object for file or directory registrations on the local system
        self.__fs_repo =  fs_repo # FS_Repository object for file system architecture on the local system
        self.__status = WorkerStatus.INITIALISE # current status of the worker
        self.__th_worker = None # the thread that actually executes the task, this is useful for checking the status of the job
        self.__progres = 0 # how many entities from __task_list have been processed so far
        self.__results = [] # how many duplicate entities have been found
        self.__mutex_progress = Lock() # thread safe lock for __progress
        self.__mutex_status = Lock() # thread safe lock for __status
        self.__logger = HasherLogger.get_logger()
        
    def prepare(self, task_list: list) -> None:
        """
        Prepares the worker for the future tasks
            :param task_list: A list of entities(strings) that needs to be processed
        """
        self.__task_list = task_list
        self.__status = WorkerStatus.START
        self.__progres = 0
        self.__logger.info("worker prepared")
    
    def get_progress(self) -> int:
        """
        Gets the current progress of the worker
            :return: An integer representing how many entities have been processed 
        """
        self.__mutex_progress.acquire()
        prog = self.__progres
        self.__mutex_progress.release()    
        return prog
    
    def get_status(self) -> WorkerStatus:
        """
        Gets the current status of the worker
            :return: A WorkerStatus representing the current status of the worker
        """
        self.__mutex_status.acquire()
        status = self.__status
        self.__mutex_status.release()    
        return status  
    
    def set_status(self, status:WorkerStatus) -> None:
        """
        Sets the current status of the worker
            :param status: The new status of the worker
            :raise Exception: If the new status is invalid 
        """
        if not isinstance(status, WorkerStatus):
            raise Exception("Invalid worker status")
        self.__mutex_status.acquire()
        self.__status = status
        self.__mutex_status.release()    
    
    def get_work_results(self) -> list:
        """
        Gets the current results list of entities
            :return: the current results list
        """
        return self.__results
    
    def __analyse_target(self) -> None:
        """
        Gets the files and subdirectories from all levels of the specified target
            :raise Exception:
                -> If the target is already in the analyzing stage.
        """
        #nr_files = 0
        files = []
        #nr_dirs = 0
        dirs = []
        target =  self.__task_list[0]
        #print(target)
        previous_parent_id = 0
        target_id = None
        stack = [(target, previous_parent_id)]
        try:
            while stack:
                current_dir, previous_parent_id = stack.pop()
                dir_name = self.__operator.get_directory_name_from_path(current_dir)
                dir_size =  self.__operator.get_dir_size(current_dir)
                dir_modif_time = self.__operator.get_modification_time_for_path(current_dir)
                current_parent_id = self.__fs_repo.add_fs_item(dir_name, ItemType.DIRECTORY, previous_parent_id, dir_size, str(dir_modif_time), current_dir)
                self.__logger.debug("Add %s to FS_Repo with id %d" % (current_dir, current_parent_id))
                if target_id is None:
                    target_id = current_parent_id
                sub_files, sub_dirs = self.__operator.get_content_of_directory(current_dir)
                # process the files
                for item in sub_files:
                    item_name = self.__operator.get_file_name_from_path(item)
                    file_size = self.__operator.get_file_size(item)
                    file_modif_time = self.__operator.get_modification_time_for_path(item)
                    item_id = self.__fs_repo.add_fs_item(item_name, ItemType.FILE, current_parent_id, file_size, str(file_modif_time), item)
                    self.__logger.debug("Add %s to FS_Repo with id %d" % (item, item_id))
                    files.append(item)
                #process the sub directories
                for item in sub_dirs:
                    item_path = self.__operator.concat_paths(current_dir, item)
                    stack.append((item_path, current_parent_id))
                    dirs.append(item_path)
            #print(files, dirs, target_id)
            self.__results = files, dirs, target_id
            self.set_status(WorkerStatus.FINISH)
        except Exception as ex:
            self.__logger.error(ex)
            print(ex, traceback.format_exc())
            self.set_status(WorkerStatus.FAILURE)
        self.__logger.info("worker end execution")
        
    def __add_progress(self) -> None:
        """
        Increments the __progres
        """
        self.__mutex_progress.acquire()
        self.__progres += 1
        self.__mutex_progress.release()
    
    def __calculate_chunks_per_size(self, size:int) -> int:
        """
        Gets the number of chunks based on the size of the entity
            :param size: The size of the entity
            :return: The positive integer representing the number of chunks 
        """
        chunks = 0
        if size < 0:
            chunks = 0
        elif size < 10240: # less than 10k bytes
            chunks = 4 #one at the beginning, one at the end and 2 in the middle
        elif size < 104857600: # less than 100mb
            chunks = 4 +  size // 10485760 # one for each 10mb
        elif size < 1073741824: # less than 1Gb
            chunks = 14 + size // 104857600 # ne chunk for each 100mb
        elif  size < 10737418240: # less than 10Gb
            chunks = 24 + size // 1073741824 # for each Gb
        else: 
            chunks = 24 + size // 10737418240 # for each 10Gb
        return chunks
        
        
    def __hash_files_by_content(self) -> None:
        """
        Hashed each file from the list of tasks by content
        """
        duplicates = []
        self.__logger.info("worker start executing")
        try:
            for file in self.__task_list:
                self.__logger.debug("hashing %s" %(file))
                # get the file size
                file_size = self.__operator.get_file_size(file)
                # get the number of chunk based on the file size
                nr_chunks = self.__calculate_chunks_per_size(file_size)
                # get the chunks of files of a fixed size
                chunks = self.__operator.get_file_chunks(file, nr_chunks)
                # create the hash based on the chunks
                hash = Algorithm.create_hash_for_file(chunks)
                self.__logger.debug("hash for %s is %s" %(file,hash))
                # save the new data
                status_ent = self.__dup_repo.add_data(file, file_size, hash)
                if status_ent == 1:
                    duplicates.append(file)
                    self.__logger.debug("file %s is duplicate"%(file))
                #update progress
                self.__add_progress()
            #self.__results = duplicates
            self.set_status(WorkerStatus.FINISH)
            self.__logger.info("worker end execution")
        except Exception as ex:
            self.__logger.error(ex)
            print(ex, traceback.format_exc())
            self.set_status(WorkerStatus.FAILURE)
    
    def __hash_directories_by_content(self) -> None:
        """
        Hashed each directory from the list of tasks by content
        """
        duplicates = []
        try:
            for dir in self.__task_list:
                # get the file size
                dir_size = self.__operator.get_file_size(dir)
                # get the number of chunk based on the file size
                files, dirs = self.__operator.get_content_of_directory(dir)
                content_hashes = []
                for ent in files + dirs:
                    hash_ent = self.__dup_repo.get_hash_for_entity(ent)
                    content_hashes.append(hash_ent)
                # get the chunks of files of a fixed size
                # create the hash based on the chunks
                hash = Algorithm.create_hash_for_file(content_hashes)
                # save the new data
                status_ent = self.__dup_repo.add_data(dir, dir_size, hash)
                if status_ent == 1:
                    duplicates.append(dir)
                #update progress
                self.__add_progress()
            self.__results = duplicates
            self.set_status(WorkerStatus.FINISH)
        except Exception as ex:
            self.__logger.error(ex)
            print(ex, traceback.format_exc())
            # print(sys.gettrace())
            self.set_status(WorkerStatus.FAILURE)
    
    def execute(self, job_type:WorkerJobType) -> None:
        """
        After the worker has been prepared with the list of tasks and depending of the job_type, the job execution begins 
            :param job_type: A WorkerJobType object that represents the type of job that needs to be executed on the tasks list
        """
        self.set_status(WorkerStatus.RUNNING)
        if job_type == WorkerJobType.DUPLICATE_FILE_CONTENT:
            target_method = partial(self.__hash_files_by_content)
        elif job_type == WorkerJobType.DUPLICATE_DIRECTORY_CONTENT:
            target_method = partial(self.__hash_directories_by_content)
        elif job_type == WorkerJobType.ANALYSE_TARGET:
            target_method = partial(self.__analyse_target)
        self.__th_worker = ThreadPoolExecutor()
        future = self.__th_worker.submit(target_method)
    
    def finish(self) -> None:
        """
        Waits for the current job to finish and updated the worker's status
        """
        self.__th_worker.shutdown(True)
        self.set_status(WorkerStatus.SUCCESS)
    
    def terminate_job(self) -> None:
        """
        Terminates for the current job and updated the worker's status
        """
        self.__th_worker.shutdown(False)
        self.set_status(WorkerStatus.STOP)
        

