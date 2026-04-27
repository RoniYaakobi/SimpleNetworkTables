__author__ = "RONI YAAKOBI"
import tkinter as tk
from typing import Any

from client.src.Backend import AppBackend
from client.lib.commands.CommandScheduler import CommandScheduler


class ControllerInterface:
    """ A class that acts as an interface for all objects that can trigger a command, or can send you to a page which can """
    def __init__(self, backend: Any, scheduler: CommandScheduler, controller: None | "ControllerInterface" = None):
        """
        Args:
            backend (Any): the backend for the application. Use this to communicate between the frontend and the backend
            scheduler (CommandScheduler): The command scheduler that this controller is using to schedule commands.
            controller (None | ControllerInterface, optional): _description_. Defaults to None.
        """
        self.m_backend = backend
        self.m_scheduler = scheduler
        self.m_links = dict()
        self.m_controller = controller
        self.m_fields = []

    def backend(self) -> AppBackend:
        return self.m_backend
    
    def scheduler(self) -> CommandScheduler:
        return self.m_scheduler
    
    def get_page(self, page_type):
        if not isinstance(page_type, int):
            page_type = page_type.PAGE_ID

        page = self.m_links.get(page_type)
        if page:
            return page
        elif self.m_controller:
            return self.m_controller.get_page(page_type)
        else:
            print(f"Couldn't find page {page_type}")
            return None


    def goto(self, page_type):
        page = self.get_page(page_type)
        if page:
            for field in self.m_fields:
                field.delete(0, tk.END)
            page.show()