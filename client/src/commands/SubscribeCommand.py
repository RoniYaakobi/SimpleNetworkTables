__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.lib.commands.Command import Command

from protocol.protocol_constants import ProtocolCode

from client.lib.pages.ControllerInterface import ControllerInterface



class SubscribeCommand(Command):
    """ Run to subscribe to a topic """
    def __init__(self, controller: ControllerInterface, topic: str):
        """
        Args:
            controller (ControllerInterface): Object which triggers this command.
            topic (str): the topic string
        """
        super().__init__(controller)
        self.topic = topic
        self.connection_alive = False
        self.has_errors = False

    def initialize(self):
        self.connection_alive = self.controller.backend().subscribe(self.topic)

        if not self.connection_alive:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolCode.SUBSCRIBE)

        if len(errors) > 0:
            self.has_errors = True
            self.cancel()
            return False

        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            return
        elif self.has_errors:
            messagebox.showerror("Subscribe", f"The server disagreed!")
        else:
            messagebox.showerror("Subscribe", f"Failed to connect to server!")
