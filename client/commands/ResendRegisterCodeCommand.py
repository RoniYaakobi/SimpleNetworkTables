__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.Command import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.controller_interface import ControllerInterface


class ResendRegisterCodeCommand(Command):
    """ Resend the register code to the email"""
    def __init__(self, controller: ControllerInterface):
        """
        Args:
            controller (ControllerInterface): object that triggers this command
        """
        super().__init__(controller)
        self.already_valid = False
        self.wrong_username = False

    def initialize(self):
        self.connection_alive = self.controller.backend().reset_code()
        if not self.connection_alive:
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
