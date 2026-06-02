__author__ = "RONI YAAKOBI"
from client.lib.pages import Page, PageType, ControllerInterface
from tkinter import Frame

from threading import Thread, Lock

from client.src.commands.SubscribeCommand import SubscribeCommand
from client.src.commands.PublishCommand import PublishCommand

from protocol.Entry import EntryType
from client.src.GraphCanva import Graph, initialize as intialize_graphing, run as run_graphs


class DashboardPage(Page):
    PAGE_ID = PageType.assign_id("dashboard")
    def __init__(self, parent: Frame, controller: ControllerInterface):
        """
        Args:
            parent (Frame): The Tk Frame which this page is connected to.
            controller (ControllerInterface): The object which controls this object.
        """
        super().__init__(parent, controller)

        self.set_title("Dashboard")

        self.subscribe_topic = self.create_field("Subscribe to topic:")
        self.subscribe_topic.pack()
        self.create_action_button("Subscribe", self._subscribe_action, pack_pady=5)
        
        self.publish_topic = self.create_field("Publish to topic:")
        self.publish_topic.pack()

        self.entry_type = self.add_radio_choice("Boolean",EntryType.BOOLEAN.value)
        self.entry_type = self.add_radio_choice("Integer",EntryType.INT_64.value, self.entry_type)
        self.entry_type = self.add_radio_choice("String",EntryType.STRING.value, self.entry_type)

        self.value_bytes = self.create_field("Value bytes")
        self.value_bytes.pack()

        self.create_action_button("Publish", self._publish_action, pack_pady=5)

        self.inspect_target = self.create_field("Inspect topic:")
        self.inspect_target.pack()

        self.create_action_button("Inspect", self._inspect_action, pack_pady=5)

        self.inspect_result = ""

        self.create_text_box("Topic:", self._update_inspection, lambda : self.inspect_result)

        self.create_action_button("Graph (only integer)", self._turn_on_graph, pack_pady=5)

        self.graph_data = []
        self.graph_data_lock = Lock()
        self.graph = None


    def _subscribe_action(self):
        """ Use the input username and password to attempt to login. """
        topic = self.subscribe_topic.get()

        self.scheduler().schedule(SubscribeCommand(self, topic))

    def _publish_action(self):
        topic = self.publish_topic.get()
        entry_type = EntryType(self.entry_type.get())
        bytes_value = self.value_bytes.get().encode("utf-8")

        self.scheduler().schedule(PublishCommand(self, topic, entry_type, bytes_value))

    def _inspect_action(self):
        inspect_result = self.backend().get_topic(self.inspect_target.get())

        if not inspect_result:
            return

        self.inspect_result = EntryType.format(inspect_result.entry_type, inspect_result.value_bytes)


    
    def _update_inspection(self):
        inspect_result = self.backend().get_topic(self.inspect_target.get())

        if not(inspect_result):
            return

        values = [EntryType.format(EntryType.INT_64, bytes) for bytes in inspect_result.values_int]

        with self.graph_data_lock:
            self.graph_data = list(zip(inspect_result.timestamps, values))
            if self.graph:
                self.graph.data_points = self.graph_data

    def _turn_on_graph(self):
        self.graph_thread = Thread(target=self.start_graph, daemon=True)
        self.graph_thread.start()

        self.graph_thread.join()

    def start_graph(self):
        intialize_graphing()
        with self.graph_data_lock:
            self.graph = Graph("Data", self.graph_data, self.graph_data_lock)
        run_graphs()
        
