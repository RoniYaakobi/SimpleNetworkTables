from __future__ import annotations
from typing import Optional
from enum import Enum
from dataclasses import dataclass
from protocol.tcp_server import ClientSocketWrapper

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

    @staticmethod
    def format(type: EntryType, value_bytes: bytes):
        match (type):
            case EntryType.PLACEHOLDER:
                return "null"
            case EntryType.BOOLEAN:
                print(int(value_bytes.decode(), 16))
                return "true" if int(value_bytes.decode(), 16) > 0 else "false"
            case EntryType.INT_64:
                return str(int(value_bytes.decode(), 16))
            case EntryType.STRING:
                return hex_str_to_bytes(value_bytes.decode("utf-8"))
            case _:
                return "null"


def hex_str_to_bytes(string):
    total = 0
    for c in string:
        total = total * 16 + int(c ,16)
    
    new_str = ""
    while total != 0:
        new_str += chr(total % 256)
        total //= 256

    return new_str[::-1]

class _Subscriber:
    """Stores in an object the client and whether or not it is updated"""
    def __init__(self, client):
        self.__client = client
        self.__updated = False

    @property
    def updated(self):
        return self.__updated
    
    @updated.setter
    def updated(self, value: bool):
        self.__updated = value

class Entry:
    def __init__(self, topic: str, entry_type: EntryType, value_bytes: bytes):
        """NT entry"""
        self.__topic: str =  topic
        self._type : EntryType = entry_type
        self._value_bytes : bytes = value_bytes
        self._children : dict[str, Entry] = dict()

        # 
        self.__subscribers : dict[ClientSocketWrapper ,_Subscriber] = dict()

    @property
    def type(self) -> EntryType:
        """The entry type"""
        return self._type
    
    @type.setter
    def type(self, value):
        self._type = value
    
    @property
    def value_bytes(self) -> bytes:
        """The bytes of the entry's value"""
        return self._value_bytes
    
    @value_bytes.setter
    def value_bytes(self, value_bytes: bytes):

        self._value_bytes = value_bytes[2:-1]

    def get_child(self, topic: str) -> Optional[Entry]:
        """Get the child entry at this topic"""
        return self._children.get(topic)
    
    def add_child(self, topic: str, entry: Entry) -> bool:
        """Add a child entry of a topic, if it doesn't already exist, to this table"""
        child_already_exists = not self.get_child(topic) is None
        
        if not child_already_exists:
            self._children[topic] = entry

        return child_already_exists
    
    def subscribe(self, client: ClientSocketWrapper) -> bool:
        """Subscribe to a given entry

        Args:
            client (ClientSocketWrapper): I really don't care as long as it can send stuff

        Returns:
            bool: if client already subscribed
        """

        print(client.username + " subscribed to " + self.__topic)
        if not client in self.__subscribers.keys():
            self.__subscribers[client] = _Subscriber(client)
            return False
        return True

    def print_all(self, path=""):
        """Print all the children and the current node"""
        subs = list(self.__subscribers.values())
        print(path ,self._type, self._value_bytes)
        print([sub.updated for sub in subs])

        for key, child in self._children.items():
            child.print_all(path + "/" + key)

    def get_all_children(self, path= "") -> list[tuple[str, Entry]]:
        """Get all the children"""
        family = [self]
        for key, child in self._children.items():
            family.extend(child.get_all_children(path + "/" + key))
        
        return family
    
    @staticmethod
    def create_null(path = ""):
        """Create an empty entry

        Args:
            path (str): the topic ,defaults to ""

        Returns:
            Entry: a null entry
        """
        return Entry(path, EntryType.PLACEHOLDER, 0x00.to_bytes())
    
    def get_topics_for_client_update(self, client: ClientSocketWrapper,  __child_of_subscribed: bool = False) -> list[Entry]:
        """Get all the topics for updating a client

        Args:
            client (ClientSocketWrapper): the client
            __child_of_subscribed (bool, optional): Internal flag.

        Returns:
            list[Entry]: A list of entries
        """

        is_subscribed = (client in self.__subscribers) or __child_of_subscribed

        needs_update = is_subscribed and not self.__subscribers.get(client).updated
        family = [self] if needs_update else []
        for child in self._children.values():
            family.extend(child.get_topics_for_client_update(client, is_subscribed))

        return family
    
    @property
    def topic(self):
        return self.__topic
    
    def subscriber_updated(self, client):
        """ Mark client as updated """
        self.__subscribers.get(client).updated = True

    def publish(self, entry_type : EntryType, new_value: bytes):
        self.type = entry_type
        self.value_bytes = new_value

        print(self.__topic + " -> " + str(self.value_bytes))

        self.mark_all_as_outdated()
    

    def mark_all_as_outdated(self):
        for subscriber in self.__subscribers.values():
            subscriber.updated = False