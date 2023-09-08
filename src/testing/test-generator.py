'''
Created on Aug 17, 2023

@author: cristeacodrin
'''
import random
import shutil
import os
from random import randint, choice
from Business.offline_controller import OfflineController
from Repository.SingletonRepository import SingletonRepository



number_of_files_names = 6 # the number of file names
number_of_dirs_names = 10 # the number of directory names
max_num_of_files_per_dir = 5 # the maximum number of files for each directory
max_num_of_subdirs_per_dir = 4 # the maximum number of subdirectories for each directory
special_change_percentage = 20 # the chance in which a subdirectory is a special duplicate directory
number_of_subdir_for_root = 3 # the maximum number of subdirectories for the root directory
number_of_dir_dups = 1 # the number of special subdirectory duplicates
max_depth = 10 # maximum recursion depth for a directory
max_size_file = 10000 # bytes # maximum file size
min_size_file = 100 # bytes # minimum file size
min_file_name_length = 5 # minimum file name length
max_file_name_length = 10 # maximum file name length
min_dir_name_length = 5 # minimum directory name length
max_dir_name_length = 10 # maximum directory name length
dir_field_name= "simulation_ffline_hasher" # the name of the root directory
dir_originals_name= "originals" # the name of a root subdirectory in which the ORIGINAL files and special directories will be stored
dir_duplicates_name= "duplicates" # the name of a root subdirectory in which the DUPLICATE files and special directories will be stored
alphanum = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" # the alphanumerical values
file_extension = ".prob" # extension for the file names
dir_control_options = 0o777 # privacy access mode for directory

file_duplicates = {}

def add_to_file_duplicates(file_name, path):
    if file_duplicates.get(file_name) is None:
        file_duplicates[file_name] = []
    file_duplicates[file_name].append(path)
 
def save_file(path, file_name, file_content, register_duplicate: bool = False):
    file_path = os.path.join(path, file_name)
    #print("file",file_path, file_name)
    if not os.path.exists(file_path):
        f =  open(file_path, "x")
    with open(file_path, "w") as file:
        file.write(file_content)
    if register_duplicate:
        add_to_file_duplicates(file_name, file_path)

class Directory:
    def __init__(self, name, path):
        if path is None:
            self.__path = ""
        self.__path = path
        self.__name = name
        self.__subdirs = []
        self.__files = {}
    
    def add_dir(self, dir):
        self.__subdirs.append(dir)
    def add_file(self, file_name, file_content):
        self.__files[file_name] = file_content 
    def get_dirs(self):
        return self.__subdirs
    def get_files(self):
        return self.__files  
    def get_name(self):
        return self.__name
    def get_path(self):
        return self.__path
    def set_name(self, value):
        self.__name =  value
    def set_path(self, value):
        self.__path = value
    def create_fs_object(self, start_path:str):
        self.__path = os.path.join(start_path, self.__name)
        #print("facem ceva", self.__str__()) 
        if not os.path.exists(self.__path):
            os.mkdir(self.__path, dir_control_options)
        for subdir in self.__subdirs:
            subdir.create_fs_object(self.__path)
            #subdir_path =  os.path.join(self.__path, subdir.gz
        #print(self.__files)
        for file_name in self.__files:
            save_file(self.__path, file_name, self.__files[file_name], True)
            # file_path = os.path.join(self.__path, file_name)
            # with open(file_path, "w") as file:
            #     file.write("")
    def __str__(self):
        return self.__path + " [" + self.__name + "]" + ":( " + str([str(di) for di in self.__subdirs]) + "|" + str([str(file_name) for file_name in list(self.__files.keys())]) + ")"
    
    def __repr__(self):
        return self.__str__()
    
def generate_file_name():
    """
    Generates a file name
    """
    name_length = randint(min_file_name_length, max_file_name_length)
    file_name = ""
    for _ in range(name_length):
        opt = choice(alphanum)
        file_name += opt
    file_name += file_extension
    return file_name

def generate_dir_name():
    """
    Generates a file name
    """
    name_length = randint(min_dir_name_length, max_dir_name_length)
    dir_name = ""
    for _ in range(min_file_name_length, max_file_name_length):
        opt = choice(alphanum)
        dir_name += opt
    return dir_name

def generate_file_content():
    """
    Generate a file content
    """
    content_length = randint(min_size_file, max_size_file)
    content = ""
    for _ in range(min_size_file, max_size_file):
        opt = choice(alphanum)
        content += opt
    return content

