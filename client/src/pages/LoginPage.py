__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType, ControllerInterface
from tkinter import Frame

from client.src.commands.LoginCommand import LoginCommand


class LoginPage(Page):
    PAGE_ID = PageType.assign_id("login")
    def __init__(self, parent: Frame, controller: ControllerInterface):
        """
        Args:
            parent (Frame): The Tk Frame which this page is connected to.
            controller (ControllerInterface): The object which controls this object.
        """
        super().__init__(parent, controller)

        self.set_title("Login")

        self.login_username = self.create_field("Username:")
        self.login_username.pack()
        
        self.login_password = self.create_field("Password:", hidden=True)
        self.login_password.pack()

        self.create_action_button("Login", self._login_action, pack_pady=5)

        self.add_link(page_type=PageType.identify("signup"), text="Sign Up")
        self.add_link(page_type=PageType.identify("forgot"), text="Forgot Password?",pack_pady=5)

    def _login_action(self):
        """ Use the input username and password to attempt to login. """
        username = self.login_username.get()
        password = self.login_password.get()

        self.scheduler().schedule(LoginCommand(self, username, password))
        
        
