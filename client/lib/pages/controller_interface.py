__author__ = "RONI YAAKOBI"
import tkinter as tk

from client.src.backend import AppBackend
from client.lib.commands.CommandScheduler import CommandScheduler


class ControllerInterface:
    pass

class ControllerInterface:
    def __init__(self, backend, scheduler, controller: None | ControllerInterface = None):
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