def create_file_registry():
    """
    Generate a registration(a dictionary) of filenames with it's corresponding content
    """
    files = {}
    for _ in range(number_of_files_names):
        file_name = generate_file_name()
        file_content = generate_file_content()
        files[file_name] = file_content
    return files

def create_dir_registry():
    """
    Generates a registration of directory names
    """
    dirs = []
    for _ in range(number_of_dirs_names):
        dir_name = generate_dir_name()
        dirs.append(dir_name)
    return dirs

def create_directories_duplicates(files, dirs):
    """
    Generates a list of special duplicatable directories
    """
    special_dirs = []
    for _ in range(number_of_dir_dups):
        depth = randint(1, max_depth // 2 + 1)
        dir_name = choice(dirs)
        root_dir = Directory(dir_name, dir_name)
        directories = [root_dir] 
        for i in range(depth):
            subdirs = []
            for dirul in directories:
                if i != depth - 1:
                    how_many_dirs = randint(1, max_num_of_subdirs_per_dir)
                    for _ in range(how_many_dirs):
                        subdir_name = choice(dirs)
                        subdir = Directory(subdir_name, "")
                        dirul.add_dir(subdir)
                    subdirs += dirul.get_dirs()
                how_many_files = randint(1, max_num_of_files_per_dir)
                for _ in range(how_many_files):
                    file_name = choice(list(files.keys()))
                    dirul.add_file(file_name, files[file_name]) 
            directories = subdirs
        #print("dup dir", root_dir)
        special_dirs.append(root_dir)
    return special_dirs

def create_root_subdirectory(files:dict, dir_names:list, special_dirs:list, path:str):
    """
    Generates a subroot environment (subdirectories and files)
    """
    depth = randint(1, max_depth // 2 + 1)
    root_dir = Directory(os.path.basename(path), path)
    #print(dir_names)
    directories = [root_dir] 
    for i in range(depth):
        subdirs = []
        for dir in directories:
            #print(dir, i)
            subdir_path = ""
            if dir.get_path() != root_dir.get_path():
                subdir_path = os.path.join(path, dir.get_name())
                if not os.path.exists(subdir_path):
                    os.mkdir(subdir_path, dir_control_options)
            else:
                subdir_path = root_dir.get_path()
            if not os.path.exists(subdir_path):
                os.mkdir(subdir_path, dir_control_options)
            #print(subdir_path)
            if i != depth - 1:
                how_many_dirs = randint(1, max_num_of_subdirs_per_dir)
                for _ in range(how_many_dirs):
                    chance_for_special = randint(1,101)
                    if chance_for_special < special_change_percentage:
                        special_dir = choice(special_dirs)
                        special_dir.create_fs_object(subdir_path)
                    else:
                        subdir_name = choice(dir_names)
                        while subdir_name == dir.get_name() or subdir_name in [subdirs.get_name() for subdirs in dir.get_dirs()]:
                            subdir_name = choice(dir_names)
                        #print("new subdir", subdir_name)
                        subsubdir_path = os.path.join(subdir_path, subdir_name)
                        subdir = Directory(subdir_name, subsubdir_path)
                        #print(subdir)
                        dir.add_dir(subdir)
                subdirs += dir.get_dirs()
            how_many_files = randint(1, max_num_of_files_per_dir)
            for _ in range(how_many_files):
                file_name = choice(list(files.keys()))
                #file_path = os.path.join(subdir_path,file_name)
                save_file(subdir_path, file_name, files.get(file_name), True)
                dir.add_file(file_name, files[file_name]) 
        directories = subdirs

def create_environment(files:dict, dirs: list):
    """
    Creates the file system architecture, separates the original ones from the duplicated ones
    """
    current_path = os.path.join(os.getcwd(), dir_field_name)
    #os.mkdir(current_path, dir_control_options)
    #save the original files
    originals_path = os.path.join(current_path, dir_originals_name)
    os.mkdir(originals_path, dir_control_options)
    #print([file for file in files])
    for file_name in files:
        save_file(originals_path, file_name, files[file_name])
    #make duplicates
    dups_path = os.path.join(current_path, dir_duplicates_name)
    os.mkdir(dups_path, dir_control_options)
    special_dirs = create_directories_duplicates(files, dirs)
    for _ in range(number_of_subdir_for_root):
        dir_name = choice(dirs)
        subdir_path = os.path.join(dups_path, dir_name)
        create_root_subdirectory(files,dirs,special_dirs,subdir_path)
    

def generate_test_field():
    """
    Creates a test field scenario: files and dirs to be duplicated and the environment 
    """
    if not os.path.exists(dir_field_name):
        os.mkdir(dir_field_name, dir_control_options)
    else:
        shutil.rmtree(dir_field_name)
        os.mkdir(dir_field_name, dir_control_options)
    files = create_file_registry()
    dirs = create_dir_registry()
    create_environment(files, dirs)    
    

def cmp_lists(list1, list2)-> any:
    """
    Compares the elements of 2 list and returns the first different element
    """
    dif_el = None
    for el in list1:
        if not el in list2:
            dif_el = el
            break
    return dif_el
    
if __name__ == '__main__':
    generate_test_field()
    print("done")
    total_dups_created = 0
    a_file_key = None
    for dup in file_duplicates:
        print(f"%s (%d)"%(dup, len(file_duplicates[dup])))
        total_dups_created += len(file_duplicates[dup])
        # for el in  file_duplicates[dup]:
        #     print(el)
        if a_file_key is None:
            a_file_key = dup
    print("total duplicates created %d"%(total_dups_created))
    cont = OfflineController()
    print("Detected duplicates")
    dups_detected = cont.check_duplicates_by_content(os.path.join(os.getcwd(),dir_field_name))
    print("total duplicates detected %d"%(len(set(dups_detected))))
    # for el in dups_detected:
    #     print(el)
    dups_detected_dict = {}
    for dup_path in dups_detected:
        dup_name = os.path.basename(dup_path)
        if dups_detected_dict.get(dup_name) is None:
            dups_detected_dict[dup_name] = []
        dups_detected_dict[dup_name].append(dup_path)
    if len(dups_detected_dict.keys()) != len(file_duplicates.keys()):
        print("dif len dict size %d <-> %d" %(len(dups_detected_dict.keys()), len(file_duplicates.keys())))
    print(dups_detected_dict.keys())
    for dup in dups_detected_dict:
        if file_duplicates.get(dup) is None:
            print("False positive detected %s with size %d" %(dup, len(set(dups_detected_dict.get(dup)))))
        elif not len(set(dups_detected_dict[dup])) == len(set(file_duplicates[dup])):
            print (f"dif len %d(detected) != %d(created)" %(len(set(dups_detected_dict[dup])), len(set(file_duplicates[dup]))))
        else:
            dif_el = cmp_lists(dups_detected_dict[dup], file_duplicates[dup])
            if dif_el is not None:
                print(f"dif el between %s(detected) <-> %s(created) with %s" %(dup, dup, dif_el))
            else:
                print(f"same for %s <-> %s" %(dup, dup))
    if dups_detected_dict.get(a_file_key) is None:
        print("cannot analysis for %s on detected" %(a_file_key))
    elif file_duplicates.get(a_file_key) is None:
        print("cannot analysis for %s on created" %(a_file_key))
    else:
        print("key %s with len %d(detected) <-> %d(created)" %(a_file_key,len(set(dups_detected_dict.get(a_file_key))), len(set(file_duplicates.get(a_file_key)))))
        print("Not Detected")
        # max_len = len(dups_detected_dict.get(a_file_key)) if len(dups_detected_dict.get(a_file_key)) > len(file_duplicates.get(a_file_key)) else len(file_duplicates.get(a_file_key))
        true_detected = 0
        not_detected = []
        false_detected = []
        for el in dups_detected_dict.get(a_file_key):
            if el not in file_duplicates.get(a_file_key):
                not_detected.append(el)
            else:
                true_detected += 1
        for el in file_duplicates.get(a_file_key):
            if el not in dups_detected_dict.get(a_file_key):
                false_detected.append(el)
        print("similarity %d/%d" %(true_detected,len(dups_detected_dict.get(a_file_key))))
        print("False Detected")
        for el in not_detected:
            print(el)   
        print("Not Detected")
        for el in false_detected:
            print(el)   
        # for i in range(max_len):
            # if i < len(dups_detected_dict.get(a_file_key)):
            #     print (dups_detected_dict.get(a_file_key)[i], end=" ")
            # else:
            #     print("", end=" ")
            # if i < len(file_duplicates.get(a_file_key)):
            #     print (file_duplicates.get(a_file_key)[i], end="\n")
            # else:
            #     print("", end="\n")
    # repo = SingletonRepository()
    # repo.begin_session()
    # repo.add_data("simulation_ffline_hasher/duplicates/OaUsX/ou6Jw6MLz.prob",9990, "9463f69b217d0e1e535a851bb0944b9a1892d04de2f16ffd02119708a636f8fe")
    # repo.add_data("simulation_ffline_hasher/duplicates/OaUsX/ou6Jw6MLz1.prob",9991, "9463f69b217d0e1e535a851bb0944b9a1892d04de2f16ffd02119708a636f8ff")
    