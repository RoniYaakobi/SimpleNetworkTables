__author__ = "RONI YAAKOBI"

#TODO DOCUMENTATION
import threading 
from dataclasses import dataclass
from enum import StrEnum

from protocol.tcp_client import TcpClient
from protocol.protocol_constants import ProtocolCode, EncryptionType
from protocol.Entry import EntryType

from .BackendConstants import BackendConstants

@dataclass 
class Message:
    """ A message from the server """
    code: str
    fields: list

@dataclass
class ErrorMessage(Message):
    """ An error message from the server """
    handled: bool = False

@dataclass
class Entry:
    """ Network tables entry record from the server """
    entry_type: EntryType
    value_bytes: bytes

class ConnectionStatus(StrEnum):
    Disconnected = "Disconnected"
    Connecting = "Connecting"
    Connected = "Connected"



class AppBackend:
    def __init__(self):
        super().__init__()
        self.socket = TcpClient()
        self.socket.set_addr(BackendConstants.SERVER_ADDR)
        self.messages = []
        self.errors = []
        self.lock = threading.Lock()

        self.connection_status = ConnectionStatus.Disconnected
        self.network_tables = dict()

        self.encryption_type = None

        self.username = None
        self.email = None
        self.password = None
        self.code = None

    def set_encryption_type(self, encryption_type):
        self.encryption_type = encryption_type

    def is_connected(self):
        return self.connection_status == ConnectionStatus.Connected
    
    def is_connecting(self):
        return self.connection_status == ConnectionStatus.Connecting
    
    def get_lock(self):
        return self.lock

    def set_password(self, password):
        self.password = password
    
    def reset_password(self):
        self.password = None

    def set_username(self, username):
        self.username = username
    
    def reset_username(self):
        self.username = None

    def get_username(self):
        return self.username

    def set_email(self, email):
        self.email = email
    
    def reset_email(self):
        self.email = None

    def get_email(self):
        return self.email

    def set_code(self, code):
        self.code = code
    
    def reset_code(self):
        self.code = None

    def get_topic(self, topic):
        print(self.network_tables)
        return self.network_tables.get(topic)

    def connect(self):
        """ Try opening a secure session with the server. If succeeded, initialize async communication. """

        self.connection_status = ConnectionStatus.Connecting
        if self.encryption_type == EncryptionType.RSA:
            self.connection_status = ConnectionStatus.Connected if self.socket.connect_rsa() else ConnectionStatus.Disconnected 
        else:
            self.connection_status = ConnectionStatus.Connected if self.socket.connect_dh() else ConnectionStatus.Disconnected

        if (self.is_connected()):
            self.updateThread = threading.Thread(target=self._update, daemon=True)
            self.updateThread.start()

    def login(self) -> bool:
        """ Attempt to login to the server

        Returns:
            bool: Whether or not you managed to send the login request.
        """
        try:
            self.socket.send_with_size(self.socket.build_request(ProtocolCode.LOGIN, self.username, self.password))
            return True
        except Exception as e:
            print(e)
            return False

    def register(self) -> bool:
        """
        Returns:
            bool: Whether or not the register request went through.
        """
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.REGISTER, self.username, self.password , self.email)
            )
            return True
        except Exception as e:
            print(e)
            return False
    
    def forgot_password(self) -> bool:
        """
        Returns:
            bool: Whether or not the request go through
        """
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.FORGOT_PASSWORD, self.email)
            )

            return True
        except Exception as e:
            print(e)
            return False
        
    def reset_password(self):
        """
        Returns:
            bool: Whether or not the request go through
        """
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.RESET_PASSWORD, self.email, self.code, self.password)
            )

            return True
        except Exception as e:
            print(e)
            return False
        
    def verify_account(self):
        """
        Returns:
            bool: Whether or not the request go through
        """
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.VERIFY_REGISTER, self.username, self.password, self.code)
            )

            return True
        except Exception as e:
            print(e)
            return False
        
    def verify_for_reset(self):
        """
        Returns:
            bool: Whether or not the request go through
        """
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.VERIFY_FORGOT, self.email, self.code)
            )

            return True
        except Exception as e:
            print(e)
            return False
    
    def reset_code(self, email=False):
        """
        Returns:
            bool: Whether or not the request went through
        """
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.RESEND_CODE, self.username)
            )

            return True
        except Exception as e:
            print(e)
            return False

    def reset_code_password(self):
        """
        Returns:
            bool: Whether or not the request go through
        """
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.RESEND_FORGOT_MAIL, self.email)
            )

            return True
        except Exception as e:
            print(e)
            return False

    def subscribe(self, topic : str):
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.SUBSCRIBE, topic)
            )

            return True
        except Exception as e:
            print(e)
            return False
        
    def publish(self, topic : str, entry_type: EntryType, value_bytes: bytes):
        try:
            self.socket.send_with_size(
                self.socket.build_request(ProtocolCode.PUBLISH, topic, str(entry_type.value), str(value_bytes))
            )

            return True
        except Exception as e:
            print(e)
            return False

    def _update(self):
        """ Forever, get a message and then store it based on if it is an error or a normal response """
        while True:
            message = self.socket.recv_by_size()
            code, fields = self.socket.deconstruct_response(message)

            print(code)

            if ProtocolCode(code) is ProtocolCode.UPDATE:
                self.network_tables[fields[0]] = Entry(EntryType(int(fields[1])), bytes(fields[2][2:-1], "utf-8"))
                continue
                
            with self.lock:
                self.messages.append(Message(code,fields))
                if ProtocolCode(code) is ProtocolCode.ERROR:
                    self.errors.append(ErrorMessage(fields[0],fields[1:]))
                   

    def get_messages_of_type(self, code: ProtocolCode) -> tuple[list[Message], list[ErrorMessage]]:
        """Equivalent to SELECT * WHERE code == {code}

        Args:
            code (ProtocolCode): the message code which you need

        Returns:
            tuple[list[Message], list[ErrorMessage]]: a list of those messages, and their respective error messages.
        """

        code_responses = []
        error_messages = []

        with self.lock:
            for index, message in enumerate(self.messages):
                if ProtocolCode(message.code) is code:
                    code_responses.append(message)

                    self.messages.pop(index)
                    


            remove_indices = []
            for index,error in enumerate(self.errors):
                if ProtocolCode(error.code) is code:
                    error_messages.append(error)

                    remove_indices.append(index)

            for i in remove_indices[::-1]:
                self.errors.pop(i)



        return code_responses, error_messages
