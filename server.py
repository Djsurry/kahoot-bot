import socket
from selenium import webdriver
import selenium
from time import sleep
import threading
import names

path = '/home/david/kahoot-bot/chromedriver'
INPUT_ID = 'inputSession'
NAME_ID = 'username'
options = webdriver.ChromeOptions()
options.add_argument('headless')


class Browser(threading.Thread):
    def __init__(self, pin, name):
        super().__init__()
        self.name = name
        self.pin = pin
        self.browser = None

    def run(self):
        self.browser = webdriver.Chrome(path, chrome_options=options)
        self.browser.get('https://kahoot.it/')
        elem = self.browser.find_element_by_id(INPUT_ID)
        elem.send_keys(self.pin + '\n')
        sleep(1)
        elem = self.browser.find_element_by_id(NAME_ID)
        elem.send_keys(self.name + '\n')
    def test(self):
        self.browser = webdriver.Chrome(path, chrome_options=options)
        self.browser.get('https://kahoot.it/')
        elem = self.browser.find_element_by_id(INPUT_ID)
        elem.send_keys(self.pin + '\n')
        sleep(5)
        try:
            _ = self.browser.find_element_by_id(NAME_ID)
            return True
        except:
            return False



class Host(threading.Thread):
    def __init__(self, conn):
        super().__init__()
        self.sock = conn

    def read(self):
        print('reading')
        code =[]
        names = []
        number = []
        seen = 0
        while True:
            data = self.sock.recv(1)
            if not data:
                return None, None, None
            print(data)
            if data == b'\x00':
                seen += 1
                print(seen)
                if seen == 3:
                    print('exiting')
                    break
                continue
            if seen == 0:
                code.append(data)
            elif seen == 1:
                names.append(data)
            elif seen == 2:
                number.append(data)
        print('returning')
        return b''.join(code).decode(), b''.join(names).decode(), b''.join(number).decode()

    def run(self):
        print('STARTING')
        try:
            code, names, number = self.read()
            if code is None:
                return
            print('done')
            print(f'got {code}, {names}, {number}')
        except:
            self.sock.close()
            return
        b = Botnet(code, names, number)
        if b.test():
            self.sock.sendall(b'\x01')
        else:
            self.sock.sendall(b'\x00')
            return
        b.start()
        self.sock.close()

class Server:
    def __init__(self):
        self.port = 55555
        self.sock = socket.socket()
        self.sock.bind(('', 55555))
        print(f'PORT: {self.sock.getsockname()[1]}')
        self.sock.listen(5)
    def test(self):
        conn, addr = self.sock.accept()
        print('GOT CONN')
        print(conn.recv(2048))
    def run(self):
        while True:
            conn, addr = self.sock.accept()
            print('Got connection')
            h = Host(conn)
            h.start()


class Botnet:
    def __init__(self, code, names, number):
        self.code = code
        self.names = names.split() if names else Botnet.gen_names()
        self.number = number

    def test(self):
        print('testing')
        b = Browser(self.code, self.names[0])
        return b.test()

    def start(self):
        print('starting')
        created = 0
        index = 0
        print(f"names: {self.names}")
        max_index = len(self.names)-1
        while created < int(self.number):
            print('Creating bot {}'.format(created))
            b = Browser(self.code, self.names[index])
            b.start()
            index += 1
            if index > max_index:
                index = 0
            created += 1

    @staticmethod
    def gen_names():
        return [names.get_first_name() for _ in range(20)]


s = Server()
s.run()