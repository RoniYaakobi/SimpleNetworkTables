__author__ = "RONI YAAKOBI"
import os


class ServerConstants:
    DB = r"host\db.pkl"
    ENCRYPT_PATH = r"host"
    PRIVATE_PATH = os.path.join(ENCRYPT_PATH, "RSA_private.pem")
    PUBLIC_PATH = os.path.join(ENCRYPT_PATH, "RSA_public.pem")
    DH_PATH = os.path.join(ENCRYPT_PATH, "DH.pem")


    DB = r"host/db.pkl"
    PRIVATE_PATH = "host/RSA_private.pem"
    PUBLIC_PATH = "host/RSA_public.pem"
    DH_PATH = "host/DH.pem"

    IP = "0.0.0.0"
    PORT = 67
    ADDR = (IP,PORT)

    PEPPER = "PELEG"