__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.basic_commands import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.login import LoginPage


class ResendCommand(Command):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.already_valid = False
        self.wrong_username = False
        self._initialize = self.initialize
        self._is_finished = self.is_finished
        self._end = self.end

    def initialize(self):
        self.connected = self.controller.backend().reset_code()
        if not self.connected:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["resend"])
        if len(errors) > 0:
            for error in errors:
                self.already_valid = self.already_valid or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "user already valid"

                self.wrong_username = self.wrong_username or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "username or password"
            self.cancel()
            return False
        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Resend", f"Resending code for {self.controller.backend().get_username()}!")
        elif self.already_valid:
            messagebox.showerror("Resend", f"User already valid!")
        elif self.wrong_username:
            messagebox.showerror("Resend", f"Wrong account!")
        else:
            messagebox.showerror("Resend", f"Failed to connect to server!")
