__author__ = "RONI YAAKOBI"
import pickle
import os
import hmac
import datetime
import random as rnd
from dataclasses import dataclass
from typing import Callable


from host.server_constants import ServerConstants



@dataclass
class User:
    """
        Practically a username row in a database put in python code.
    """
    username: str
    hashed_password: str
    email: str
    salt: bytes
    code: int
    expiration_date: datetime.datetime
    is_verified: bool

class DataBase:
    """
        The static database class.
    """
    USER_DATA = {}

    def auto_save(func) -> Callable:
        """
        Args:
            func: the function you want to wrap with autosave 
        """

        def wrapper(*args, **kwargs):
            val = func(*args,**kwargs)
            DataBase.save()
            return val
        
        return wrapper
    
    @staticmethod
    def hash_password(password: str, salt: int = None) -> tuple[int, str]:
        """ Hashes a password

        Args:
            password (str): the password to hash
            salt (int, optional): the salt to use in the hash. Defaults to None.

        Returns:
            (salt, hash_hex): the salt that was used for the hashing, and the hashed password.
        """
        if not salt: 
            salt = os.urandom(16)

        combined = password.encode("utf-8") + salt + ServerConstants.PEPPER.encode()

        hash_hex = hmac.new(ServerConstants.PEPPER.encode(), combined, "md5").hexdigest()

        return salt, hash_hex

    @staticmethod
    def load():
        """ 
            Load the database into working memory
        """
        try:
            with open(ServerConstants.DB,"rb") as data:
                DataBase.USER_DATA = pickle.load(data)
        except Exception as e:
            print("Failed to load USER_DATA")

    @staticmethod
    def save():
        """ 
            Save the database onto the hard drive
        """
        with open(ServerConstants.DB,"wb") as data:
            pickle.dump(DataBase.USER_DATA, data)

    @staticmethod
    def IsPasswordOK(username: str, password: str) -> bool:
        """Check if the password matches the username

        Args:
            username (str): the username
            password (str): the password

        Returns:
            bool: whether or not the username matches the password.
        """
        salt = DataBase.USER_DATA[username].salt

        hashed_password = DataBase.USER_DATA[username].hashed_password

        return hashed_password == DataBase.hash_password(password,salt)[1]
    
    @staticmethod
    def IsUserExist(username: str) -> bool:
        """Does the username exist in the database

        Args:
            username (str): the username to check

        Returns:
            bool: whether or not the username exists
        """
        return username in DataBase.USER_DATA.keys()

    @staticmethod
    def __GetByEmail(email: str) -> User | None:
        """Get a user object using the email as the identifier

        Args:
            email (str): The email the user registered with

        Returns:
            User | None: a user object
        """
        for user in DataBase.USER_DATA.values():
            if user.email == email:
                return user
        return None

    @staticmethod
    def GetUserEmail(username: str) -> str | None:
        """Gets the email linked to a username

        Args:
            username (str): the username that is to be checked

        Returns:
            str | None: the user email
        """
        if user := DataBase.USER_DATA.get(username, None):
            return user.email
        
        return None
    
    @staticmethod
    def IsEmailUsed(email: str) -> bool:
        """Return whether or not the email is used

        Args:
            email (str): the email to check

        Returns:
            bool: whether or not the email is used
        """
        user = DataBase.__GetByEmail(email)
        return not user is None
    
    @staticmethod
    @auto_save
    def VerifyCodeForgot(email: str, code: int, reset: bool =False) -> bool:
        """ Verify the code sent to the user. Optionally also reset the code

        Args:
            email (str): the email that needs to be verified
            code (int): the code the user said they got
            reset (bool, optional): whether or not the code needs to be reset. Defaults to False.

        Returns:
            bool: whether or not the code is valid
        """
        user = DataBase.__GetByEmail(email)
        if user:
            if DataBase.__IsValidCode(user, code):
                if reset:
                    user.expiration_date = datetime.datetime.now() - datetime.timedelta(seconds = 1)
                else:
                     user.expiration_date += datetime.timedelta(days=5) 
                return True
        return False
    
    @staticmethod
    @auto_save
    def ValidateAccount(username: str, code: int) -> bool:
        """Attempt to validate the user and return whether or not it worked.

        Args:
            username (str): the username that needs to be validated
            code (int): the code that is supposed to be the code to validate with

        Returns:
            bool: whether or not the validation worked
        """
        user = DataBase.USER_DATA.get(username, None)
        if DataBase.__IsValidCode(user, code):
            user.is_verified = True

        return user.is_verified
    
    @staticmethod
    
    def __IsValidCode(user: User, code: int) -> bool:
        """Check if the code is valid

        Args:
            user (User): attempt to validate the user
            code (int): the user code to check

        Returns:
            bool: whether the code was valid for the user
        """
        return user and user.code == int(code) and user.expiration_date > datetime.datetime.now()
    
    
    @staticmethod
    def IsVerified(username: str) -> bool:
        """Is the username of a verified user

        Args:
            username (str): the username to check

        Returns:
            bool: whether or not the user is verified
        """
        user = DataBase.USER_DATA.get(username, None)
        return user and user.is_verified


    @staticmethod
    @auto_save
    def SaveUser(username: str, email: str, password: str) -> str:
        """Create a user record

        Args:
            username (str): the username
            email (str): the email that the user wants to use
            password (str): the password that the user wants to use

        Returns:
            str: the code as a string
        """
        salt, hashed_password = DataBase.hash_password(password)
        code = rnd.randint(1,1000)
        DataBase.USER_DATA[username] = User(username, hashed_password, email, salt,
                                            code , datetime.datetime.now() + datetime.timedelta(minutes=5), False)
        return str(code)
    
    @staticmethod
    @auto_save
    def ResetCode(username: str) -> int:
        """ Reset the code for a given username's verification

        Args:
            username (str): the username

        Returns:
            int: the new code the user got
        """
        user = DataBase.USER_DATA.get(username, None)
        if user:
            code = rnd.randint(1,1000)
            user.code = code
            user.expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=5)
            return code
        
        return -1
    
    @staticmethod
    @auto_save
    def ResetPassword(email: str, password: str) -> bool:
        """Reset the password for a given account's email

        Args:
            email (str): the email to reset the password for
            password (str): the new password 

        Returns:
            bool: whether or not the reset succeeded
        """
        user = DataBase.__GetByEmail(email)
        if not user:
            return False
        
        salt, hashed_password = DataBase.hash_password(password)
        user.salt = salt
        user.hashed_password = hashed_password

        return True
    
    @staticmethod
    @auto_save
    def ResetCodeByEmail(email: str) -> int:
        """Reset the code using the email as the identifier

        Args:
            email (str): the email that we want to use as the identifier

        Returns:
            int: the new code that has been chosen.
        """
        user = DataBase.__GetByEmail(email)
        if user:
            code = rnd.randint(1,1000)
            user.code = code
            user.expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=5)
            return code
        
        return -1

