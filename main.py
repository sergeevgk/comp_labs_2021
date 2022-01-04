from network import Network
from tests import losing_test, window_test


def main():
    model = Network()
    elapsed_time = model.process_messages()
    print(elapsed_time)
    pass


if __name__ == '__main__':
    # main()

    # print("------------------------------------------")
    # print("losing")
    # print("------------------------------------------")
    # losing_test()

    print("------------------------------------------")
    print("window")
    print("------------------------------------------")
    window_test()
