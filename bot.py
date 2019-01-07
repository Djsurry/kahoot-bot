from selenium import webdriver
from time import sleep
from socket import socket
import PySimpleGUI as sg  
path = '/Users/davidsurry/Downloads/chromedriver'
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


class Window:
    def __init__(self):
        self.layout = [[sg.Text('Welcome to Kahoot-Bot!', key='intro')],
                       [sg.Text('Game Code'), sg.Input(key='code')],
                       [sg.Text('Number of bots (no more than 100)'), sg.Input(key='number')],
                       [sg.Text('Custom names *optional* (text file of names, each on own line)')],
                       [sg.Input(key='file', do_not_clear=True), sg.FileBrowse()],
                       [sg.OK(), sg.Exit()]]
        self.window = sg.Window('Window that stays open').Layout(self.layout)

    def run(self):
        while True:
            event, values = self.window.Read()
            if event is None or event == 'Exit':
                break
            if values['code'] == '':
                sg.Popup('Please enter a game-code')
                continue
            else:
                code = values['code']
            try:
                number = int(values['number'])
            except ValueError:
                sg.Popup('Please enter a number for the number field')
                continue
            if 1 > number or number > 100:
                sg.Popup('Please enter a number bigger than 0 and less than 100')
            if values['file'] != '':
                try:
                    with open(values['file']) as f:
                        names = [n.strip() for n in f.readlines()]
                except FileNotFoundError:
                    sg.Popup('File {} not found'.format(values['file']))
                    continue
            else:
                names = None
            self.window.FindElement('intro').Update('Working')
            r = self.order_botting(code, names, number)

            if r is None:
                sg.Popup('Unknown Error Occured')
            elif r == 1:
                sg.Popup('Success')
            elif r == 0:
                sg.Popup('Failure: Bad code')

    @staticmethod
    def order_botting(code, names, number):
        sock = socket()
        print('connecting')
        sock.connect(('167.99.180.229', 55555))
        print('sendin')
        sock.sendall(f'{code}\x00{names}\x00{number}\x00'.encode())
        resp = sock.recv(1)
        if not resp:
            return None
        elif resp == b'\x00':
            return 0
        elif resp == b'\x01':
            return 1





w = Window()
w.run()