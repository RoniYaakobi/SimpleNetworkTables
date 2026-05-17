__author__ = "RONI YAAKOBI"
from enum import Enum

class ProtocolConstants:
    #TODO figure out documentation
    CODES = {
        "login" : "LGN", # Login
        "confirm register": "CRG", # Confirm registration (can't find where this is in the code) 
        "register" : "RGS", # first phase of registering. user sends the email and password and username and gets a verification code
        "forgot" : "FRG", # username forgot their password
        "error" :  "ERR", # general error
        "verify" : "VRF", # verify the code sent to the user for register
        "resend": "RSD", # resend the verification code 
        "reset": "RST", # reset the password
        "verforgot": "VFR", # verify ownership of the email in forgot password
        "resendmail": "RSE" # resend the the email but using the email as the identifier instead of the username (idk smh)
    }

    ERRORS = [
        "username or password",
        "wrong email",
        "username taken",
        "email taken",
        "wrong code",
        "code expired",
        "user already valid"
    ]

    ACK = "ACK"

    class EncryptionType(Enum):
        RSA = 1
        DH = 2