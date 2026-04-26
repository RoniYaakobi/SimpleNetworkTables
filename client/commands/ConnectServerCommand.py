__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.Command import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.login import LoginPage
from client.pages.controller_interface import ControllerInterface

import threading


class ConnectCommand(Command):
    """ Connect to the server, starting the secure session. """
    def __init__(self, controller : ControllerInterface, encryption_type : ProtocolConstants.EncryptionType):
        """
        Args:
            controller (ControllerInterface): The controller which schedules the command.
            encryption_type (EncryptionType): The type of secure session chosen to connect to the server with.
        """
        super().__init__(controller)
        self.encryption_type = encryption_type
        self.already_connecting = False
        self.connect_thread = None


    def initialize(self):
        self.already_connecting = self.controller.backend().is_connecting()
        if (self.already_connecting):
            return
        self.controller.backend().set_encryption_type(self.encryption_type)

        self.connect_thread = threading.Thread(target=self.controller.backend().connect, daemon=True)
        self.connect_thread.start()

    def is_finished(self):
        return not self.connect_thread or not self.connect_thread.is_alive() or self.already_connecting


    def end(self, interrupted):
        if not interrupted and self.controller.backend().is_connected():
            messagebox.showinfo("Connected", f"Connected to the server successfully!")
            
            self.controller.goto(LoginPage.PAGE_ID)
        elif self.already_connecting:
            messagebox.showerror("Connected", f"Already connecting!")
        elif interrupted:
            messagebox.showerror("Connected", f"Connection Interrupted!")
        else:
            messagebox.showerror("Connected", f"Failed to connect to server!")