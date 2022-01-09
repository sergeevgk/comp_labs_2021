from network import Network


def linear():
    cur_topology = {
        "nodes": [0, 1, 2, 3, 4],
        "neighbors": [[1], [0, 2], [1, 3], [2, 4], [3]]
    }
    ntw = Network()
    ntw.simulate(cur_topology["nodes"], cur_topology["neighbors"])
    pass


def circle():
    cur_topology = {
        "nodes": [0, 1, 2, 3, 4],
        "neighbors": [[4, 1], [0, 2], [1, 3], [2, 4], [3, 0]]
    }
    ntw = Network()
    ntw.simulate(cur_topology["nodes"], cur_topology["neighbors"])
    pass


def star():
    cur_topology = {
        "nodes": [0, 1, 2, 3, 4],
        "neighbors": [[1, 2, 3, 4], [0], [0], [0], [0]]
    }
    ntw = Network()
    ntw.simulate(cur_topology["nodes"], cur_topology["neighbors"])
    pass
