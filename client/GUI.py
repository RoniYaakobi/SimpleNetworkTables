__author__ = "RONI YAAKOBI"
import tkinter as tk
from tkinter import messagebox


from client.backend import AppBackend
from client.pages.forgot_password import ForgotPage
from client.pages.login import LoginPage
from client.pages.signup import SignUpPage
from client.pages.verify_account import VerifyPage
from client.pages.verify_forgot import ForgotCodePage
from client.pages.reset_password import ResetPasswordPage
from client.pages.settings import SettingsPage
from client.commands.basic_commands import CommandScheduler, Command
from client.GUI_constants import GUIConstants

from client.pages.controller_interface import ControllerInterface


class App(tk.Tk, ControllerInterface):
    def __init__(self):
        tk.Tk.__init__(self)
        ControllerInterface.__init__(self, AppBackend(), CommandScheduler(self, GUIConstants.SCHEDULER_MS))

        self.current_page = None

        self.title("Messenger")
        self.geometry("400x300")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for PageClass in (LoginPage, SignUpPage, ForgotPage, VerifyPage,
                           ForgotCodePage, ResetPasswordPage, SettingsPage):
            page = PageClass(container, self)
            self.m_links[PageClass.PAGE_ID] = page

            page.grid(row=0, column=0, sticky="nsew")

        for page in self.m_links.values():
            for page_id in page.get_links().keys():

                page.set_link(page_id, self.m_links.get(page_id,page))


        self.scheduler().register_command(Command(self, execute=self.backend().update))

        self.goto(SettingsPage)

        self.scheduler().periodic()

if __name__ == "__main__":
    app = App()
    app.mainloop()

