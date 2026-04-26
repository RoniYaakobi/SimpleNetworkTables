__author__ = "RONI YAAKOBI"
from client.lib.pages.page import Page, PageType

from protocol.protocol_constants import ProtocolConstants

from client.src.commands.ConnectServerCommand import ConnectCommand

class SettingsPage(Page):
    PAGE_ID = PageType.assign_id("settings")
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.set_title("Settings")

        self.encryption_type = self.add_radio_choice(text="RSA",
                                                  value=ProtocolConstants.EncryptionType.RSA.value)
        
        self.encryption_type = self.add_radio_choice(text="Diffie Hellman",
                                                  value=ProtocolConstants.EncryptionType.DH.value,
                                                  variable=self.encryption_type)

        self.create_action_button("Connect", self.connect_action, pack_pady=5)

    def connect_action(self):
        encryption_type = ProtocolConstants.EncryptionType(self.encryption_type.get())
        self.scheduler().schedule(ConnectCommand(self, encryption_type))
        
        
        
