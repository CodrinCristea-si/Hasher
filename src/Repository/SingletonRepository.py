'''
Created on Aug 16, 2023

@author: cristeacodrin
'''
from Repository.repository import Repository

class SingletonRepository(Repository):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Repository, cls).__new__(cls)
        return cls.instance
