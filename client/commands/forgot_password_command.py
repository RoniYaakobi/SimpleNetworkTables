__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.basic_commands import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.verify_forgot import ForgotCodePage


class ForgotPasswordCommand(Command):
    def __init__(self, controller, email, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)

        self.email = email
        self.bad_email = False
        self.connected = False
        self._initialize = self.initialize
        self._is_finished = self.is_finished
        self._end = self.end

    def initialize(self):
        
        self.controller.backend().set_email(self.email)

        self.connected = self.controller.backend().forgot_password()
        if not self.connected:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["forgot"])
        if len(errors) > 0:
            self.bad_email = True
            self.cancel()
            return False
        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Forgot", f"Sent code to {self.email}, enter it to reset password")

            self.controller.goto(ForgotCodePage.PAGE_ID)
        elif self.bad_email:
            messagebox.showerror("Forgot", f"Email {self.email} is not an account!")
        else:
            messagebox.showerror("Forgot", f"Failed to connect to server!")
