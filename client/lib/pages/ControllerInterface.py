from __future__ import annotations
__author__ = "RONI YAAKOBI"

import tkinter as tk
from typing import Any,Type


from client.lib.commands.CommandScheduler import CommandScheduler

class ControllerInterface:
    """ A class that acts as an interface for all objects that can trigger a command, or can send you to a page which can """
    def __init__(self, backend: Any, scheduler: CommandScheduler, controller: None | ControllerInterface = None):
        """
        Args:
            backend (Any): the backend for the application. Use this to communicate between the frontend and the backend
            scheduler (CommandScheduler): The command scheduler that this controller is using to schedule commands.
            controller (None | ControllerInterface, optional): The controller which controlls the controller. Defaults to None.
        """
        self.m_backend = backend
        self.m_scheduler = scheduler
        self.m_links = dict()
        self.m_controller = controller
        self.m_fields = []

    def backend(self) :
        """ Get this controller's backend. """
        return self.m_backend
    
    def scheduler(self) -> CommandScheduler:
        """
        Returns:
            CommandScheduler: The command scheduler which the controller is using.
        """
        return self.m_scheduler
    
    def get_page(self, page_type):
        """Search for a Page by id or class. Checks in the current controller, and parent controllers, otherwise returns None

        Args:
            page_type (Page | int): The page id or class.

        Returns:
            Page: the page of that type.
        """
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


    def goto(self, page_type: type | int):
        """ Uses `get_page()` to get the page of a type, then displays it after reseting fields

        Args:
            page_type (Page | int): the page type you to be shown
        """
        page = self.get_page(page_type)
        if page:
            for field in self.m_fields:
                field.delete(0, tk.END)
            page.show()