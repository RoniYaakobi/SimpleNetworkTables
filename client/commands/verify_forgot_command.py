__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.basic_commands import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.reset_password import ResetPasswordPage


class VerifyForgotCommand(Command):
    def __init__(self, controller, code, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.code = code
        self.wrong_email = False
        self.wrong_code = False
        self._initialize = self.initialize
        self._is_finished = self.is_finished
        self._end = self.end

    def initialize(self):
        self.controller.backend().set_code(self.code)

        self.connected = self.controller.backend().verify_for_reset()
        if not self.connected:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["verforgot"])
        if len(errors) > 0:
            for error in errors:
                self.wrong_code = self.wrong_code or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "wrong code"

                self.wrong_email = self.wrong_username or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "wrong email"
            self.cancel()
            return False
        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Verify Forgot", f"Verified {self.controller.backend().get_email()}!")
            self.controller.goto(ResetPasswordPage.PAGE_ID)
        elif self.invalid_code:
            messagebox.showerror("Verify Forgot", f"Invalid code!")
        elif self.wrong_username:
            messagebox.showerror("Verify Forgot", f"Wrong account!")
        else:
            messagebox.showerror("Verify Forgot", f"Failed to connect to server!")
