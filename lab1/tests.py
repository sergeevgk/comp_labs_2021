import numpy as np
import time
from threading import Thread
from message import MessageQueue
from network import Network
import matplotlib.pyplot as plt


def draw_plots_loss(loss_probability_arr, gbn_k, srp_k, gbn_time, srp_time):
    fig, ax = plt.subplots()
    ax.plot(loss_probability_arr, gbn_k, label="Selective repeat")
    ax.plot(loss_probability_arr, srp_k, label="Go-Back-N")
    ax.set_xlabel('вероятность потери пакета')
    ax.set_ylabel('коэффициент эффективности')
    ax.legend()
    fig.show()
    plt.savefig("loss_k_fig.png")

    fig, ax = plt.subplots()
    ax.plot(loss_probability_arr, gbn_time, label="Go-Back-N")
    ax.plot(loss_probability_arr, srp_time, label="Selective repeat")
    ax.set_xlabel('вероятность потери пакета')
    ax.set_ylabel('время передачи, с')
    ax.legend()
    fig.show()
    plt.savefig("loss_t_fig.png")
    pass


def draw_plots_window(window_size_arr, gbn_k, srp_k, gbn_time, srp_time):
    fig, ax = plt.subplots()
    ax.plot(window_size_arr, gbn_k, label="Go-Back-N")
    ax.plot(window_size_arr, srp_k, label="Selective repeat")
    ax.set_xlabel('размер окна')
    ax.set_ylabel('коэф. эффективности')
    ax.legend()
    fig.show()
    plt.savefig("wnd_k_fig.png")

    fig, ax = plt.subplots()
    ax.plot(window_size_arr, gbn_time, label="Go-Back-N")
    ax.plot(window_size_arr, srp_time, label="Selective repeat")
    ax.set_xlabel('размер окна')
    ax.set_ylabel('время передачи, с')
    ax.legend()
    fig.show()
    plt.savefig("wnd_t_fig.png")
    pass


def print_table(stat_name, stat_array, gbn_time, gbn_k, srp_time, srp_k):
    print(stat_name)
    print(stat_array)
    print("GBN")
    print(gbn_time)
    print("time")
    print("k")
    print(gbn_k)

    print("SRP")
    print(srp_time)
    print("time")
    print("k")
    print(srp_k)
    pass


def losing_test():
    window_size = 2
    timeout = 0.2
    max_number = 100
    loss_probability_arr = np.linspace(0, 0.9, 9)
    protocol_arr = ["GBN", "SRP"]

    print("p    | GBN             |SRP")
    print("     | t     |k        |t    |  k")

    gbn_time = []
    srp_time = []
    gbn_k = []
    srp_k = []
    for p in loss_probability_arr:
        table_row = f"{p:.1f}\t"
        for protocol in protocol_arr:
            model = Network(window_size, max_number, timeout, p, protocol)
            elapsed_time = model.process_messages()
            k = len(model.received_msgs) / len(model.posted_msgs)

            table_row += f" | {elapsed_time:2.2f}  | {k:.2f}   "
            if protocol == "GBN":
                gbn_time.append(elapsed_time)
                gbn_k.append(k)
            else:
                srp_time.append(elapsed_time)
                srp_k.append(k)

        print(table_row)

    draw_plots_loss(loss_probability_arr, gbn_k, srp_k, gbn_time, srp_time)

    print_table("p", loss_probability_arr, gbn_time, gbn_k, srp_time, srp_k)
    pass


def window_test():
    window_size_arr = range(2, 11)
    timeout = 0.2
    max_number = 100
    loss_probability = 0.2
    protocol_arr = ["GBN", "SRP"]

    print("w    | GBN             |SRP")
    print("     | t     |k        |t    |  k")

    gbn_time = []
    srp_time = []
    gbn_k = []
    srp_k = []
    for window_size in window_size_arr:
        table_row = f"{window_size:}\t"

        for protocol in protocol_arr:
            model = Network(window_size, max_number, timeout, loss_probability, protocol)
            elapsed_time = model.process_messages()

            k = len(model.received_msgs) / len(model.posted_msgs)

            table_row += f" | {elapsed_time:2.2f}  | {k:.2f}   "
            if protocol == "GBN":
                gbn_time.append(elapsed_time)
                gbn_k.append(k)
            else:
                srp_time.append(elapsed_time)
                srp_k.append(k)

        print(table_row)

    draw_plots_window(window_size_arr, gbn_k, srp_k, gbn_time, srp_time)

    print_table("w", window_size_arr, gbn_time, gbn_k, srp_time, srp_k)
    pass

