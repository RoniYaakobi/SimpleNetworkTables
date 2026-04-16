__author__ = "RONI YAAKOBI"
from enum import Enum

class ProtocolConstants:
    #TODO figure out documentation
    CODES = {
        "login" : "LGN", 
        "confirm register": "CRG", 
        "register" : "RGS", 
        "forgot" : "FRG", 
        "error" :  "ERR", 
        "verify" : "VRF", 
        "resend": "RSD", 
        "reset": "RST",
        "verforgot": "VFR",
        "resendmail": "RSE"
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