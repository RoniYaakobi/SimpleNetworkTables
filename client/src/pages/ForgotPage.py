__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType, ControllerInterface
from tkinter import Frame


from client.src.commands.ForgotCommand import ForgotPasswordCommand


class ForgotPage(Page):
    PAGE_ID = PageType.assign_id("forgot")
    def __init__(self, parent: Frame, controller: ControllerInterface):
        """
        Args:
            parent (Frame): The Tk Frame which this page is connected to.
            controller (ControllerInterface): The object which controls this object.
        """
        super().__init__(parent, controller)

        self.set_title("Forgot Password")

        self.forgot_email = self.create_field("Email:")
        self.forgot_email.pack()
        

        self.create_action_button("Send Reset Code", self._forgot_action, pack_pady=5)
        
        self.add_link(page_type=PageType.identify("login"), text="Back to Login")


    def _forgot_action(self):
        """ Use the input email to request the server let client reset password. """
        email = self.forgot_email.get()

        self.scheduler().schedule(ForgotPasswordCommand(self,email))

            



    
