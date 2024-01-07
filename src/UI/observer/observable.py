'''
Created on Sep 8, 2023

@author: cristeacodrin
'''

from abc import ABC
from UI.observer.observer import Observer
from UI.observer.update_event import UpdateEvent


class Observable(ABC):
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer: Observer):
        self._observers.append(observer)
    
    def notify_observers(self, update_event: UpdateEvent):
        for obs in self._observers:
            obs.update_signal.emit(update_event)
    
