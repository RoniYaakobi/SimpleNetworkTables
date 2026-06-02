__author__ = "RONI YAAKOBI"
from protocol.protocol_constants import ProtocolCode
from protocol.tcp_server import ClientSocketWrapper
from typing import Callable
import logging

class Request:
    """A client request abstracted into a class
    """
    def __init__(self, callback: Callable, code: str | ProtocolCode, errors: list[str]):
        """
        Args:
            callback (Callable): the callback for the behavior of the request
            code (str | ProtocolCode): the code of the request
            errors (list[str]): the possible error messages of the Request
        """
        self.callback = callback

        if type(code) is ProtocolCode:
            self.code = code.value
        elif type(code) is str:
            self.code = code
        else:
            print("bruh")
            raise Exception("bruh")
        
        self.errors = errors


    def respond(self, client: ClientSocketWrapper, *args):
        """Respond to a client's request

        Args:
            client (ClientSocketWrapper): the socket wrapper

        Raises:
            Exception: if the callback returns a number of flags not matching the errors list
        """
        errors_returned = self.callback(args, client)

        if type(errors_returned) is bool:
            errors_returned = (errors_returned,)
        
        if errors_returned is None:
            errors_returned = []

        if len(errors_returned) != len(self.errors):
            logging.error(f"{'More' if len(errors_returned) > len(self.errors) else 'Less'} flags returned by function than got errors.")
            raise Exception(f"{'More' if len(errors_returned) > len(self.errors) else 'Less'} flags returned by function than got errors.")

        for error_message, has_error in zip(self.errors, errors_returned):
            if has_error:
                client.send_with_size(
                    client.build_response(
                        ProtocolCode.ERROR,
                        self.code,
                        str(error_message.value)
                    )
                )
                break
        else:
            client.send_with_size(
                client.build_response(self.code)
            )