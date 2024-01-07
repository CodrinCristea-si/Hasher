'''
Created on Aug 16, 2023

@author: cristeacodrin
'''
from Repository.duplicate_repository import DuplicateRepository
from Repository.fsrepository import FSRepository

class SingletonDuplicateRepository(DuplicateRepository):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DuplicateRepository, cls).__new__(cls)
        return cls.instance

class SingletonFsRepository(FSRepository):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FSRepository, cls).__new__(cls)
        return cls.instance
