__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.lib.commands.Command import Command

from protocol.protocol_constants import ProtocolConstants

from client.src.pages.login import LoginPage
from client.lib.pages.controller_interface import ControllerInterface


class ResetPasswordCommand(Command):
    """ Reset the password """
    def __init__(self, controller: ControllerInterface, email: str, password: str, confirmation_password: str):
        """
        Args:
            controller (ControllerInterface): object that triggers this command.
            email (str): the email of the account to reset the password for
            password (str): the new password stored as a string.
            confirmation_password (str): verification for the new password, must be the same as password.
        """
        super().__init__(controller)
        self.email = email
        self.password = password
        self.confirmation_password = confirmation_password
        self.connection_alive = False
        self.not_same_password = False
        self.bad_code = False
        self.bad_email = False

    def initialize(self):
        self.not_same_password = self.password != self.confirmation_password

        if (self.not_same_password):
            self.cancel()
            return

        self.controller.backend().set_password(self.password)
        self.controller.backend().set_email(self.email)
        self.connection_alive = self.controller.backend().reset_password()

        if not self.connection_alive:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["reset"])

        if len(errors) > 0:
            for error in errors:
                self.bad_code = self.bad_code or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "wrong code"
                
                self.bad_email = self.bad_email or\
                    ProtocolConstants.ERRORS[int(error.fields[0])] == "wrong email"
            self.cancel()
            return False

        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Reset", f"Reset password for email: {self.controller.backend().get_email()}")

            self.controller.goto(LoginPage.PAGE_ID)
        elif self.bad_code:
            messagebox.showerror("Reset", f"Incorrect code!")

        elif self.bad_email:
            messagebox.showerror("Reset", f"Incorrect email!")
        
        elif self.not_same_password:
            messagebox.showerror("Reset", f"Confirmation password and password not matching!")

        else:
            messagebox.showerror("Reset", f"Failed to connect to server!")
