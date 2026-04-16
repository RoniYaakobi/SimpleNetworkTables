__author__ = "RONI YAAKOBI"
from client.pages.page import Page, PageType


from client.commands.reset_password_command import ResetPasswordCommand


class ResetPasswordPage(Page):
    PAGE_ID = PageType.assign_id("Reset")
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.set_title("Reset Password")

        self.new_password = self.create_field("New password:")
        self.new_password.pack()

        self.confirm_new_password = self.create_field("Confirm new password:")
        self.confirm_new_password.pack()
        

        self.create_action_button("Reset password", self.forgot_action, pack_pady=5)
        
        self.add_link(page_type=PageType.identify("login"), text="Back to Login")


    def forgot_action(self):
        password = self.new_password.get()
        confirm = self.confirm_new_password.get()

        self.scheduler().schedule(ResetPasswordCommand(self, password, confirm))

            



    
