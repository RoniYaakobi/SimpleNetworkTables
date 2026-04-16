__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.basic_commands import Command

from protocol.protocol_constants import ProtocolConstants


class ResendForgotCommand(Command):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.wrong_email = False
        self._initialize = self.initialize
        self._is_finished = self.is_finished
        self._end = self.end

    def initialize(self):
        self.connected = self.controller.backend().reset_code(email=True)
        if not self.connected:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["resend"])
        if len(errors) > 0:
            self.wrong_email = True
            self.cancel()
            return False
        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Resend Forgot", f"Resending code for {self.controller.backend().get_email()}!")
        elif self.wrong_email:
            messagebox.showerror("Resend Forgot", f"Email doesn't exist")
        else:
            messagebox.showerror("Resend Forgot", f"Failed to connect to server!")
