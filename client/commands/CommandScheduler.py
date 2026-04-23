from client.commands.Command import Command
from tkinter import Tk

import threading

class CommandScheduler:
    """
        In charge of the scheduling of all the commands.
        Use this scheduler in order to schdule commands.
    """
    def __init__(self, root: Tk, period_ms : int = 10):
        """
            - root (Tk): The window to tie the command scheduler's periodic to.
            - period_ms (int): The amount of miliseconds to wait between command cycles.
                Faster means more load while slower means reactivness drops.
        """
        self.root = root
        self.period = period_ms
        self.commands = []

        self.__periodic_thread = threading.Thread(target=self.__periodic, daemon=True)
        self.__periodic_thread.start()

    def schedule(self, command: Command):
        """
            Schedule a given command.
            - command (Command): The command that needs to be scheduled
        """
        command.initialize()
        command._is_active = True

    def _register_command(self, command: Command):
        """
            Internal CommandScheduler method. Do not call.
            - command (Command): The given command to register to the CommandScheduler.

            - returns and int which is the ID of the command by the CommandScheduler.
        """
        self.commands.append(command)
        return len(self.commands)

    
    def __periodic(self):
        """
            Run the all active commands periodically after checking that they haven't finished.
        """
        for command in self.commands:
            if not command._is_active:
                continue

            if command.is_finished():
                self.__stop_command(command)
            else:
                command.execute()


        self.root.after(self.period, self.__periodic)

    def __stop_command(self, command: Command):
        """
            - command (Command): A given command which has finished and needs to be stopped.
        """
        command._is_active = False
        command.end(False)