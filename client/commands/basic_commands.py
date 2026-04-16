__author__ = "RONI YAAKOBI"
import tkinter as tk
from typing import Callable

class Command:
    def __init__(self,
                controller,
                initialize : Callable[[object], None] = lambda: None,
                execute : Callable[[object], None] = lambda: None, 
                is_finished : Callable[[object],bool] = lambda: True, # explore the default being never stopping
                end : Callable[[object,bool],None] = lambda inturrepted: None):
        
        self.controller = controller
        self._initialize = initialize
        self._execute = execute
        self._is_finished = is_finished
        self._end = end
        self.active = False
        self.ID = controller.scheduler().register_command(self)
    
    def schedule(self):
        self.active = True
        self._initialize()

    def cancel(self, interrupted= True):
        self.active = False
        self._end(interrupted)

class CommandScheduler:
    def __init__(self, root: tk.Tk, period = 10):
        self.root = root
        self.period = period
        self.commands = []

    def schedule(self, command: Command):
        command.schedule()

    def register_command(self, command: Command):
        self.commands.append(command)
        return len(self.commands)

    
    def periodic(self):
        # iterate only over active commands
        for command in self.commands[:]: # TODO figure out if the colon is needed to work
            if not command.active:
                continue

            if command._is_finished():
                command.cancel(False)
            else:
                command._execute()


        self.root.after(self.period, self.periodic)


    
