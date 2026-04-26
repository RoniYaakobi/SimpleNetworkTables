__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.Command import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.controller_interface import ControllerInterface



class LoginCommand(Command):
    """ Run to login to the server when the user supplies a username and a password. """
    def __init__(self, controller: ControllerInterface, username: str, password: str):
        """
        Args:
            controller (ControllerInterface): Object which triggers this command.
            username (str): the username string
            password (str): the password string
            
        """
        super().__init__(controller)
        self.username = username
        self.password = password
        self.connection_alive = False
        self.has_errors = False

    def initialize(self):
        self.controller.backend().set_username(self.username)
        self.controller.backend().set_password(self.password)
        self.connection_alive = self.controller.backend().login()

        if not self.connection_alive:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["login"])

        if len(errors) > 0:
            self.has_errors = True
            self.cancel()
            return False

        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Login", f"Connected to username: {self.username}")
            
            self.controller.goto(0)
        elif self.has_errors:
            messagebox.showerror("Login", f"Incorrect username or password!")
        else:
            messagebox.showerror("Login", f"Failed to connect to server!")
