__author__ = "RONI YAAKOBI"
from client.lib.pages.page import Page, PageType

from client.src.commands.LoginCommand import LoginCommand


class LoginPage(Page):
    PAGE_ID = PageType.assign_id("login")
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.set_title("Login")

        self.login_username = self.create_field("Username:")
        self.login_username.pack()
        
        self.login_password = self.create_field("Password:", hidden=True)
        self.login_password.pack()

        self.create_action_button("Login", self.login_action, pack_pady=5)

        self.add_link(page_type=PageType.identify("signup"), text="Sign Up")
        self.add_link(page_type=PageType.identify("forgot"), text="Forgot Password?",pack_pady=5)

    def login_action(self):
        username = self.login_username.get()
        password = self.login_password.get()

        self.scheduler().schedule(LoginCommand(self, username, password))
        
        
