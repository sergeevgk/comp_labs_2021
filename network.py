import enum
import time
from threading import Thread
from message import Message, MessageQueue, MessageStatus


class Network:
    send_msg_queue = MessageQueue()
    answer_msg_queue = MessageQueue()
    posted_msgs = []
    received_msgs = []
    sender_th = Thread()
    receiver_th = Thread()

    def __init__(self, window_size=2, max_number=100, timeout=0.2, loss_probability=0.3, protocol="GBN"):
        self.window_size = window_size
        self.max_number = max_number
        self.timeout = timeout
        self.loss_probability = loss_probability
        self.protocol = protocol
        if self.protocol == "GBN":
            self.sender_th = Thread(target=self.GBN_sender, args=(self.window_size, self.max_number, self.timeout))
            self.receiver_th = Thread(target=self.GBN_receiver, args=(self.window_size,))
        else:
            self.sender_th = Thread(target=self.SRP_sender, args=(self.window_size, self.max_number, self.timeout))
            self.receiver_th = Thread(target=self.SRP_receiver, args=())
        pass

    def process_messages(self):
        self.send_msg_queue = MessageQueue(self.loss_probability)
        self.answer_msg_queue = MessageQueue(self.loss_probability)

        timer_start = time.time()

        self.sender_th.start()
        self.receiver_th.start()

        self.sender_th.join()
        self.receiver_th.join()

        timer_end = time.time()

        # print(f"posted ({len(self.posted_msgs)}): \t", self.posted_msgs)
        # print(f"received ({len(self.received_msgs)}):\t", self.received_msgs)

        return timer_end - timer_start

    def GBN_sender(self, window_size, max_number, timeout):
        curr_number = 0
        last_ans_number = -1
        start_time = time.time()
        while last_ans_number < max_number:
            expected_number = (last_ans_number + 1) % window_size

            if self.answer_msg_queue.has_msg():
                ans = self.answer_msg_queue.get_message()
                if ans.number == expected_number:
                    last_ans_number += 1
                    start_time = time.time()
                else:
                    curr_number = last_ans_number + 1

            if time.time() - start_time > timeout:
                curr_number = last_ans_number + 1
                start_time = time.time()

            if (curr_number < last_ans_number + window_size) and (curr_number <= max_number):
                k = curr_number % window_size
                msg = Message()
                msg.number = k
                msg.real_number = curr_number
                self.send_msg_queue.send_message(msg)
                self.posted_msgs.append(f"{curr_number}({k})")

                curr_number += 1
            pass

        msg = Message()
        msg.data = "STOP"
        self.send_msg_queue.send_message(msg)

    def GBN_receiver(self, window_size):
        expected_number = 0
        while True:
            if self.send_msg_queue.has_msg():
                curr_msg = self.send_msg_queue.get_message()
                if curr_msg.data == "STOP":
                    break

                if curr_msg.status == MessageStatus.LOST:
                    continue

                if curr_msg.number == expected_number:
                    ans = Message()
                    ans.number = curr_msg.number
                    self.answer_msg_queue.send_message(ans)

                    self.received_msgs.append(f"{curr_msg.real_number}({curr_msg.number})")
                    expected_number = (expected_number + 1) % window_size

                else:
                    continue

    def SRP_sender(self, window_size, max_number, timeout):
        class WndMsgStatus(enum.Enum):
            BUSY = enum.auto()
            NEED_REPEAT = enum.auto()
            CAN_BE_USED = enum.auto()

        class WndNode:
            def __init__(self, number):
                self.status = WndMsgStatus.NEED_REPEAT
                self.time = 0
                self.number = number
                pass

            def __str__(self):
                return f"( {self.number}, {self.status}, {self.time})"

        wnd_nodes = [WndNode(i) for i in range(window_size)]

        curr_number = 0
        ans_count = 0

        while ans_count < max_number:

            res_str = "["
            for i in range(window_size):
                res_str += wnd_nodes[i].__str__()
            res_str += "]"

            if self.answer_msg_queue.has_msg():
                ans = self.answer_msg_queue.get_message()
                ans_count += 1
                wnd_nodes[ans.number].status = WndMsgStatus.CAN_BE_USED

            curr_time = time.time()
            for i in range(window_size):
                if wnd_nodes[i].number > max_number:
                    continue

                send_time = wnd_nodes[i].time
                if curr_time - send_time > timeout:
                    wnd_nodes[i].status = WndMsgStatus.NEED_REPEAT

            for i in range(window_size):
                if wnd_nodes[i].number > max_number:
                    continue

                if wnd_nodes[i].status == WndMsgStatus.BUSY:
                    continue

                elif wnd_nodes[i].status == WndMsgStatus.NEED_REPEAT:

                    wnd_nodes[i].status = WndMsgStatus.BUSY
                    wnd_nodes[i].time = time.time()

                    msg = Message()
                    msg.number = i
                    msg.real_number = wnd_nodes[i].number
                    self.send_msg_queue.send_message(msg)
                    self.posted_msgs.append(f"{msg.real_number}({msg.number})")

                elif wnd_nodes[i].status == WndMsgStatus.CAN_BE_USED:
                    wnd_nodes[i].status = WndMsgStatus.BUSY
                    wnd_nodes[i].time = time.time()
                    wnd_nodes[i].number = wnd_nodes[i].number + window_size

                    if wnd_nodes[i].number > max_number:
                        continue

                    msg = Message()
                    msg.number = i
                    msg.real_number = wnd_nodes[i].number
                    self.send_msg_queue.send_message(msg)
                    self.posted_msgs.append(f"{msg.real_number}({msg.number})")

        msg = Message()
        msg.data = "STOP"
        self.send_msg_queue.send_message(msg)

    def SRP_receiver(self):
        while True:
            if self.send_msg_queue.has_msg():
                curr_msg = self.send_msg_queue.get_message()

                if curr_msg.data == "STOP":
                    break

                if curr_msg.status == MessageStatus.LOST:
                    continue

                ans = Message()
                ans.number = curr_msg.number
                self.answer_msg_queue.send_message(ans)
                self.received_msgs.append(f"{curr_msg.real_number}({curr_msg.number})")

