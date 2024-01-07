import unittest
import pickle
# from Repository.duplicate_repository import *
from Repository.fsrepository import FSRepository, FsItem, ItemType
from Repository.SingletonRepository import *
from Repository.fsitem import FsItemFormatter


class FsRepositoryTest(unittest.TestCase):

    def test_singleton_repo(self):
        repo1 = SingletonFsRepository()
        repo2 = SingletonFsRepository()
        self.assertEqual(id(repo1), id(repo2), "Check if singleton design pattern works")
    
    def test_session(self):
        repo1 = SingletonFsRepository()
        res = repo1.begin_session()
        self.assertEqual(res, 0, "Session started with success")
        
        res = repo1.begin_session()
        self.assertEqual(res, -1, "Cannot start the same session twice")
        
        self.assertFalse(repo1.is_session_ended(), "A started session is not ended")
        
        res = repo1.end_session()
        self.assertEqual(res, 0, "Session ended with success")
        
        res = repo1.end_session()
        self.assertEqual(res, -1, "Cannot end a not started session")
        
        self.assertTrue(repo1.is_session_ended(), "The session should be ended")
        
        res = repo1.begin_session()
        self.assertEqual(res, 0, "Session started with success")
    
    def test_add_item(self):
        repo = SingletonFsRepository()
        repo.begin_session()
        item_id = repo.add_fs_item("a", ItemType.FILE, 0, 50, "02-10-2022")
        self.assertGreater(item_id, 0, "Check if the item has been processed")
        
        item = None
        repo2 = FSRepository()
        with open(FSRepository.__dict__.get("_FSRepository__STORAGE_ITEM_FILE"), "rb") as file:
            #item_bitarray = file.readline()[:-1] # remove the \n
            item_bitarray = repo2.read_item_from_file(file)
            item = FsItemFormatter.read_bytes(item_bitarray)
            #item = pickle.loads(item_bitarray)
        #print(item)
        self.assertIsNotNone(item, "The item has been saved in the storage file")
        self.assertEqual(item_id, item.item_id, "Check if they have the same id")
        self.assertEqual("a", item.item_name, "Check if they have the same name")
        self.assertEqual(ItemType.FILE, item.item_type, "Check if they have the same type")
        self.assertEqual(0, item.parent_id, "Check if they have the same parent id")
        self.assertEqual(50, item.item_size, "Check if they have the same size")
        self.assertEqual("02-10-2022", item.last_modified, "Check if they have the same last modification date")
        
        repo.end_session()
    
    def test_add_multiple_items(self):
        repo = SingletonFsRepository()
        repo.begin_session()
        item_id1 = repo.add_fs_item("a", ItemType.DIRECTORY, 0, 50, "02-10-2022")
        item_id2 = repo.add_fs_item("b", ItemType.FILE, item_id1, 100, "03-10-2022")
        item_id3 = repo.add_fs_item("c", ItemType.DIRECTORY, item_id1, 70, "04-10-2022")
        item_id4 = repo.add_fs_item("d", ItemType.SYMLINK, item_id3, 90, "05-10-2022")
        item_id5 = repo.add_fs_item("e", ItemType.FILE, item_id3, 65, "06-10-2022")
        
        item = None
        repo2 = FSRepository()
        with open(FSRepository.__dict__.get("_FSRepository__STORAGE_ITEM_FILE"), "rb") as file:
            #item_bitarray = file.readline()[:-1] # remove the \n
            item_bitarray1 = repo2.read_item_from_file(file)
            item1 = FsItemFormatter.read_bytes(item_bitarray1)
            
            item_bitarray2 = repo2.read_item_from_file(file)
            item2 = FsItemFormatter.read_bytes(item_bitarray2)
            
            item_bitarray3 = repo2.read_item_from_file(file)
            item3 = FsItemFormatter.read_bytes(item_bitarray3)
            
            item_bitarray4 = repo2.read_item_from_file(file)
            item4 = FsItemFormatter.read_bytes(item_bitarray4)
            
            item_bitarray5 = repo2.read_item_from_file(file)
            item5 = FsItemFormatter.read_bytes(item_bitarray5)
            
            item_bitarray6 = repo2.read_item_from_file(file)
            #item = pickle.loads(item_bitarray)
        self.assertEqual(item_bitarray6, b'', "Null when eof is reached")
        
        #item1
        self.assertIsNotNone(item1, "The item has been saved in the storage file")
        self.assertEqual(item_id1, item1.item_id, "Check if they have the same id")
        self.assertEqual("a", item1.item_name, "Check if they have the same name")
        self.assertEqual(ItemType.DIRECTORY, item1.item_type, "Check if they have the same type")
        self.assertEqual(0, item1.parent_id, "Check if they have the same parent id")
        self.assertEqual(50, item1.item_size, "Check if they have the same size")
        self.assertEqual("02-10-2022", item1.last_modified, "Check if they have the same last modification date")
        
        #item4
        self.assertIsNotNone(item4, "The item has been saved in the storage file")
        self.assertEqual(item_id4, item4.item_id, "Check if they have the same id")
        self.assertEqual("d", item4.item_name, "Check if they have the same name")
        self.assertEqual(ItemType.SYMLINK, item4.item_type, "Check if they have the same type")
        self.assertEqual(item_id3, item4.parent_id, "Check if they have the same parent id")
        self.assertEqual(90, item4.item_size, "Check if they have the same size")
        self.assertEqual("05-10-2022", item4.last_modified, "Check if they have the same last modification date")
    
        #item5
        self.assertIsNotNone(item5, "The item has been saved in the storage file")
        self.assertEqual(item_id5, item5.item_id, "Check if they have the same id")
        self.assertEqual("e", item5.item_name, "Check if they have the same name")
        self.assertEqual(ItemType.FILE, item5.item_type, "Check if they have the same type")
        self.assertEqual(item_id3, item5.parent_id, "Check if they have the same parent id")
        self.assertEqual(65, item5.item_size, "Check if they have the same size")
        self.assertEqual("06-10-2022", item5.last_modified, "Check if they have the same last modification date")
    
    def test_load_item(self):
        repo = SingletonFsRepository()
        repo.begin_session()
        item_id1 = repo.add_fs_item("a", ItemType.DIRECTORY, 0, 50, "02-10-2022")
        item_id2 = repo.add_fs_item("b", ItemType.FILE, item_id1, 100, "03-10-2022")
        item_id3 = repo.add_fs_item("c", ItemType.DIRECTORY, item_id1, 70, "04-10-2022")
        item_id4 = repo.add_fs_item("d", ItemType.SYMLINK, item_id3, 90, "05-10-2022")
        item_id5 = repo.add_fs_item("e", ItemType.FILE, item_id3, 65, "06-10-2022")
        
        item1 =repo.load_item_by_id(item_id1)
        item4 =repo.load_item_by_id(item_id4)
        item5 =repo.load_item_by_id(item_id5)
        
        item6 = repo.load_item_by_id(0)
        
        self.assertIsNone(item6, "Check for nonexisting items")
        
        #item1
        self.assertIsNotNone(item1, "The item has been saved in the storage file")
        self.assertEqual(item_id1, item1.item_id, "Check if they have the same id")
        self.assertEqual("a", item1.item_name, "Check if they have the same name")
        self.assertEqual(ItemType.DIRECTORY, item1.item_type, "Check if they have the same type")
        self.assertEqual(0, item1.parent_id, "Check if they have the same parent id")
        self.assertEqual(50, item1.item_size, "Check if they have the same size")
        self.assertEqual("02-10-2022", item1.last_modified, "Check if they have the same last modification date")
        
        #item4
        self.assertIsNotNone(item4, "The item has been saved in the storage file")
        self.assertEqual(item_id4, item4.item_id, "Check if they have the same id")
        self.assertEqual("d", item4.item_name, "Check if they have the same name")
        self.assertEqual(ItemType.SYMLINK, item4.item_type, "Check if they have the same type")
        self.assertEqual(item_id3, item4.parent_id, "Check if they have the same parent id")
        self.assertEqual(90, item4.item_size, "Check if they have the same size")
        self.assertEqual("05-10-2022", item4.last_modified, "Check if they have the same last modification date")
    
        #item5
        self.assertIsNotNone(item5, "The item has been saved in the storage file")
        self.assertEqual(item_id5, item5.item_id, "Check if they have the same id")
        self.assertEqual("e", item5.item_name, "Check if they have the same name")
        self.assertEqual(ItemType.FILE, item5.item_type, "Check if they have the same type")
        self.assertEqual(item_id3, item5.parent_id, "Check if they have the same parent id")
        self.assertEqual(65, item5.item_size, "Check if they have the same size")
        self.assertEqual("06-10-2022", item5.last_modified, "Check if they have the same last modification date")
    
    
        repo.end_session()
    
    def test_load_items(self):
        repo = SingletonFsRepository()
        repo.begin_session()
        item_id1 = repo.add_fs_item("a", ItemType.DIRECTORY, 0, 50, "02-10-2022")
        item_id2 = repo.add_fs_item("b", ItemType.FILE, item_id1, 100, "03-10-2022")
        item_id3 = repo.add_fs_item("c", ItemType.DIRECTORY, item_id1, 70, "04-10-2022")
        item_id4 = repo.add_fs_item("d", ItemType.SYMLINK, item_id3, 90, "05-10-2022")
        item_id5 = repo.add_fs_item("e", ItemType.FILE, item_id3, 65, "06-10-2022")
        
        item1, item4, item5, item6  =repo.load_items_by_id([item_id1, item_id4, item_id5, 0])
        
        self.assertIsNone(item6, "Check for non existing items")
        
        #item4
        self.assertIsNotNone(item4, "The item has been saved in the storage file")
        self.assertEqual(item_id4, item4.item_id, "Check if they have the same id")
        self.assertEqual("d", item4.item_name, "Check if they have the same name")
        self.assertEqual(ItemType.SYMLINK, item4.item_type, "Check if they have the same type")
        self.assertEqual(item_id3, item4.parent_id, "Check if they have the same parent id")
        self.assertEqual(90, item4.item_size, "Check if they have the same size")
        self.assertEqual("05-10-2022", item4.last_modified, "Check if they have the same last modification date")

