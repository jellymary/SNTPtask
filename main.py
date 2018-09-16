from sntp_server import SNTPServer


def open_file(name: str):
    try:
        with open(name, 'r', encoding='UTF-8') as file:
            return file.readline()
    except FileNotFoundError:
        print('error: invalid name of file entered')


if __name__ == "__main__":
    offset_time = float(open_file("offset.txt"))
    SNTPServer(offset_time).start()
