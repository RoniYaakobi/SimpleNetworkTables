__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType, ControllerInterface
from tkinter import Frame
from tkinter import messagebox

from client.src.commands.RegisterCommand import RegisterCommand


class SignUpPage(Page):
    PAGE_ID = PageType.assign_id("signup")
    def __init__(self, parent: Frame, controller: ControllerInterface):
        """
        Args:
            parent (Frame): The Tk Frame which this page is connected to.
            controller (ControllerInterface): The object which controls this object.
        """
        super().__init__(parent, controller)

        self.set_title(text="Sign Up")

        self.signup_username = self.create_field(text="Username:")
        self.signup_username.pack()

        self.signup_email = self.create_field(text="Email:")
        self.signup_email.pack()

        self.signup_password = self.create_field(text="Password:", hidden= True)
        self.signup_password.pack()

        self.confirm_password = self.create_field(text="Confirm Password:", hidden= True)
        self.confirm_password.pack(pady=(0,10))

        self.create_action_button("Sign Up", self._signup_action, pack_pady=5)
        self.add_link(page_type=PageType.identify("login"), text="Back To Login")

    def _signup_action(self):
        """ Use input username, email, password, and confirmation passwords to attempt to register. """
        username = self.signup_username.get()
        email = self.signup_email.get()

        password = self.signup_password.get()
        confirm = self.confirm_password.get()

        self.scheduler().schedule(RegisterCommand(self, username, email, password, confirm))
