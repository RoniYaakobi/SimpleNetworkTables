__author__ = "RONI YAAKOBI"
import socket, os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class TcpSocket(socket.socket):
    """A parent of the tcp client and server. holds the functions they have in common
    """
    SIZE_HEADER_FORMAT = "00000000|"  # n digits for data size + one delimiter
    size_header_size = len(SIZE_HEADER_FORMAT)
    TCP_DEBUG = True
    LEN_TO_PRINT = 100
    FIELD_DELIMETER = '``````````````````````````````````````' # well this isn't technically safe, but I am not changing my tcp by size implementation for nothing lol 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def send_with_size(self, bdata: bytes | str):
        """Send bytes with a size header for recv_by_size

        Args:
            bdata (bytes | str): the data to send to the other socket
        """
        if type(bdata) != bytes:
            bdata = bdata.encode()

        padder = padding.PKCS7(128).padder()
        padded = padder.update(bdata) + padder.finalize()


        iv = os.urandom(16)

        cipher = Cipher(algorithm=algorithms.AES256(self.aes_key), mode=modes.CBC(iv))

        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(padded) + encryptor.finalize()

        msg = iv + ciphertext

        self.raw_send_with_size(msg)

    def recv_by_size(self) -> bytes:
        """Waits until received a message as specified by the tcp by size protocol. Returns the bytes of the message.

        Returns:
            bytes: the message that was recieved
        """
        raw = self.raw_recv_by_size()

        iv, ciphertext = raw[:16], raw[16:]

        cipher = Cipher(algorithm=algorithms.AES256(self.aes_key), mode=modes.CBC(iv))

        decryptor = cipher.decryptor()

        padded_message = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()

        message = unpadder.update(padded_message) + unpadder.finalize()

        return message

    def raw_recv_by_size(self) -> bytes:
        """recv by size but without encryption

        Returns:
            bytes: the bytes that have been recieved
        """
        size_header = b''
        data_len = 0
        while len(size_header) < TcpSocket.size_header_size:
            _s = self.recv(TcpSocket.size_header_size - len(size_header))
            if _s is None:
                size_header = b''
                break
            size_header += _s
        # Now, the size header field has entirely received in size_header (which is binary).
        data = b''
        if size_header != b"":
            data_len = int(size_header[:TcpSocket.size_header_size - 1])
            while len(data) < data_len:
                _d = self.recv(data_len - len(data))
                if _d is None:
                    data = b""
                    break
                data += _d

        if TcpSocket.TCP_DEBUG and size_header is not None:
            print(f"\nRecv({int(size_header[:-1])})>>>{data[:TcpSocket.LEN_TO_PRINT]}")
        if data_len != len(data):
            data = b""  # Partial data is like no data !
        return data


    def raw_send_with_size(self, bdata: bytes | str):
        """sends data with no encryption according to tc[ by size]

        Args:
            bdata (bytes | str): the raw data that is to be sent
        """
        if type(bdata) != bytes:
            bdata = bdata.encode()
        len_data = len(bdata)
        header_data = str(len(bdata)).zfill(TcpSocket.size_header_size - 1).encode() + b"|"
        bytea = header_data + bdata

        self.send(bytea)
        
        if TcpSocket.TCP_DEBUG and len_data > 0:
            print(f"\nSent({len_data})>>>{bytea[:TcpSocket.LEN_TO_PRINT]}")