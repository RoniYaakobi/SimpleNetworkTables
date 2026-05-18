__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType, ControllerInterface
from tkinter import Frame

from protocol.protocol_constants import EncryptionType

from client.src.commands.ConnectServerCommand import ConnectCommand

class SettingsPage(Page):
    PAGE_ID = PageType.assign_id("settings")
    def __init__(self, parent: Frame, controller: ControllerInterface):
        """
        Args:
            parent (Frame): The Tk Frame which this page is connected to.
            controller (ControllerInterface): The object which controls this object.
        """
        super().__init__(parent, controller)

        self.set_title("Settings")

        self.encryption_type = self.add_radio_choice(text="RSA",
                                                  value=EncryptionType.RSA.value)
        
        self.encryption_type = self.add_radio_choice(text="Diffie Hellman",
                                                  value=EncryptionType.DH.value,
                                                  variable=self.encryption_type)

        self.create_action_button("Connect", self._connect_action, pack_pady=5)

    def _connect_action(self):
        """ Use the type of encryption that the user decided on in order to intialize the secure connection with the server. """
        encryption_type = EncryptionType(self.encryption_type.get())
        self.scheduler().schedule(ConnectCommand(self, encryption_type))
        
        
        
