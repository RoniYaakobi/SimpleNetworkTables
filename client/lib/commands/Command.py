__author__ = "RONI YAAKOBI"
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from client.pages.controller_interface import ControllerInterface


class Command:
    """
        A command that runs in three phases (These are not the actual implementations, but the correct mental model):

        - Initialization:
            `initialize()`
        
        - Execution while not finished:
        ```python
        while not isFinished():
            execute()
         ```

        - End function based on if the command was interrupted during execution:
            `end(interrupted)`
            Notice this allows to change how the command reacts to finishing based on if it finished or not,
            which allows you to make the program react to whether or not the command finished its job.

    """

    def __init__(self,
                controller : "ControllerInterface",
                initialize : Callable[[object], None] | None = None,
                execute : Callable[[object], None] | None = None, 
                is_finished : Callable[[object],bool] | None  = None, 
                end : Callable[[object,bool],None] | None = None):
        """
        Args:
            controller (ControllerInterface): The object which triggers the command
            initialize (Callable[[object], None] | None, optional): What to do on command triggered. Defaults to None.
            execute (Callable[[object], None] | None, optional): What to do while the command is still active. Defaults to None.
            is_finished (Callable[[object],bool] | None, optional): Return True if the command is done. Checked before each call to execute. Defaults to None.
            end (Callable[[object,bool],None] | None, optional): How to react to the command ending. Has a flag to indicate whether or not the command was interrupted. Defaults to None.
        """
        
        
        self.controller = controller

        self._initialize = initialize
        self._execute = execute
        self._is_finished = is_finished
        self._end = end

        self._is_active = False
        self.ID = controller.scheduler()._register_command(self)

    def initialize(self):
        """ What to do on command triggered. """
        if self._initialize:
            self._initialize()
    
    def execute(self):
        """ What to do while the command is still active. """
        if self._execute:
            self._execute()

    def is_finished(self) -> bool:
        """
        Returns:
            bool: whether or not the command is organically finished for this cycle
        """
        if self._is_finished:
            return self._is_finished()
        return True 

    def end(self, interrupted: bool):
        """ How to react to the command ending. Has a flag to indicate whether or not the command was interrupted. """
        if self._end:
            self._end(interrupted)

    def cancel(self):
        """ Cancel this command. """
        if self._is_active:
            self._is_active = False
            self.end(True)
        else:
            raise Exception("Cancelled a command that wasn't running.")
    
    def is_running(self) -> bool:
        """
        Returns:
            bool: whether or not the command is currently running.
        """
        return self._is_active
