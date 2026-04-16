__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.basic_commands import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.login import LoginPage


class VerifyCommand(Command):
    def __init__(self, controller, code, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.code = code
        self.invalid_code = False
        self.wrong_username = False
        self._initialize = self.initialize
        self._is_finished = self.is_finished
        self._end = self.end

    def initialize(self):
        self.controller.backend().set_code(self.code)

        self.connected = self.controller.backend().verify_account()
        if not self.connected:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["verify"])
        if len(errors) > 0:
            for error in errors:
                self.invalid_code = self.invalid_code or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "wrong code"

                self.wrong_username = self.wrong_username or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "username or password"
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
