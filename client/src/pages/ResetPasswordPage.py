__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType, ControllerInterface
from tkinter import Frame


from client.src.commands.ResetPasswordCommand import ResetPasswordCommand


class ResetPasswordPage(Page):
    PAGE_ID = PageType.assign_id("Reset")
    def __init__(self, parent: Frame, controller: ControllerInterface):
        """
        Args:
            parent (Frame): The Tk Frame which this page is connected to.
            controller (ControllerInterface): The object which controls this object.
        """
        super().__init__(parent, controller)

        self.set_title("Reset Password")

        self.email = self.create_field("Email:")
        self.email.pack()

        self.new_password = self.create_field("New password:")
        self.new_password.pack()

        self.confirm_new_password = self.create_field("Confirm new password:")
        self.confirm_new_password.pack()
        

        self.create_action_button("Reset password", self._reset_password_action, pack_pady=5)
        
        self.add_link(page_type=PageType.identify("login"), text="Back to Login")


    def _reset_password_action(self):
        """ Use the input email, password, and confirmation password to reset the password. This comes after verification. """
        email = self.email.get()
        password = self.new_password.get()
        confirm = self.confirm_new_password.get()

        self.scheduler().schedule(ResetPasswordCommand(self, email, password, confirm))

            



    
