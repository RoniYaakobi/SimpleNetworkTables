__author__ = "RONI YAAKOBI"
from client.lib.commands.Command import Command
from tkinter import Tk

import threading

class CommandScheduler:
    """
        In charge of the scheduling of all the commands.
        Use this scheduler in order to schdule commands.
    """

    def __init__(self, root: Tk, period_ms : int = 10):
        """_summary_

        Args:
            root (Tk): The window to tie the command scheduler's periodic to.
            period_ms (int, optional): The amount of miliseconds to wait between command cycles.
                Faster means more load while slower means reactivness drops. Defaults to 10.
        """
        self.root = root
        self.period = period_ms
        self.commands = []

        self.__periodic_thread = threading.Thread(target=self.__periodic, daemon=True)
        self.__periodic_thread.start()

    def schedule(self, command: Command):
        """Schedule a given command.

        Args:
            command (Command): The command that needs to be scheduled
        """
        command.initialize()
        command._is_active = True


    def _register_command(self, command: Command) -> int:
        """Internal CommandScheduler method. Do not call.

        Args:
            command (Command): The given command to register to the CommandScheduler.

        Returns:
            int: ID of the command by this CommandScheduler.
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
        """ Deactivate the command and end it.
        Args:
            command (Command): A given command which has finished and needs to be stopped.
        """
        command._is_active = False
        command.end(False)