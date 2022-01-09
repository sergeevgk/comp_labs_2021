from message import Message, MessageType
from connection import Connection
import topology as topology_class


class Router:

    def __init__(self, conn, index):
        self.DR_connection = conn
        self.topology = topology_class.Topology()
        self.shortest_roads = None
        self.index = index
        self.neighbors = []

    def print_shortest_ways(self):
        shortest_ways = self.topology.get_shortest_ways(self.index)
        print(f"{self.index}: {shortest_ways}\n", end="")

    def send_neighbors(self):
        msg = Message()
        msg.type = MessageType.NEIGHBORS
        msg.data = self.neighbors.copy()
        self.DR_connection.send_message(msg)

    def get_topology(self):
        msg = Message()
        msg.type = MessageType.GET_TOPOLOGY
        self.DR_connection.send_message(msg)

    def router_start(self):
        self.send_neighbors()
        self.get_topology()

    def router_off(self):
        msg = Message()
        msg.type = MessageType.OFF
        self.DR_connection.send_message(msg)

    def add_node(self, index, neighbors):
        self.topology.add_node(index)
        for j in neighbors:
            self.topology.add_link(index, j)

        if index in self.neighbors:
            if index not in self.topology.topology[self.index]:
                msg = Message()
                msg.type = MessageType.NEIGHBORS
                msg.data = [index]
                self.DR_connection.send_message(msg)

    def delete_node(self, index):
        self.topology.delete_node(index)

    def process_message(self):
        input_msg = self.DR_connection.get_message()

        if input_msg is None:
            return

        print(f"Router no. ({self.index}) received message: {input_msg}\n", end="")

        if input_msg.type == MessageType.NEIGHBORS:
            index = input_msg.data["index"]
            neighbors = input_msg.data["neighbors"]
            self.add_node(index, neighbors)

        elif input_msg.type == MessageType.SET_TOPOLOGY:
            new_topology = input_msg.data
            self.topology = new_topology

        elif input_msg.type == MessageType.OFF:
            index = input_msg.data
            self.delete_node(index)

        elif input_msg.type == MessageType.PRINT_WAYS:
            self.print_shortest_ways()

        else:
            print("Unexpected msg type:", input_msg.type)

    pass


class DesignatedRouter:

    def __init__(self):
        self.connections = []
        self.topology = topology_class.Topology()

    def add_connection(self):
        new_connection = Connection()
        new_index = len(self.connections)
        self.connections.append(new_connection)
        return new_connection, new_index

    def add_node(self, index, neighbors):
        self.topology.add_node(index)
        for j in neighbors:
            self.topology.add_link(index, j)

    def delete_node(self, index):
        self.topology.delete_node(index)

    def send_all_exclude_one(self, exclude_index, msg):
        for conn_ind in range(len(self.connections)):
            conn = self.connections[conn_ind]
            if conn is None:
                continue
            if conn_ind == exclude_index:
                continue
            conn.send_message(msg, 1)

    def process_neighbors_message(self, conn_ind, input_msg):
        self.add_node(conn_ind, input_msg.data)

        msg = Message()
        msg.type = MessageType.NEIGHBORS
        msg.data = {"index": conn_ind,
                    "neighbors": input_msg.data
                    }

        self.send_all_exclude_one(conn_ind, msg)

    def process_off_message(self, conn_ind):
        self.delete_node(conn_ind)

        msg = Message()
        msg.type = MessageType.OFF
        msg.data = conn_ind

        self.send_all_exclude_one(conn_ind, msg)

    def print_shortest_ways(self):
        msg = Message()
        msg.type = MessageType.PRINT_WAYS
        for conn in self.connections:
            conn.send_message(msg, 1)

    def process_message(self):
        for conn_ind in range(len(self.connections)):
            conn = self.connections[conn_ind]
            if conn is None:
                continue

            input_msg = conn.get_message(1)

            if input_msg is None:
                continue

            print(f"Designated Router received from no. ({conn_ind}) message: {input_msg}\n", end="")

            if input_msg.type == MessageType.NEIGHBORS:
                self.process_neighbors_message(conn_ind, input_msg)

            elif input_msg.type == MessageType.GET_TOPOLOGY:
                msg = Message()
                msg.type = MessageType.SET_TOPOLOGY
                msg.data = self.topology.copy()
                conn.send_message(msg, 1)

            elif input_msg.type == MessageType.OFF:
                self.process_off_message(conn_ind)

            else:
                print("Unexpected message type:", input_msg.type)
