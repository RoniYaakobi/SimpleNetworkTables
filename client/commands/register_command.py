__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.basic_commands import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.verify_account import VerifyPage


class RegisterCommand(Command):
    def __init__(self, controller, username, email, password, confirm, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.username = username
        self.email = email
        self.password = password
        self.confirm = confirm
        self.username_taken = False
        self.email_taken = False
        self.passwords_matching = False
        self.connected = False
        self._initialize = self.initialize
        self._is_finished = self.is_finished
        self._end = self.end

    def initialize(self):
        self.passwords_matching = self.password == self.confirm

        if not self.passwords_matching:
            self.cancel()
            return

        self.controller.backend().set_username(self.username)
        self.controller.backend().set_email(self.email)
        self.controller.backend().set_password(self.password)

        self.connected = self.controller.backend().register()
        if not self.connected:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["register"])
        if len(errors) > 0:
            for error in errors:
                self.username_taken = self.username_taken or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "username taken"
                
                self.email_taken = self.email_taken or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "email taken"
            self.cancel()
            return False
        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Register", f"Sent code to {self.email}, enter it to finish registration")
            
            self.controller.goto(VerifyPage.PAGE_ID)
        elif self.username_taken:
            messagebox.showerror("Register", f"Username {self.username} was taken")
        elif self.email_taken:
            messagebox.showerror("Register", f"Email {self.email} was taken")
        elif not self.passwords_matching:
            messagebox.showerror("Register", f"Confirmation password was different from password")
        else:
            messagebox.showerror("Register", f"Failed to connect to server!")
