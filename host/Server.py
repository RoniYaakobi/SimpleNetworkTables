__author__ = "RONI YAAKOBI"
#TODO DOCUMENTATION
import threading, os
import time, socket

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dh

from protocol.tcp_server import TcpConnection, ClientSocketWrapper
from protocol.protocol_constants import ProtocolConstants
from host.server_constants import ServerConstants
from host.database import DataBase
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

        while True:
            client,_ = self.server.accept()
            client = ClientSocketWrapper(client)
            thread = threading.Thread(target=self.deal_with_async_client, args=(client,), daemon=True)
            self.clients_to_threads[client] = [False, thread]
            thread.start()
            

    def deal_with_async_client(self, client):
        is_connected = client.accept_secure(rsa_private_key=self.RSA_PRIVATE_KEY,
                                             rsa_public_key=self.RSA_PUBLIC_KEY,
                                             dh_parameters=self.DH_PARAMS)
        if not is_connected:
            del self.clients_to_threads[client]

            self.async_messages.delete_socket(client)
        
        listen_thread = threading.Thread(target=self.listen_to_client, args=(client,))
        update_thread = threading.Thread(target=self.update_client_messages, args=(client,))
        business_logic= threading.Thread(target=self.business_logic, args=(client,))
        self.clients_to_threads[client] += [listen_thread, update_thread, business_logic]
        listen_thread.start()
        update_thread.start()
        business_logic.start()
        
        
        listen_thread.join()
        update_thread.join()
        business_logic.join()

        del self.clients_to_threads[client]

    def update_client_messages(self, client):
        time.sleep(1)


    def listen_to_client(self, client):
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
                if code == ProtocolConstants.CODES["login"]:
                    username_taken = self.login(fields, client)
                    if username_taken:
                        client.send_with_size(
                            client.build_response(code)
                        )
                    else:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("username or password")))
                        )


                elif code == ProtocolConstants.CODES["register"]:
                    username_taken, email_taken = self.register(fields)
                    if not username_taken and not email_taken:
                        client.send_with_size(
                            client.build_response(code)
                        )
                    elif username_taken:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("username taken")))
                        )
                    elif email_taken:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("email taken")))
                        )
                elif code == ProtocolConstants.CODES["verify"]:
                    right_email, correct_code = self.verify(fields)
                    if right_email and correct_code:
                        client.send_with_size(
                            client.build_response(code)
                        )
                    elif not correct_code:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("wrong code")))
                        )
                    elif not right_email:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("username or password")))
                        )

                elif code == ProtocolConstants.CODES["resend"]:
                    right_email, user_not_valid = self.resend_code(fields)
                    if right_email and user_not_valid:
                        client.send_with_size(
                            client.build_response(code)
                        )
                    elif not user_not_valid:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("user already valid")))
                        )
                    elif not right_email :
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("username or password")))
                        )

                elif code == ProtocolConstants.CODES["forgot"]:
                    right_email = self.forgot(fields)
                    if right_email:
                        client.send_with_size(
                            client.build_response(code)
                        )
                    else:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("wrong email")))
                        )
                
                elif code == ProtocolConstants.CODES["verforgot"]:
                    is_valid_email, is_valid_code = self.verify_with_email(fields)
                    if is_valid_email and is_valid_code:
                        client.send_with_size(
                            client.build_response(code)
                        )
                    elif not is_valid_email:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("wrong email")))
                        )
                    elif not is_valid_code:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("wrong code")))
                        )
                elif code == ProtocolConstants.CODES["reset"]:
                    is_valid_email, is_valid_code = self.reset_password(fields)
                    if is_valid_email and is_valid_code:
                        client.send_with_size(
                            client.build_response(code)
                        )
                    elif not is_valid_email:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("wrong email")))
                        )
                    elif not is_valid_code:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("wrong code")))
                        )

                elif code == ProtocolConstants.CODES["resendmail"]:
                    right_email = self.resend_code_email(fields)
                    if right_email:
                        client.send_with_size(
                            client.build_response(code)
                        )
                    else:
                        client.send_with_size(
                            client.build_response(ProtocolConstants.CODES["error"], code, 
                                                  str(ProtocolConstants.ERRORS.index("wrong email")))
                        )

    def register(self, fields):
        username = fields[0]
        password = fields[1]
        email = fields[2]

        if DataBase.IsUserExist(username) or DataBase.IsEmailUsed(email):
            return DataBase.IsUserExist(username), DataBase.IsEmailUsed(email)
        
        code = DataBase.SaveUser(username, email, password)

        send_email(email, "Verification code", code)

        return False, False
            


    def login(self, fields, client):
        username = fields[0]
        password = fields[1]

        if not (DataBase.IsUserExist(username) and
                 DataBase.IsPasswordOK(username, password) and DataBase.IsVerified(username)):
            return False 
        
        self.async_messages.connect_user(client, username)
        client.username = username
        return True
    
    def resend_code(self, fields):
        username = fields[0]

        if (not DataBase.IsUserExist(username) or DataBase.IsVerified(username)):
            return DataBase.IsUserExist(username), DataBase.IsVerified(username)
        
        email = DataBase.GetUserEmail(username)
        code = DataBase.ResetCode(username)

        if code != -1:
            send_email(email,"Verification code", str(code))
            return True, True,
            
        
        return True, True  
      
    def verify(self, fields):
        username = fields[0]
        password = fields[1]
        code = fields[2]

        if (DataBase.IsPasswordOK(username,password)):
            return True, DataBase.ValidateAccount(username, code)
        
        return False, True
    
    def forgot(self, fields):
        email = fields[0]

        code = DataBase.ResetCodeByEmail(email)
        if code != -1:
            send_email(email,"Verification code", str(code))
            return True

        return False
    
    def reset_password(self, fields):
        email = fields[0]
        code = fields[1]
        new_password = fields[2]

        is_valid_email = DataBase.IsEmailUsed(email)

        if not is_valid_email:
            return False, True
        

        is_valid_code = DataBase.VerifyCodeForgot(email, code)
        if not is_valid_code:
            return True, False
        
        DataBase.ResetPassword(email, new_password)

        return True, True
             
    def resend_code_email(self, fields):
        email = fields[0]

        code = DataBase.ResetCodeByEmail(email)

        if code != -1:
            send_email(email,"Verification code", str(code))
            return True
        
        return False    

    def verify_with_email(self, fields):
        email = fields[0]
        code = fields[1]

        is_valid_email = DataBase.IsEmailUsed(email)

        if is_valid_email:
            is_valid_code = DataBase.VerifyCodeForgot(email, code)
            return is_valid_email, is_valid_code
        else:
            return is_valid_email, True       
    
    
    @staticmethod
    def generate_keys():
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
        with open(ServerConstants.PRIVATE_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    @staticmethod
    def load_public_key():
        with open(ServerConstants.PUBLIC_PATH, "rb") as f:
            return serialization.load_pem_public_key(f.read())

    @staticmethod
    def generate_params_dh():
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
        with open(ServerConstants.DH_PATH, "rb") as f:
            return serialization.load_pem_parameters(f.read())


if __name__ == "__main__":
    Server()
