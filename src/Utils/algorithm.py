'''
Created on Aug 15, 2023

@author: cristeacodrin
'''
import hashlib


class Algorithm:
    def __init__(self):
        pass
    
    @staticmethod
    def create_hash_for_file(components:list) -> str:
        """
        Creates a hash from a list of components
            :param components: A list of objects that needs to be digested to create a hash
            :return: A SHA-256 string object
        """
        hash_object = hashlib.sha256()

        for comp in components:
            digestible = ""
            if isinstance(comp, str):  # Convert strings to bytes
                digestible = comp.encode("utf-8")
            else:
                digestible = repr(comp).encode("utf-8")
            # Update the hash object with multiple inputs
            hash_object.update(digestible)
        
        # Get the hexadecimal representation of the hash
        hash_hex = hash_object.hexdigest()
        return hash_hex


