__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType, ControllerInterface
from tkinter import Frame

from client.src.commands.VerifyForgotCodeCommand import VerifyForgotCodeCommand
from client.src.commands.ResendForgotCodeCommand import ResendForgotCodeCommand


class ForgotCodeVerificationPage(Page):
    PAGE_ID = PageType.assign_id("verify forgot")
    def __init__(self, parent: Frame, controller: ControllerInterface):
        """
        Args:
            parent (Frame): The Tk Frame which this page is connected to.
            controller (ControllerInterface): The object which controls this object.
        """
        super().__init__(parent, controller)

        self.set_title(text="verify forgot")

        self.verification_code = self.create_field(text="Code")
        self.verification_code.pack()


        self.create_action_button("Verify", self._verification_action, pack_pady=5)
        self.create_action_button("Resend", self._resend_code_action, pack_pady=5)
        self.add_link(page_type=PageType.identify("forgot"), text="Back To Forgot Password")

    def _verification_action(self):
        """ Use the inputted code to try to verify the forgot request. """
        code = self.verification_code.get()

        self.scheduler().schedule(VerifyForgotCodeCommand(self, code))

    def _resend_code_action(self):
        """ Request the server resends the code. """

        self.scheduler().schedule(ResendForgotCodeCommand(self))
