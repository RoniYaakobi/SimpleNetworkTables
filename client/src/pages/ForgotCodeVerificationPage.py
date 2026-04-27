__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType

from client.src.commands.VerifyForgotCodeCommand import VerifyForgotCodeCommand
from client.src.commands.ResendForgotCodeCommand import ResendForgotCodeCommand


class ForgotCodeVerificationPage(Page):
    PAGE_ID = PageType.assign_id("verify forgot")
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.set_title(text="verify forgot")

        self.verification_code = self.create_field(text="Code")
        self.verification_code.pack()


        self.create_action_button("Verify", self.verification_action, pack_pady=5)
        self.create_action_button("Resend", self.resend_code_action, pack_pady=5)
        self.add_link(page_type=PageType.identify("forgot"), text="Back To Forgot Password")

    def verification_action(self):
        code = self.verification_code.get()

        self.scheduler().schedule(VerifyForgotCodeCommand(self, code))

    def resend_code_action(self):

        self.scheduler().schedule(ResendForgotCodeCommand(self))
