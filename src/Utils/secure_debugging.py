'''
Created on Jan 7, 2024

@author: cristeacodrin
'''
import inspect
import sys


class _Debug_Wrapper_Core:
    Debugger_Name = "_DEBUG_MODE"
    
    def __init__(self):
        self.__DEBUG_MODE = None
    
    def enable_debug(self):
        self.__DEBUG_MODE = True
    
    def disable_debug(self):
        self.__DEBUG_MODE = None
    
    def is_debug_enabled(self):
        return self.__DEBUG_MODE == True
    
    def __repr__(self):
        return f"Debug Mode {self.__DEBUG_MODE}"
    
    def __str__(self):
        return self.__repr__()

class _Debug_Wrapper(_Debug_Wrapper_Core): # Singleton style
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_Debug_Wrapper_Core, cls).__new__(cls)
        return cls.instance

def _check_if_the_current_module_is_the_caller():
    """
    Checks if the calling module is the same as the one that this function is defined
    This prevents certain functions to be used outside of this module
    """
    caller_module = inspect.getmodule(inspect.currentframe().f_back)
    current_module = sys.modules[__name__]
    
    return caller_module == current_module

def enable_safe_use_of_debug_function(func):
    """
    Enables the debug mode session
    Cannot be used outside of this module
    """
    def wrapper(*args, **kwargs):
        # this decorator can be used in the same module as the one that is being defined 
        if not _check_if_the_current_module_is_the_caller():
            return None
        
        # check if the session is not already started 
        if globals().get("_DEBUG_MODE") is not None:
            raise Exception("Debug Mode is already enabled")
        
        # start the debug session
        global _DEBUG_MODE
        _DEBUG_MODE = _Debug_Wrapper()
        _DEBUG_MODE.enable_debug()
        
        #return the execution
        return func(*args, **kwargs) if func is not None else None
    
    return wrapper

def disable_safe_use_of_debug_function(func):
    """
    Disables the debug mode session
    Cannot be used outside of this module
    """
    def wrapper(*args, **kwargs):
        # this decorator can be used in the same module as the one that is being defined 
        if not _check_if_the_current_module_is_the_caller():
            return None
        
        # check is the session is started
        if globals().get("_DEBUG_MODE") is None:
            raise Exception("Debug Mode is not enabled")
        
        # end the debug session
        _DEBUG_MODE.disable_debug()
        
        #return execution
        return func(*args, **kwargs) if func is not None else None
    return wrapper

def check_if_debug_mode_is_enabled(func):
    """
    Checks if the debug mode session is enabled
    Cannot be used outside of this module
        :return: True if the session is started/enabled, False otherwise
    """
    def wrapper(*args, **kwargs):
        # this decorator can be used in the same module as the one that is being defined 
        if not _check_if_the_current_module_is_the_caller():
            return None
        
        # check if the session exists and is started
        return globals().get("_DEBUG_MODE") is not None and _DEBUG_MODE.is_debug_enabled()
    return wrapper

def safe_debug_function(func):
    """
    Ensures that the func can be executed if the debug session is enabled/ started
    Can be used outside outside of this module
    """
    def wrapper(*args, **kwargs):
        # ensure that the debug session is started before executing
        if globals().get("_DEBUG_MODE") is None or not _DEBUG_MODE.is_debug_enabled():
            return None
        return func(*args, **kwargs)
    return wrapper

@enable_safe_use_of_debug_function
def _enable_debug_mode():
    """
    Enables the debug session
    Cannot be used outside of this module
    """
    pass

def enable_debug_mode():
    """
    Enables the debug session
    """
    _enable_debug_mode()

@disable_safe_use_of_debug_function
def _disable_debug_mode():
    """
    Disables the debug session
    Cannot be used outside of this module
    """
    pass

def disable_debug_mode():
    """
    Disables the debug session
    """
    _disable_debug_mode()
    
@check_if_debug_mode_is_enabled
def _is_debug_mode():
    """
    Checks if the debug session started/ enabled
    Cannot be used outside of this module
    """
    pass

def is_debug_mode():
    """
    Checks if the debug session started/ enabled
    """
    return _is_debug_mode()

if __name__ == "__main__":
    
    def some_test_function():
        print("some_test_function executed")
    
    @safe_debug_function    
    def some_debug_test_function():
        print("some_debug_test_function executed")
        
    print("No debug session started")
    some_test_function()
    some_debug_test_function()
    
    print("Debug session started")
    enable_debug_mode()
    
    some_test_function()
    some_debug_test_function()
    print("Debug Session", is_debug_mode())
    
    print("Debug session ended")
    disable_debug_mode()
    
    some_test_function()
    some_debug_test_function()
    
    print("Debug Session", is_debug_mode())
    
    
    
    
        