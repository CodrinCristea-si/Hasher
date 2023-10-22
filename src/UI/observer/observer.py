'''
Created on Sep 8, 2023

@author: cristeacodrin
'''

from UI.observer.update_event import UpdateEvent
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal

class Observer():
    update_signal = pyqtSignal(UpdateEvent)
    
    def __init__(self):
        self.update_signal.connect(self.updateObserver)

    def updateObserver(self, update_event: UpdateEvent):
        raise NotImplementedError("This method should be overridden")
