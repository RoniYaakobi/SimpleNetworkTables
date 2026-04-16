__author__ = "RONI YAAKOBI"
from client.pages.page import Page, PageType


from client.commands.forgot_password_command import ForgotPasswordCommand


class ForgotPage(Page):
    PAGE_ID = PageType.assign_id("forgot")
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.set_title("Forgot Password")

        self.forgot_email = self.create_field("Email:")
        self.forgot_email.pack()
        

        self.create_action_button("Send Reset Code", self.forgot_action, pack_pady=5)
        
        self.add_link(page_type=PageType.identify("login"), text="Back to Login")


    def forgot_action(self):
        email = self.forgot_email.get()

        self.scheduler().schedule(ForgotPasswordCommand(self,email))

            



    
