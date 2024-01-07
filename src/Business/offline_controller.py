'''
Created on Aug 15, 2023

@author: cristeacodrin
'''
import os
from enum import Enum
from threading import Thread
from Business.oflline_worker import OfflineWorker, WorkerJobType
from Business.offline_operator import OfflineOperator
from Repository.SingletonRepository import SingletonDuplicateRepository
from Repository.SingletonRepository import SingletonFsRepository
from Repository.fsrepository import FsItem, ItemType
from UI.ui_item import *
from Utils.logger import *


class ProccessingStages(Enum):
    ANALYSE = 0
    PROCESS = 1
    FINISH = 2

class OfflineController:
    def __init__(self):
        self.__nr_file_workers = 3 # the number of workers that process files 
        self.__file_workers = [] # the list of workers that process files
        self.__nr_dir_workers = 2  # the number of workers that process directories 
        self.__dir_workers = [] # the list of workers that process directories
        self.__logger = HasherLogger.get_logger()

    def analyse_target(self, target:str) -> tuple:
        """
        Gets tne files and subdirectories from all levels of the specified target
            :param target: A string object specifying the path to the target object
            :return: A 3 element tuple object in which the first element represents the path files on all levels, 
            the second element represents all the subdirectories on all the levels, and the third element represents the id for the item target
            :raise Exception:
                -> If the target does not exist
                -> If the target is not a directory
                -> If the target is already in the analyzing stage.
        """
        #nr_files = 0
        files = []
        #nr_dirs = 0
        dirs = []
        if not os.path.exists(target):
            self.__logger.error("%s does not exist!" % (target))
            raise Exception("%s does not exist!" % (target))
        if not os.path.isdir(target):
            self.__logger.error("%s is not a directory" % (target))
            raise Exception("%s is not a directory" % (target))
        fs_repo = SingletonFsRepository()
        if not fs_repo.begin_session() == 0:
            self.__logger.critical("Cannot analyze the an already in analyzing process of the target %s" %(target))
            raise Exception("Cannot analyze the an already in analyzing process of the target %s" %(target))
        previous_parent_id = 0
        target_id = None
        stack = [(target, previous_parent_id)]
        while stack:
            current_dir, previous_parent_id = stack.pop()
            current_parent_id = fs_repo.add_fs_item(os.path.basename(current_dir), ItemType.DIRECTORY, previous_parent_id, os.path.getsize(current_dir), str(os.path.getmtime(current_dir)), current_dir)
            self.__logger.debug("Add %s to FS_Repo with id %d" % (current_dir, current_parent_id))
            if target_id is None:
                target_id = current_parent_id
            for item in os.listdir(current_dir):
                item_path = os.path.join(current_dir, item)
                if os.path.isfile(item_path):
                    item_id = fs_repo.add_fs_item(item, ItemType.FILE, current_parent_id, os.path.getsize(target), str(os.path.getmtime(target)), item_path)
                    self.__logger.debug("Add %s to FS_Repo with id %d" % (item, item_id))
                    files.append(item_path)
                elif os.path.isdir(item_path):
                    stack.append((item_path, current_parent_id))
                    dirs.append(item_path)
            #previous_parent_id = current_parent_id
        fs_repo.end_session()
        self.__logger.info("Fs_Repo session ended")
        return files, dirs, target_id
    
    def __mark_duplicates_in_fs_repo(self):
        fs_repo = SingletonFsRepository()
        dup_repo = SingletonDuplicateRepository()
        all_duplicates_path =  dup_repo.get_all_duplicates_full_path()
        fs_repo.mark_all_duplicates(all_duplicates_path)
    
    def check_duplicates_by_content(self, target:str):
        """
        Check the duplicates by analysing the content of the target object
            :param target: A string object specifying the path to the target object
            :return: A list of path like objects for all the files and subdirectories that are marked as duplicates 
        """
        self.__logger.info("Checking duplicates by content for %s" %(target))
        files, dirs, target_id = self.analyse_target(target)
        self.__logger.info("Analyze step done")
        dups = []
        start_index = 0
        amount = len(files) // self.__nr_file_workers
        operator = OfflineOperator()
        repo = SingletonDuplicateRepository()
        repo.begin_session()
        
        # file hashing content
        for i in range(self.__nr_file_workers):
            end_index = start_index + amount  if i != self.__nr_file_workers - 1 else len(files)
            task_list = files[start_index:end_index]
            worker = OfflineWorker(operator, repo)
            worker.prepare(task_list)
            self.__file_workers.append(worker)
            worker.execute(WorkerJobType.DUPLICATE_FILE_CONTENT)
            self.__logger.info("Start worker executing on %d files" %(len(task_list)))
        
        # directory hashing content
        worker = OfflineWorker(operator, repo)
        worker.prepare(dirs)
        self.__file_workers.append(worker)
        worker.execute(WorkerJobType.DUPLICATE_DIRECTORY_CONTENT)
        self.__logger.info("Start worker executing on %d dirs" %(len(dirs)))
        # waiting for jobs to be done
        for worker in self.__file_workers:
            worker.finish()
            # dups += worker.get_work_results()
        self.__logger.info("Workers ended their execution")
        self.__mark_duplicates_in_fs_repo()
        self.__logger.info("Duplicates marked")

        
    def __convert_item_type_to_ui_type(self, item_type:ItemType):
        return UIItemType[item_type.name]
    
    def __convert_fs_item_to_ui_item(self, fs_item: FsItem) -> UIItem:
        if fs_item is None:
            return None
        return UIItem(fs_item.item_id, fs_item.item_name, self.__convert_item_type_to_ui_type(fs_item.item_type), fs_item.parent_id, fs_item.is_duplicate)
        
    def get_all_duplicates(self):
        fs_repo = SingletonFsRepository()
        return fs_repo.get_all_duplicates()
    
    def get_graph_representation(self):
        fs_repo = SingletonFsRepository()
        return fs_repo.get_graph_representation()
        