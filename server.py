import socket
from selenium import webdriver
import selenium
from time import sleep
import threading
import names

path = '/home/david/kahoot-bot/chromedriver'
INPUT_ID = 'inputSession'
NAME_ID = 'username'


class Browser:
    def __init__(self, pin, name):
        self.name = name
        self.pin = pin
        self.browser = webdriver.Chrome(path)
    def run(self):
        self.browser.get('https://kahoot.it/')
        elem = self.browser.find_element_by_id(INPUT_ID)
        elem.send_keys(self.pin + '\n')
        sleep(1)
        elem = self.browser.find_element_by_id(NAME_ID)
        elem.send_keys(self.name + '\n')
    def test(self):
        self.browser.get('https://kahoot.it/')
        elem = self.browser.find_element_by_id(INPUT_ID)
        elem.send_keys(self.pin + '\n')
        sleep(1)
        try:
            elem = self.browser.find_element_by_id(NAME_ID)
            return True
        except selenium.common.exceptions.NoSuchElementException:
            return False



class Host(threading.Thread):
    def __init__(self, conn):
        super().__init__()
        self.sock = conn

    def read(self):
        code =[]
        names = []
        number = []
        seen = 0
        while True:
            data = self.sock.recv(1)
            if data == '\x00':
                seen += 1
                if seen == 3:
                    break
                continue
            if seen == 0:
                code.append(data)
            elif seen == 1:
                names.append(data)
            elif seen == 2:
                number.append(data)

        return b''.join(code).decode(), b''.join(names).decode(), b''.join(number).decode()

    def run(self):
        try:
            code, names, number = self.read()
            print(f'got {code}, {names}, {number}')
        except:
            self.sock.close()
            return
        b = Botnet(code, names, number)
        if b.test():
            self.sock.sendall('\x01')
        else:
            self.sock.sendall('\x00')
        b.start()
        self.sock.close()

class Server:
    def __init__(self):
        self.port = 55555
        self.sock = socket.socket()
        self.sock.bind(('', self.port))
        self.sock.listen(5)

    def run(self):
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
        max_index = len(self.names)-1
        while created < self.number:
            b = Browser(self.code, self.names[index])
            b.run()
            index += 1
            if index > max_index:
                index = 0
            created += 1

    @staticmethod
    def gen_names():
        return [names.get_first_name() for _ in range(20)]

s = Server()
s.run()