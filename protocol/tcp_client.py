__author__ = "RONI YAAKOBI"
import struct, os
from typing import Tuple
from protocol.protocol_constants import ProtocolConstants
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from protocol.tcp_socket import TcpSocket
from client.src.BackendConstants import BackendConstants
from cryptography.hazmat.primitives.kdf.hkdf import HKDF



class TcpClient(TcpSocket):
    """The client variation of tcp socket
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aes_key = TcpClient.__generate_aes_key()

    def set_addr(self, addr: Tuple[str, int]):
        """Set the address of the socket to

        Args:
            addr (Tuple[str, int]): the address
        """
        self.addr = addr
        
    def build_request(self, code: str, *args) -> str:
        """Build the request to the server

        Args:
            code (str): 

        Returns:
            str: The request and the fields in one string
        """
        return code + TcpClient.FIELD_DELIMETER.join(args)
    

    def deconstruct_response(self, message: str) -> Tuple[str, list[str]]:
        """ Deconstruct the server response into fields

        Args:
            message (str): the message that needs to be deconstructed 

        Returns:
            Tuple[str, list[str]]: What ended up being deconstructed
        """
        code = message[:3].decode()
        fields = message[3:].decode().split(TcpClient.FIELD_DELIMETER)
        return code, fields
    
    def __validate_server_support(self, encryption_type: ProtocolConstants.EncryptionType) -> bool:
        """Check if the server supports a certain encryption type

        Args:
            encryption_type (ProtocolConstants.EncryptionType): What encryption type to check

        Returns:
            bool: whether or not the server actually supports the encryption
        """
        self.send(struct.pack("!B", encryption_type.value))
        return struct.unpack("!B", self.recv(1))[0] == 1
    
    def connect_rsa(self) -> bool:
        """Secure connect via RSA to the server

        Returns:
            bool: whether or not the connection happened
        """
        self.connect(self.addr)
        server_supports_method = self.__validate_server_support(ProtocolConstants.EncryptionType.RSA)
        if not server_supports_method:
            self.connected = False
            return False
        
        self.raw_send_with_size(ProtocolConstants.ACK)
        public_key_bytes = self.raw_recv_by_size()
        self.server_public_key_rsa = serialization.load_pem_public_key(public_key_bytes)

        self.__send_aes_with_rsa()

        return self.__verify_connection()



    def __send_aes_with_rsa(self):
        """
            Send the AES key ecrypted with rsa
        """
        aes_key = self.server_public_key_rsa.encrypt(
            self.aes_key,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),  
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.raw_send_with_size(aes_key)

    def connect_dh(self) -> bool:
        """Connect secure with diffie hellman

        Returns:
            bool: whether or not the connection worked
        """
        self.connect(self.addr)
        server_supports_method = self.__validate_server_support(ProtocolConstants.EncryptionType.DH)
        if not server_supports_method:
            self.connected = False
            return False
        
        self.raw_send_with_size(ProtocolConstants.ACK)
        
        params_bytes = self.raw_recv_by_size()
        dh_params = serialization.load_pem_parameters(params_bytes)

        client_private_key_dh = dh_params.generate_private_key()
        client_public_key = client_private_key_dh.public_key()

        client_public_bytes = client_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        self.raw_send_with_size(client_public_bytes)


        public_key_bytes = self.raw_recv_by_size()
        server_public_key_dh = serialization.load_pem_public_key(public_key_bytes)
        shared_secret = client_private_key_dh.exchange(server_public_key_dh)

        self.aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=ProtocolConstants.ACK.encode(),
        ).derive(shared_secret)

        self.send_with_size(ProtocolConstants.ACK)

        return self.__verify_connection()

    def __verify_connection(self) -> bool:
        """Verify the secure connection to the server worked

        Returns:
            bool: whether or not the server connected
        """
        response = self.recv_by_size()
        if response.decode() == ProtocolConstants.ACK:
            self.connected = True
            return True
        else:
            print("Error: Server failed to respond with AES ack")
            self.connected = False
            return False

    @staticmethod
    def __generate_aes_key() -> bytes:
        """Create the aes key for the client

        Returns:
            _type_: _description_
        """
        return os.urandom(32)
    
if __name__ == "__main__":
    client = TcpClient()
    client.set_addr(BackendConstants.SERVER_ADDR)
    print(client.connect_dh())
    print("test")
    client.send_with_size("YAY")
