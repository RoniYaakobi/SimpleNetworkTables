__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.lib.commands.Command import Command

from protocol.protocol_constants import ProtocolConstants

from client.lib.pages.ControllerInterface import ControllerInterface

class ResendForgotCodeCommand(Command):
    """ Resend the code for the forgot password. """
    def __init__(self, controller: ControllerInterface):
        """
        Args:
            controller (ControllerInterface): the object that triggers this command
        """
        super().__init__(controller)
        self.wrong_email = False

    def initialize(self):
        self.connection_alive = self.controller.backend().reset_code(email=True)
        if not self.connection_alive:
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
