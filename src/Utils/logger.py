import inspect
from logging import *



class _CoreHasherLogger(Logger):
    def __init__(self, filename: str = "hasher_logs.log", logger_name:str = "Hasher") -> None:
        Logger.__init__(self,logger_name)
        self.__filename =  filename
    
    @classmethod
    def initialize(cls, filename: str = "hasher_logs.log", logger_name: str = "Hasher") -> "_CoreHasherLogger":
        logger = cls(logger_name=logger_name)
        logger.setLevel(INFO)
    
        file_log_handler = FileHandler(filename)
        file_log_handler.setLevel(INFO)
    
        log_formatter = Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s  - %(message)s')
        file_log_handler.setFormatter(log_formatter)
    
        logger.addHandler(file_log_handler)
        return logger      

class HasherLogger(_CoreHasherLogger):
    
    @classmethod
    def get_logger(cls, filename: str = "hasher_logs.log", logger_name = "Hasher"):
        if not hasattr(cls, 'instance') :
            #cls.instance = super(_CoreHasherLogger, cls).__new__(cls)
            cls.instance = cls.initialize(filename, logger_name)
        return cls.instance



    