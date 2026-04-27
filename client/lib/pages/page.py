__author__ = "RONI YAAKOBI"
import tkinter as tk
from tkinter import messagebox
from client.lib.commands.Command import Command

from client.lib.pages.ControllerInterface import ControllerInterface


class PageType:
    ids_to_names = dict()
    names_to_ids = dict()
    page_types = 0

    @staticmethod
    def assign_id(name):
        PageType.page_types += 1
        PageType.ids_to_names = {PageType.page_types: name, **PageType.ids_to_names}
        PageType.names_to_ids = {name: PageType.page_types, **PageType.names_to_ids}
        return PageType.page_types

    @staticmethod
    def identify(name):
        return PageType.names_to_ids.get(name)


class Page(tk.Frame, ControllerInterface):
    PAGE_ID = PageType.assign_id("plain")

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        ControllerInterface.__init__(self, controller.backend(), controller.scheduler(), controller= controller)

    def show(self):
        self.tkraise()
        self.m_controller.current_page = __class__.PAGE_ID

    def set_title(self, text="Title", font=("Arial", 20)):
        tk.Label(self, text=text, font=font).pack(pady=10)

    def add_radio_choice(self, text="Option", value=0, variable=None):
        if variable is None:
            variable = tk.IntVar(value=value)
        tk.Radiobutton(self, text=text, value=value, variable=variable).pack()

        return variable

    def create_text_box(self, name, update_command, getter, pack_padx=0, pack_pady=0):
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
        tk.Label(self, text=text).pack()
        field = tk.Entry(self, show="*") if hidden else tk.Entry(self)
        self.m_fields.append(field)
        return field
    
    def create_action_button(self, text="Action",
        command= lambda: messagebox.showerror("Action button","No action"), pack_pady=0):
        
        tk.Button(self, text= text, command= command).pack(pady=pack_pady)

    def add_link(self, page_type: type , text="Go to a page", pack_pady=0):
        self.m_links[page_type] = self
        self.create_action_button(text=text,
                                   command= lambda: self.goto(page_type), pack_pady=pack_pady)
        

    def set_link(self, page_type: type, page):
        self.m_links[page_type] = page
    
    def get_links(self):
        return self.m_links
    

    


   