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
        
        operator = OfflineOperator()
        repo = SingletonDuplicateRepository()
        repo.begin_session()
        
        worker = OfflineWorker(operator, repo, fs_repo)
        worker.prepare([target])
        worker.execute(WorkerJobType.ANALYSE_TARGET)
        worker.finish()
        files, dirs, target_id = worker.get_work_results()
        
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
        fs_repo = SingletonFsRepository()
        
        repo = SingletonDuplicateRepository()
        repo.begin_session()
        
        # file hashing content
        for i in range(self.__nr_file_workers):
            end_index = start_index + amount  if i != self.__nr_file_workers - 1 else len(files)
            task_list = files[start_index:end_index]
            worker = OfflineWorker(operator, repo, fs_repo)
            worker.prepare(task_list)
            self.__file_workers.append(worker)
            worker.execute(WorkerJobType.DUPLICATE_FILE_CONTENT)
            self.__logger.info("Start worker executing on %d files" %(len(task_list)))
        
        # directory hashing content
        worker = OfflineWorker(operator, repo, fs_repo)
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
    
    def load_duplicates_for_target(self, target:str) -> list:
        self.__logger.info("Load duplicates for %s" %(target))
        fs_repo = SingletonFsRepository()
        fs_item_target = fs_repo.load_item_by_path(target)
        duplicates_items = fs_repo.load_items_by_parent_id(fs_item_target.item_id)
        self.__logger.info("Duplicates found %d" %(len(duplicates_items)))
        dups_ui_items = []
        for di in duplicates_items: 
            if di.is_duplicate:   
                ui_item = self.__convert_fs_item_to_ui_item(di)
                dups_ui_items.append(ui_item)
        self.__logger.info("Conversion done")
        return dups_ui_items
    
    def load_duplicates_for_target_by_id(self, target_id:int) -> list:
        self.__logger.info("Load duplicates for %d" %(target_id))
        fs_repo = SingletonFsRepository()
        duplicates_items = fs_repo.load_items_by_parent_id(target_id)
        self.__logger.info("Duplicates found %d" %(len(duplicates_items)))
        dups_ui_items = []
        for di in duplicates_items: 
            if di.is_duplicate:
                ui_item = self.__convert_fs_item_to_ui_item(di)
                dups_ui_items.append(ui_item)
        self.__logger.info("Conversion done")
        return dups_ui_items
        
    def get_all_duplicates(self):
        fs_repo = SingletonFsRepository()
        return fs_repo.get_all_duplicates()
    
    def get_graph_representation(self):
        fs_repo = SingletonFsRepository()
        return fs_repo.get_graph_representation()
        