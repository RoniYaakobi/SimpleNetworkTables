from __future__ import annotations
from typing import Optional
from enum import Enum

class EntryType(Enum):
    PLACEHOLDER = -1
    BOOLEAN = 0
    INT_64 = 1
    FLOAT_64 = 2
    STRING = 3
    BYTES = 4
    ARRAY_INT_64 = 5 
    ARRAY_FLOAT_64 = 6 
    ARRAY_BOOLEAN = 7

class Entry:
    def __init__(self, entry_type: EntryType, value_bytes: bytes):
        """NT entry"""
        self._type : EntryType = entry_type
        self._value_bytes : bytes = value_bytes
        self._children : dict[str, Entry] = dict()

    @property
    def type(self) -> EntryType:
        """The entry type"""
        return self._type
    
    @property
    def value_bytes(self) -> bytes:
        """The bytes of the entry's value"""
        return self._value_bytes
    
    @value_bytes.setter
    def value_bytes(self, value_bytes: bytes):

        self._value_bytes = value_bytes

    def get_child(self, topic: str) -> Optional[Entry]:
        """Get the child entry at this topic"""
        return self._children.get(topic)
    
    def add_child(self, topic: str, entry: Entry) -> bool:
        """Add a child entry of a topic, if it doesn't already exist, to this table"""
        child_already_exists = not self.get_child(topic) is None
        
        if not child_already_exists:
            self._children[topic] = entry

        return child_already_exists
    
    def print_all(self, path=""):
        print(path ,self._type, self._value_bytes)
        for key, child in self._children.items():
            child.print_all(path + "/" + key)
