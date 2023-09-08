'''
Created on Aug 15, 2023

@author: cristeacodrin
'''
import os
from threading import Thread
from Business.oflline_worker import OfflineWorker, WorkerJobType
from Business.offline_operator import OfflineOperator
from Repository.SingletonRepository import SingletonRepository


class OfflineController:
    def __init__(self):
        self.__nr_file_workers = 3 # the number of workers that process files 
        self.__file_workers = [] # the list of workers that process files
        self.__nr_dir_workers = 2  # the number of workers that process directories 
        self.__dir_workers = [] # the list of workers that process directories
        
    def analyse_target(self, target:str) -> tuple:
        """
        Gets tne files and subdirectories from all levels of the specified target
            :param target: A string object specifying the path to the target object
            :return: A 2 element tuple object in which the first element represents the path files on all levels
            and the second element represents all the subdirectories on all the levels 
        """
        #nr_files = 0
        files = []
        #nr_dirs = 0
        dirs = []
        if not os.path.exists(target):
            raise Exception("%s does not exist!" % (target))
        stack = [target]

        while stack:
            current_dir = stack.pop()
            for item in os.listdir(current_dir):
                item_path = os.path.join(current_dir, item)
                if os.path.isfile(item_path):
                    #nr_files += 1
                    files.append(item_path)
                    # print("File:", item_path)
                elif os.path.isdir(item_path):
                    # print("Directory:", item_path)
                    stack.append(item_path)
                    #nr_dirs += 1
                    dirs.append(item_path)
        return files, dirs
    
    
    
    def check_duplicates_by_content(self, target:str)->list:
        """
        Check the duplicates by analysing the content of the target object
            :param target: A string object specifying the path to the target object
            :return: A list of path like objects for all the files and subdirectories that are marked as duplicates 
        """
        files, dirs = self.analyse_target(target)
        dups = []
        start_index = 0
        amount = len(files) // self.__nr_file_workers
        operator = OfflineOperator()
        repo = SingletonRepository()
        repo.begin_session()
        # file hashing content
        for i in range(self.__nr_file_workers):
            end_index = start_index + amount  if i != self.__nr_file_workers - 1 else len(files)
            task_list = files[start_index:end_index]
            worker = OfflineWorker(operator, repo)
            worker.prepare(task_list)
            self.__file_workers.append(worker)
            worker.execute(WorkerJobType.DUPLICATE_FILE_CONTENT)
        # directory hashing content
        worker = OfflineWorker(operator, repo)
        worker.prepare(dirs)
        self.__file_workers.append(worker)
        worker.execute(WorkerJobType.DUPLICATE_DIRECTORY_CONTENT)
        self.__file_workers.append(worker)
        # waiting for jobs to be done
        for worker in self.__file_workers:
            worker.finish()
            dups += worker.get_work_results()
        print("ia duplicate de unde ai")
        return dups
    
        
        
        
        