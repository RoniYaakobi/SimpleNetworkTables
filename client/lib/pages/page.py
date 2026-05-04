from __future__ import annotations
__author__ = "RONI YAAKOBI"
import tkinter as tk
from tkinter import messagebox
from client.lib.commands.Command import Command

from .ControllerInterface import ControllerInterface

from typing import Callable, Any

class PageType:
    """Stores the page names to id maps
    """
    ids_to_names = dict()
    names_to_ids = dict()
    page_types = 0

    @staticmethod
    def assign_id(name : str):
        """Assign a page an id by registering it to the PageType maps

        Args:
            name (str): a string identifier for the page

        Returns:
            int: amount of pages registered including this one, which is the id.
        """
        PageType.page_types += 1
        PageType.ids_to_names = {PageType.page_types: name, **PageType.ids_to_names}
        PageType.names_to_ids = {name: PageType.page_types, **PageType.names_to_ids}
        return PageType.page_types

    @staticmethod
    def identify(name: str):
        """
        Args:
            name (str): the string identifier used to register the page with `assign_id()`

        Returns:
            int: Page id of the respective page.
        """
        return PageType.names_to_ids.get(name)


class Page(tk.Frame, ControllerInterface):
    """ A generic page with utilities """

    PAGE_ID = PageType.assign_id("plain")

    def __init__(self, parent, controller):
        """ A weird way to do inheritance in python because python is weird. """
        tk.Frame.__init__(self, parent)
        ControllerInterface.__init__(self, controller.backend(), controller.scheduler(), controller= controller)

    def show(self):
        """ Show this page """
        self.tkraise()
        self.m_controller.current_page = __class__.PAGE_ID

    def set_title(self, text="Title", font=("Arial", 20)):
        """ Set the title of the form.

        Args:
            text (str, optional): Defaults to "Title".
            font (tuple, optional): (Font style, Font size). Defaults to ("Arial", 20).
        """
        tk.Label(self, text=text, font=font).pack(pady=10)

    def add_radio_choice(self, text="Option", value=0, variable=None):
        """A radio choice for the form

        Args:
            text (str, optional): The text of the option. Defaults to "Option".
            value (int, optional): The value of the option. Defaults to 0.
            variable (_type_, optional): The variable that is shared between the different radio options. Defaults to None.

        Returns:
            tk.IntVar: If no varibale is passed, auto initialize a new int variable, and use that for the radio.
        """
        if variable is None:
            variable = tk.IntVar(value=value)
        tk.Radiobutton(self, text=text, value=value, variable=variable).pack()

        return variable

    def create_text_box(self, name: str, update_command: Callable[[object],None], getter: Callable[[object],Any],
                         pack_padx=0, pack_pady=0):
        """Create a text box. There is a default text box style. TODO move this out of lib

        Args:
            name (str): What is the title above the text box
            update_command (Callable[[object],None]): How to update the display.
            getter (Callable[[object],Any]): What to update the display to
            pack_padx (int, optional): Padding on the x axis on packing. Defaults to 0.
            pack_pady (int, optional): Padding on the y axis on packing. Defaults to 0.
        """
        text_box_style = {
            "bg":"white",
            "fg":"black",
            "relief":"sunken",
            "bd":2,
            "anchor":"w",      
            "padx":4,
            "pady":2
        }


        tk.Label(self, text=name).pack()
        text = tk.Label(self,**text_box_style)
        text.configure(text=getter())
        
        def update_text():
            update_command()
            text.configure(text=getter())
        
        command = Command(self ,execute=update_text, is_finished=lambda: False)

        self.m_controller.scheduler().schedule(command)

        text.pack(fill="x", padx=pack_padx, pady=pack_pady)


    def create_field(self, text="field", hidden= False):
        """Build a field for user entry

        Args:
            text (str, optional): What is the title of the field. Defaults to "field".
            hidden (bool, optional): Whether or not the field is hidden (like a password). Defaults to False.

        Returns:
            tk.Entry: the field to extract the input from.
        """
        tk.Label(self, text=text).pack()
        field = tk.Entry(self, show="*") if hidden else tk.Entry(self)
        self.m_fields.append(field)
        return field
    
    def create_action_button(self, text: str = "Action",
        command: Callable[[object],None] = lambda: messagebox.showerror("Action button","No action"), pack_pady=0):
        """Create a button that does something on activation.

        Args:
            text (str, optional): The caption of the button. Defaults to "Action".
            command (Callable[[object],None], optional): _description_. Defaults to lambda:messagebox.showerror("Action button","No action").
            pack_pady (int, optional): How much vertical padding to give the button. Defaults to 0.
        """
        
        tk.Button(self, text= text, command= command).pack(pady=pack_pady)

    def add_link(self, page_type: type[Page] , text: str = "Go to a page", pack_pady=0):
        """ Add a link to the page
        Args:
            page_type (type[Page]): The page type that we want to link to.
            text (str, optional): The link text. Defaults to "Go to a page".
            pack_pady (int, optional): Vertical padding of the link in the page. Defaults to 0.
        """
        self.m_links[page_type] = self
        self.create_action_button(text=text,
                                   command= lambda: self.goto(page_type), pack_pady=pack_pady)
        

    def set_link(self, page_type: type[Page], page: Page):
        """Link the Page class to it's singleton

        Args:
            page_type (type[Page]): The page type that needs to have it's singleton assigned
            page (Page): The page singleton
        """
        self.m_links[page_type] = page
    
    def get_links(self) -> dict[type[Page],Page]:
        """
        Returns:
            dict[type[Page],Page]: Every Page class to it's respective singleton instance.
        """
        return self.m_links



   