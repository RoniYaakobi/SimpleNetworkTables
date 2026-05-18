__author__ = "RONI YAAKOBI"
#TODO DOCUMENTATION
import threading, os
import time, socket

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dh

from protocol.tcp_server import TcpConnection, ClientSocketWrapper
from protocol.protocol_constants import ProtocolCode, ProtocolError, ACK, EncryptionType

from host.Request import Request
from host.server_constants import ServerConstants
from host.Database import DataBase
from host.send_email import send_email

class Server:
    def __init__(self):
        if not os.path.exists(ServerConstants.PRIVATE_PATH) or not os.path.exists(ServerConstants.PUBLIC_PATH):
            Server.generate_keys()

        self.RSA_PRIVATE_KEY = Server.load_private_key()
        self.RSA_PUBLIC_KEY = Server.load_public_key()


        if not os.path.exists(ServerConstants.DH_PATH):
            Server.generate_params_dh()

        self.DH_PARAMS = Server.load_parmeters_dh()

        self.server = socket.socket()
        self.server.bind(ServerConstants.ADDR)
        self.server.listen(5)
        self.lock = threading.Lock()
        self.thread_dict_lock = threading.Lock()
        self.sock_to_requests = {}

        self.clients_to_threads = {}

        DataBase.load()

        self.business_logic_requests = dict()

        self.business_logic_requests[ProtocolCode.LOGIN] = \
        Request(self.login, ProtocolCode.LOGIN, [
            ProtocolError.INVALID_AUTH
        ])

        self.business_logic_requests[ProtocolCode.REGISTER] = \
        Request(self.register, ProtocolCode.REGISTER, [
            ProtocolError.USERNAME_TAKEN,
            ProtocolError.EMAIL_TAKEN
        ])
        
        self.business_logic_requests[ProtocolCode.VERIFY_REGISTER] = \
        Request(self.verify, ProtocolCode.VERIFY_REGISTER, [
            ProtocolError.INVALID_AUTH,
            ProtocolError.WRONG_CODE
        ])
        
        self.business_logic_requests[ProtocolCode.RESEND_CODE] = \
        Request(self.resend_code, ProtocolCode.RESEND_CODE, [
            ProtocolError.USER_ALREADY_VALID,
            ProtocolError.INVALID_AUTH
        ])

        self.business_logic_requests[ProtocolCode.FORGOT_PASSWORD] = \
        Request(self.forgot, ProtocolCode.FORGOT_PASSWORD, [
            ProtocolError.WRONG_EMAIL
        ])

        self.business_logic_requests[ProtocolCode.VERIFY_FORGOT] = \
        Request(self.verify_with_email, ProtocolCode.VERIFY_FORGOT, [
            ProtocolError.WRONG_EMAIL,
            ProtocolError.WRONG_CODE
        ])

        self.business_logic_requests[ProtocolCode.RESET_PASSWORD] = \
        Request(self.reset_password, ProtocolCode.RESET_PASSWORD, [
            ProtocolError.WRONG_EMAIL,
            ProtocolError.WRONG_CODE
        ])

        self.business_logic_requests[ProtocolCode.RESEND_FORGOT_MAIL] = \
        Request(self.resend_code_email, ProtocolCode.RESEND_FORGOT_MAIL, [
            ProtocolError.WRONG_EMAIL
        ])

        while True:
            client,_ = self.server.accept()
            client = ClientSocketWrapper(client)
            thread = threading.Thread(target=self.deal_with_async_client, args=(client,), daemon=True)
            self.clients_to_threads[client] = [False, thread]
            thread.start()
            

    def deal_with_async_client(self, client: ClientSocketWrapper):
        """Delegates the responsibilities of the client asynchronously 

        Args:
            client (ClientSocketWrapper): client socket
        """
        is_connected = client.accept_secure(rsa_private_key=self.RSA_PRIVATE_KEY,
                                             rsa_public_key=self.RSA_PUBLIC_KEY,
                                             dh_parameters=self.DH_PARAMS)
        if not is_connected:
            del self.clients_to_threads[client]
        
        listen_thread = threading.Thread(target=self.listen_to_client, args=(client,), daemon= True)
        business_logic= threading.Thread(target=self.business_logic, args=(client,), daemon= True)
        self.clients_to_threads[client] += [listen_thread, business_logic]
        listen_thread.start()
        business_logic.start()
        
        
        listen_thread.join()
        business_logic.join()

        del self.clients_to_threads[client]



    def listen_to_client(self, client: ClientSocketWrapper):
        """Listens to a client and polls it's requests

        Args:
            client (ClientSocketWrapper): the client socket
        """
        while True:
            
            with self.thread_dict_lock:
                terminate = self.clients_to_threads[client][0]
                if terminate:
                    break

            try:
                msg = client.recv_by_size()
                if not msg:
                    break
            except:
                self.clients_to_threads[0] = True # terimination
                break

            with self.lock:
                if self.sock_to_requests.get(client):
                    self.sock_to_requests[client].append(msg)
                else:
                    self.sock_to_requests[client] = [msg]

    def business_logic(self, client: TcpConnection):
        """Dispatch the requests to their respective handlers

        Args:
            client (TcpConnection): the given client to dispatch
        """
        while True:
            with self.thread_dict_lock:
                terminate = self.clients_to_threads[client][0]
                if terminate:
                    break
            
            with self.lock:
                try:
                    requests = self.sock_to_requests[client]
                    self.sock_to_requests[client] = []
                except KeyError:
                    requests = []
                    self.sock_to_requests[client] = []

            for request in requests:
                code, fields = client.deconstruct_request(request)
                self.business_logic_requests[code].respond(client, *fields)


    def register(self, fields: list[str], client: ClientSocketWrapper) -> tuple[bool, bool]:
        """Register a new user

        Args:
            fields (list[str]): the fields in the request

        Returns:
            tuple[bool, bool]: if the username already exists, if the email is already used
        """
        print(fields)
        username = fields[0]
        password = fields[1]
        email = fields[2]

        if DataBase.IsUserExist(username) or DataBase.IsEmailUsed(email):
            return DataBase.IsUserExist(username), DataBase.IsEmailUsed(email)
        
        code = DataBase.SaveUser(username, email, password)

        send_email(email, "Verification code", code)

        return False, False
            


    def login(self, fields: list[str], client: ClientSocketWrapper) -> bool:
        """Login a new user

        Args:
            fields (list[str]): request fields
            client (ClientSocketWrapper): the client in question

        Returns:
            bool: whether the login failed
        """
        username = fields[0]
        password = fields[1]

        if not (DataBase.IsUserExist(username) and
                 DataBase.IsPasswordOK(username, password) and DataBase.IsVerified(username)):
            return True 
        
        client.username = username
        return False
    
    def resend_code(self, fields: list[str], client: ClientSocketWrapper) -> tuple[bool, bool]:
        """Resend the code to the user

        Args:
            fields (list[str]): The request's field
            client (ClientSocketWrapper): The client's socket

        Returns:
            tuple[bool, bool]: user already exists, user already verified
        """
        username = fields[0]

        if (not DataBase.IsUserExist(username) or DataBase.IsVerified(username)):
            return DataBase.IsUserExist(username), DataBase.IsVerified(username)
        
        email = DataBase.GetUserEmail(username)
        code = DataBase.ResetCode(username)

        if code != -1:
            send_email(email,"Verification code", str(code))
            return False, False,
            
        
        return True, True  
      
    def verify(self, fields: list[str], client: ClientSocketWrapper) -> tuple[bool, bool]:
        """Verify the client

        Args:
            fields (list[str]): request's fields
            client (ClientSocketWrapper): client socket

        Returns:
            tuple[bool, bool]: whether or not the password is right, whether the code is right
        """
        username = fields[0]
        password = fields[1]
        code = fields[2]

        return not DataBase.IsPasswordOK(username,password), not DataBase.ValidateAccount(username, code)
    
    def forgot(self, fields: list[str], client: ClientSocketWrapper) -> bool:
        """Send the reset code to the client

        Args:
            fields (list[str]): the request's fields
            client (ClientSocketWrapper): the client's socket

        Returns:
            bool: is an email invalid
        """
        email = fields[0]

        code = DataBase.ResetCodeByEmail(email)
        if code != -1:
            send_email(email,"Verification code", str(code))
            return False

        return True
    
    def reset_password(self, fields: list[str], client: ClientSocketWrapper) -> list[bool, bool]:
        """Reset the password

        Args:
            fields (list[str]): the request's fields
            client (ClientSocketWrapper): the client' socket

        Returns:
            list[bool, bool]: whether or not the email is valid, and whether or not the code is valid
        """
        email = fields[0]
        code = fields[1]
        new_password = fields[2]

        is_valid_email = DataBase.IsEmailUsed(email)

        if not is_valid_email:
            return True, False
        

        is_valid_code = DataBase.VerifyCodeForgot(email, code)
        if not is_valid_code:
            return False, True
        
        DataBase.ResetPassword(email, new_password)

        return False, False
             
    def resend_code_email(self, fields: list[str], client: ClientSocketWrapper) -> bool:
        """Resend the code with the email as the key

        Args:
            fields (list[str]): the request's fields
            client (ClientSocketWrapper): the client's socket

        Returns:
            bool: if the database was missing the email
        """
        email = fields[0]

        code = DataBase.ResetCodeByEmail(email)

        if code != -1:
            send_email(email,"Verification code", str(code))
            return False
        
        return True

    def verify_with_email(self, fields: list[str], client: ClientSocketWrapper) -> tuple[bool, bool]:
        """Verify if a email exists

        Args:
            fields (list[str]): request fields
            client (ClientSocketWrapper): client socket

        Returns:
            tuple[bool, bool]: email invalid, code invalid
        """
        email = fields[0]
        code = fields[1]

        is_valid_email = DataBase.IsEmailUsed(email)

        if is_valid_email:
            is_valid_code = DataBase.VerifyCodeForgot(email, code)
            return not is_valid_email, not is_valid_code
        else:
            return not is_valid_email, False       
    
    
    @staticmethod
    def generate_keys():
        """Generate RSA keys"""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # Save private key (PKCS8 + PEM)
        with open(ServerConstants.PRIVATE_PATH, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save public key (SPKI + PEM)
        with open(ServerConstants.PUBLIC_PATH, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

        print(f"RSA keys generated!")

    @staticmethod
    def load_private_key():
        """Load the private RSA key"""
        with open(ServerConstants.PRIVATE_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    @staticmethod
    def load_public_key():
        """Load the public RSA key"""
        with open(ServerConstants.PUBLIC_PATH, "rb") as f:
            return serialization.load_pem_public_key(f.read())

    @staticmethod
    def generate_params_dh():
        """Generate the Diffie Hellman parameters"""
        dh_params = dh.generate_parameters(generator=2, key_size=2048)


        # Save public key (SPKI + PEM)
        with open(ServerConstants.DH_PATH, "wb") as f:
            f.write(dh_params.parameter_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.ParameterFormat.PKCS3
            ))

        print(f"DH params generated!")

    @staticmethod
    def load_parmeters_dh():
        """Load the Diffie Hellman parameters"""
        with open(ServerConstants.DH_PATH, "rb") as f:
            return serialization.load_pem_parameters(f.read())


if __name__ == "__main__":
    Server()
