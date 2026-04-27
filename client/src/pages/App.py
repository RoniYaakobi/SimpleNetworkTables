__author__ = "RONI YAAKOBI"
import tkinter as tk


from client.src.backend import AppBackend
from client.lib.commands import CommandScheduler
from client.src.pages.GUI_constants import GUIConstants

from client.lib.pages.ControllerInterface import ControllerInterface



class App(tk.Tk, ControllerInterface):
    def __init__(self, ALL_PAGES):
        tk.Tk.__init__(self)
        ControllerInterface.__init__(self, AppBackend(), CommandScheduler(self, GUIConstants.SCHEDULER_MS))

        self.current_page = None

        self.title("Messenger")
        self.geometry("400x300")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for PageClass in ALL_PAGES:
            page = PageClass(container, self)
            self.m_links[PageClass.PAGE_ID] = page

            page.grid(row=0, column=0, sticky="nsew")

        for page in self.m_links.values():
            for page_id in page.get_links().keys():

                page.set_link(page_id, self.m_links.get(page_id,page))

        self.goto(ALL_PAGES[0])


