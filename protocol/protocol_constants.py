__author__ = "RONI YAAKOBI"


from enum import Enum, unique

# Acknowledgement signal used across packet parsing
ACK = "ACK"


@unique
class ProtocolCode(Enum):
    """Operation codes for server-client communication messages."""
    
    # --- Authentication & Account Management ---
    LOGIN = "LGN"
    REGISTER = "RGS"           # Phase 1: User sends info, receives verification code
    VERIFY_REGISTER = "VRF"    # Phase 2: Verifies registration code
    RESEND_CODE = "RSD"        # Resends code using username
    CONFIRM_REGISTER = "CRG"   # Legacy/Unused registration confirmation
    
    # --- Password Recovery ---
    FORGOT_PASSWORD = "FRG"    # Initial forgot password request
    VERIFY_FORGOT = "VFR"      # Verifies email ownership during recovery
    RESET_PASSWORD = "RST"     # Finalizes new password
    RESEND_FORGOT_MAIL = "RSE" # Resends recovery mail using email as identifier
    
    # --- Network Tables (Pub/Sub Engine) ---
    SNAPSHOT = "SNP"           # Full state snapshot of the network tables
    SUBSCRIBE = "SUB"          # Subscribe to a specific key
    PUBLISH = "PUB"            # Publish a value to a topic
    UPDATE = "UPD"             # Broadcast updates to subscribers
    
    # --- System ---
    ERROR = "ERR"              # General error indicator


@unique
class ProtocolError(Enum):
    """Defined protocol error messages.
    
    Values can map to network payload strings or internal indices.
    """
    INVALID_AUTH = 0
    WRONG_EMAIL = 1
    USERNAME_TAKEN = 2
    EMAIL_TAKEN = 3
    WRONG_CODE = 4
    CODE_EXPIRED = 5
    USER_ALREADY_VALID = 6
    INVALID_TYPE = 7
    BAD_DATA = 8
    ALREADY_SUBSCRIBED = 9


@unique
class EncryptionType(Enum):
    """Supported asymmetric cryptographic algorithms."""
    RSA = 1
    DH = 2