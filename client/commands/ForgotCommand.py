__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.Command import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.verify_forgot import ForgotCodePage

from client.pages.controller_interface import ControllerInterface


class ForgotPasswordCommand(Command):
    """ Command to run when the user forgot their password and want to reset it via email. """
    def __init__(self, controller : ControllerInterface, email : str):
        """
        Args:
            controller (ControllerInterface): the object which triggers the command.
            email (str): The email to which the server must send the reset code for the client password.
        """
        super().__init__(controller)

        self.email = email
        self.invalid_email = False
        self.connection_alive = False


    def initialize(self):
        
        self.controller.backend().set_email(self.email)

        self.connection_alive = self.controller.backend().forgot_password()
        if not self.connection_alive:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolConstants.CODES["forgot"])
        if len(errors) > 0:
            self.invalid_email = True
            self.cancel()
            return False
        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            messagebox.showinfo("Forgot", f"Sent code to {self.email}, enter it to reset password")

            self.controller.goto(ForgotCodePage.PAGE_ID)
        elif self.invalid_email:
            messagebox.showerror("Forgot", f"Email {self.email} is not an account!")
        else:
            messagebox.showerror("Forgot", f"Failed to connect to server!")
