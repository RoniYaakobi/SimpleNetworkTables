__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.commands.basic_commands import Command

from protocol.protocol_constants import ProtocolConstants

from client.pages.login import LoginPage

import threading


class ConnectCommand(Command):
    def __init__(self, controller, encryption_type, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.encryption_type = encryption_type
        self.already_connecting = False
        self.connect_thread = None
        self._initialize = self.initialize
        self._is_finished = self.is_finished
        self._end = self.end

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
