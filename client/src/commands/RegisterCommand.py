__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.lib.commands.Command import Command

from protocol.protocol_constants import ProtocolConstants

from client.src.pages.VerifyAccountPage import VerifyAccountPage
from client.lib.pages.ControllerInterface import ControllerInterface


class RegisterCommand(Command):
    """
    Start the first stage of Registering the new user, sending the username, password, and the email for the two factor auth.
    Also a confirmation password in order to make sure that the user confirmed the password
    """
    def __init__(self, controller: ControllerInterface, username: str, email: str, password: str, confirmation_password: str):
        """
        Args:
            controller (ControllerInterface): object that triggered this command.
            username (str): the username string.
            email (str): the user's email in a string.
            passowrd (str): the username's password in a string
            confirmation_password (str): Confirmation for the password.
                User must input the exact same string in password and here in order to be considered confirmed
        """
        super().__init__(controller)
        self.username = username
        self.email = email
        self.password = password
        self.confirmation_password = confirmation_password
        self.username_taken = False
        self.email_taken = False
        self.passwords_matching = False
        self.connection_alive = False

    def initialize(self):
        self.passwords_matching = self.password == self.confirmation_password

        if not self.passwords_matching:
            self.cancel()
            return

        self.controller.backend().set_username(self.username)
        self.controller.backend().set_email(self.email)
        self.controller.backend().set_password(self.password)

        self.connection_alive = self.controller.backend().register()
        if not self.connection_alive:
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
            
            self.controller.goto(VerifyAccountPage.PAGE_ID)
        elif self.username_taken:
            messagebox.showerror("Register", f"Username {self.username} was taken")
        elif self.email_taken:
            messagebox.showerror("Register", f"Email {self.email} was taken")
        elif not self.passwords_matching:
            messagebox.showerror("Register", f"Confirmation password was different from password")
        else:
            messagebox.showerror("Register", f"Failed to connect to server!")
