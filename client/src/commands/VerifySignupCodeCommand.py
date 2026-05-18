__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.lib.commands.Command import Command

from protocol.protocol_constants import ProtocolCode, ProtocolError

from client.src.pages.LoginPage import LoginPage
from client.lib.pages.ControllerInterface import ControllerInterface


class VerifySignupCodeCommand(Command):
    """Verify the code for signup
    """
    def __init__(self, controller: ControllerInterface, verification_code: str):
        """
        Args:
            controller (ControllerInterface): The object which triggers this command
            verification_code (str): The verification code that the user entered.
        """
        super().__init__(controller)
        self.code = verification_code
        self.invalid_code = False
        self.wrong_username = False

    def initialize(self):
        self.controller.backend().set_code(self.code)

        self.connection_alive = self.controller.backend().verify_account()
        if not self.connection_alive:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolCode.VERIFY_REGISTER)
        if len(errors) > 0:
            for error in errors:
                self.invalid_code = self.invalid_code or\
                    ProtocolError(error.fields[0]) == ProtocolError.WRONG_CODE

                self.wrong_username = self.wrong_username or\
                    ProtocolError(error.fields[0]) == ProtocolError.INVALID_AUTH
            self.cancel()
            return False
        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Verify", f"Verified {self.controller.backend().get_username()}!")
            self.controller.goto(LoginPage.PAGE_ID)
        elif self.invalid_code:
            messagebox.showerror("Verify", f"Invalid code!")
        elif self.wrong_username:
            messagebox.showerror("Verify", f"Wrong account!")
        else:
            messagebox.showerror("Verify", f"Failed to connect to server!")
