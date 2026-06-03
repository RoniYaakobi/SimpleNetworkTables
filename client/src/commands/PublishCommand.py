__author__ = "RONI YAAKOBI"
from tkinter import messagebox

from client.lib.commands.Command import Command

from protocol.protocol_constants import ProtocolCode

from client.lib.pages.ControllerInterface import ControllerInterface

from protocol.Entry import EntryType


class PublishCommand(Command):
    """ Publish to a topic """
    def __init__(self, controller: ControllerInterface, topic: str, entry_type: EntryType, value_bytes: bytes):
        """
        Args:
            controller (ControllerInterface): Object which triggers this command.
            topic (str): the topic string
        """
        super().__init__(controller)
        self.topic = topic
        self.entry_type = entry_type
        self.value_bytes = value_bytes
        self.connection_alive = False
        self.has_errors = False

    def initialize(self):
        self.connection_alive = self.controller.backend().publish(self.topic, self.entry_type, self.value_bytes)

        if not self.connection_alive:
            self.cancel()
            return

    def is_finished(self):
        messages, errors = self.controller.backend().get_messages_of_type(ProtocolCode.PUBLISH)

        if len(errors) > 0:
            self.has_errors = True
            self.cancel()
            return False

        return len(messages) > 0


    def end(self, interrupted):
        if not interrupted:
            return
        elif self.has_errors:
            messagebox.showerror("Publish", f"The server disagreed!")
        else:
            messagebox.showerror("Publish", f"Failed to connect to server!")
