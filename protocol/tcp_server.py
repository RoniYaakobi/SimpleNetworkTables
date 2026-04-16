__author__ = "RONI YAAKOBI"
import struct

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from protocol.tcp_socket import TcpSocket
from protocol.protocol_constants import ProtocolConstants
from cryptography.hazmat.primitives.asymmetric import padding,dh 
from cryptography.hazmat.primitives import hashes,serialization

class ClientSocketWrapper:
    def __init__(self, sock):
        self.sock = sock
        self.aes_key = None

    def accept_secure(self, rsa_private_key= None, rsa_public_key=None, dh_parameters=None):
        choice = self.recv(1)
        self.encryption_type = ProtocolConstants.EncryptionType(struct.unpack("!B", choice)[0])

        match(self.encryption_type):
            case ProtocolConstants.EncryptionType.RSA:
                self.send(struct.pack("!B",True))
                return self.accept_secure_rsa(rsa_private_key, rsa_public_key)
            case ProtocolConstants.EncryptionType.DH:
                self.send(struct.pack("!B",True))
                return self.accept_secure_dh(dh_parameters)
            case _:
                self.send(struct.pack("!B",False))
                self.connected = False
                return False

    def accept_secure_rsa(self, rsa_private_key, rsa_public_key):
        client_message = self.raw_recv_by_size()
        if client_message.decode() != ProtocolConstants.ACK:
            self.connected = False
            return False
        
        public_key_bytes = rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.raw_send_with_size(public_key_bytes)

        aes_key_encrypted = self.raw_recv_by_size()

        self.aes_key = rsa_private_key.decrypt(
            aes_key_encrypted,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.send_with_size(ProtocolConstants.ACK)
        self.connected = True
        return True
    
    def accept_secure_dh(self, dh_parameters):
        client_message = self.raw_recv_by_size()
        if client_message.decode() != ProtocolConstants.ACK:
            self.connected = False
            return False
        
        params_bytes = dh_parameters.parameter_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.ParameterFormat.PKCS3)
        
        self.raw_send_with_size(params_bytes)

        client_public_bytes = self.raw_recv_by_size()

        client_public_key = serialization.load_pem_public_key(client_public_bytes)

        server_private_key = dh_parameters.generate_private_key()
        server_public_key = server_private_key.public_key()
        
        server_public_bytes = server_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        self.raw_send_with_size(server_public_bytes)
        
        shared_secret = server_private_key.exchange(client_public_key)

        self.aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=ProtocolConstants.ACK.encode(),
        ).derive(shared_secret)
        

        self.send_with_size(ProtocolConstants.ACK)
        self.connected = True
        return True
        
        

    def recv(self, num_bytes):
        return self.sock.recv(num_bytes)
    
    def send(self, buffer):
        return self.sock.send(buffer)

    def recv_by_size(self, *args, **kwargs):
        return TcpConnection.recv_by_size(self, *args, **kwargs)

    def send_with_size(self, *args, **kwargs):
        return TcpConnection.send_with_size(self, *args, **kwargs)
    
    def raw_recv_by_size(self, *args, **kwargs):
        return TcpConnection.raw_recv_by_size(self, *args, **kwargs)

    def raw_send_with_size(self, *args, **kwargs):
        return TcpConnection.raw_send_with_size(self, *args, **kwargs)

    def build_response(self, *args, **kwargs):
        return TcpConnection.build_response(self, *args, **kwargs)

    def deconstruct_request(self, *args, **kwargs):
        return TcpConnection.deconstruct_request(self, *args, **kwargs)



class TcpConnection(TcpSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_response(self, code, *args):
        return code + TcpSocket.FIELD_DELIMETER.join(args)
    
    def deconstruct_request(self, message):
        code = message[:3].decode()
        fields = message[3:].decode().split(TcpSocket.FIELD_DELIMETER)
        return code, fields


if __name__ == "__main__":
    from cryptography.hazmat.primitives.asymmetric import dh
    from cryptography.hazmat.primitives import serialization
    import os,socket

    ENCRYPT_PATH = r"C:\Users\roniy\software_engeeniering\11th\finalProject\server"
    PRIVATE_PATH = os.path.join(ENCRYPT_PATH, "RSA_private.pem")
    PUBLIC_PATH = os.path.join(ENCRYPT_PATH, "RSA_public.pem")
    DH_PATH = os.path.join(ENCRYPT_PATH, "DH.pem")

    def generate_params():
        dh_params = dh.generate_parameters(generator=2, key_size=2048)


        # Save public key (SPKI + PEM)
        with open(DH_PATH, "wb") as f:
            f.write(dh_params.parameter_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.ParameterFormat.PKCS3
            ))

        print(f"DH params generated!")


    def load_parmeters():
        with open(DH_PATH, "rb") as f:
            return serialization.load_pem_parameters(f.read())

    
    if not os.path.exists(DH_PATH):
        generate_params()

    params = load_parmeters()

    server_sock = socket.socket()

    import host.server_constants
    server_sock.bind(host.server_constants.ServerConstants.ADDR)
    server_sock.listen(5)
    client_socket,_ = server_sock.accept()
    client = ClientSocketWrapper(client_socket)
    print(client.accept_secure(dh_parameters = params))
    print("test")
    print(client.recv_by_size())


