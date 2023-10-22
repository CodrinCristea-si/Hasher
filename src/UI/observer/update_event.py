'''
Created on Sep 9, 2023

@author: cristeacodrin
'''

from enum import Enum


class UpdateEventType(Enum):
    UPDATE_STATUS = 0
    UPDATE_PROGRESS = 1
    UPDATE_MESSAGE = 2
    UPDATE_STAGE = 3
    
class UpdateEvent:
    def __init__(self, event_type: UpdateEventType, event_details:any) -> None:
        self.__event_type = event_type
        self.__event_details = event_details
    
    @property
    def event_type(self) -> UpdateEventType:
        return self.__event_type
    
    @property
    def event_details(self) -> any:
        return self.__event_details
