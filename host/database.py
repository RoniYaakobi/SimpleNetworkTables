__author__ = "RONI YAAKOBI"
import pickle
import os
import hmac
import datetime
import random as rnd
from dataclasses import dataclass

from host.server_constants import ServerConstants



@dataclass
class User:
    username: str
    hashed_password: str
    email: str
    salt: bytes
    code: int
    expiration_date: datetime.datetime
    is_verified: bool

class DataBase:
    USER_DATA = {}

    def write_op(func):

        def wrapper(*args, **kwargs):
            val = func(*args,**kwargs)
            DataBase.save()
            return val
        
        return wrapper
    
    @staticmethod
    def hash_password(password, salt=None):
        if not salt: 
            salt = os.urandom(16)

        combined = password.encode("utf-8") + salt + ServerConstants.PEPPER.encode()

        hash_hex = hmac.new(ServerConstants.PEPPER.encode(), combined, "md5").hexdigest()

        return salt, hash_hex

    @staticmethod
    def load():
        try:
            with open(ServerConstants.DB,"rb") as data:
                DataBase.USER_DATA = pickle.load(data)
        except Exception as e:
            print("Failed to load USER_DATA")

    @staticmethod
    def save():
        with open(ServerConstants.DB,"wb") as data:
            pickle.dump(DataBase.USER_DATA, data)

    @staticmethod
    def IsPasswordOK(username, password):
        salt = DataBase.USER_DATA[username].salt

        hashed_password = DataBase.USER_DATA[username].hashed_password

        return hashed_password == DataBase.hash_password(password,salt)[1]
    
    @staticmethod
    def IsUserExist(username):
        return username in DataBase.USER_DATA.keys()

    @staticmethod
    def GetByEmail(email):
        for user in DataBase.USER_DATA.values():
            if user.email == email:
                return user
        return None

    @staticmethod
    def GetUserEmail(username):
        if user := DataBase.USER_DATA.get(username, None):
            return user.email
        
        return "-1"
    
    @staticmethod
    def IsEmailUsed(email):
        user = DataBase.GetByEmail(email)
        return not user is None
    
    @staticmethod
    @write_op
    def VerifyCodeForgot(email, code, reset=False):
        user = DataBase.GetByEmail(email)
        if user:
            if DataBase.IsValidCode(user, code):
                if reset:
                    user.expiration_date = datetime.datetime.now() - datetime.timedelta(seconds = 1)
                else:
                     user.expiration_date += datetime.timedelta(days=5) 
                return True
        return False
    
    @staticmethod
    @write_op
    def ValidateAccount(username, code):
        user = DataBase.USER_DATA.get(username, None)
        if DataBase.IsValidCode(user, code):
            user.is_verified = True

        return user.is_verified
    
    @staticmethod
    
    def IsValidCode(user, code):
        return user and user.code == int(code) and user.expiration_date > datetime.datetime.now()
    
    
    @staticmethod
    def IsVerified(username):
        user = DataBase.USER_DATA.get(username, None)
        return user and user.is_verified


    @staticmethod
    @write_op
    def SaveUser(username, email, password):
        salt, hashed_password = DataBase.hash_password(password)
        code = rnd.randint(1,1000)
        DataBase.USER_DATA[username] = User(username, hashed_password, email, salt,
                                            code , datetime.datetime.now() + datetime.timedelta(minutes=5), False)
        return str(code)
    
    @staticmethod
    @write_op
    def ResetCode(username):
        user = DataBase.USER_DATA.get(username, None)
        if user:
            code = rnd.randint(1,1000)
            user.code = code
            user.expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=5)
            return code
        
        return -1
    
    @staticmethod
    @write_op
    def ResetPassword(email, password):
        user = DataBase.GetByEmail(email)
        if not user:
            return False
        
        salt, hashed_password = DataBase.hash_password(password)
        user.salt = salt
        user.hashed_password = hashed_password

        return True
    
    @staticmethod
    @write_op
    def ResetCodeByEmail(email):
        user = DataBase.GetByEmail(email)
        if user:
            code = rnd.randint(1,1000)
            user.code = code
            user.expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=5)
            return code
        
        return -1

