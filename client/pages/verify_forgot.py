__author__ = "RONI YAAKOBI"
from client.pages.page import Page, PageType

from client.commands.verify_forgot_command import VerifyForgotCommand
from client.commands.resend_command_forgot import ResendForgotCommand


class ForgotCodePage(Page):
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

        self.scheduler().schedule(VerifyForgotCommand(self, code))

    def resend_code_action(self):

        self.scheduler().schedule(ResendForgotCommand(self))
