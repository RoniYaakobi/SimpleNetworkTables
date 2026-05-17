__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType, ControllerInterface
from tkinter import Frame
from tkinter import messagebox

from client.src.commands.VerifySignupCodeCommand import VerifySignupCodeCommand
from client.src.commands.ResendRegisterCodeCommand import ResendRegisterCodeCommand


class VerifyAccountPage(Page):
    PAGE_ID = PageType.assign_id("verify")
    def __init__(self, parent: Frame, controller: ControllerInterface):
        """
        Args:
            parent (Frame): The Tk Frame which this page is connected to.
            controller (ControllerInterface): The object which controls this object.
        """
        super().__init__(parent, controller)

        self.set_title(text="verify")

        self.verification_code = self.create_field(text="Code")
        self.verification_code.pack()


        self.create_action_button("Verify", self._verification_action, pack_pady=5)
        self.create_action_button("Resend", self._resend_code_action, pack_pady=5)
        self.add_link(page_type=PageType.identify("signup"), text="Back To Register")

    def _verification_action(self):
        """ Use the input code to try to verify the account creation. """
        code = self.verification_code.get()

        self.scheduler().schedule(VerifySignupCodeCommand(self, code))

    def _resend_code_action(self):
        """ Tell the server to resend the register code. """
        self.scheduler().schedule(ResendRegisterCodeCommand(self))
