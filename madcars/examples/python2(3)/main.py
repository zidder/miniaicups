import json
from collections import Counter
import numpy as np
import sys


class Strategy:
    def __init__(self, epsilon, path='log.txt'):
        self.dct = {}
        self.wfile = open(path, 'w')
        self.commands = ['left', 'right', 'stop']
        self.param = epsilon
        self.last = 'stop'
        self.c = Counter()
        self.dct = {}

    @staticmethod
    def signum(a, b):
        if a > b:
            return 1
        if a < b:
            return -1
        return 0

    def set_state(self, state):
        self.wfile.write(str(state) + '\n'+str(type(state))+'\n')
        if state['type'] != 'tick':
            return
        params = state['params']
        my_car = params['my_car']
        enemy_car = params['enemy_car']
        current_state = (my_car[2], my_car[1] // 0.032,
                         self.signum(my_car[0][0], enemy_car[0][0]),
                         self.signum(my_car[0][1], enemy_car[0][1]),
                         params['deadline_position'])
        self.dct[current_state] = None
        # self.next_step = np.argmax()
        return

    def get_command(self):
        p = np.ones(3) * self.param
        p[self.commands.index(self.last)] += 1 - np.sum(p)
        command = np.random.choice(self.commands, p=p)
        self.last = command
        return command

    def __del__(self):
        self.wfile.close()


strategy = Strategy(0.2)

while True:
    z = json.loads(raw_input())
    strategy.set_state(z)
    commands = ['left', 'right', 'stop']
    cmd = strategy.get_command()
    print(json.dumps({"command": cmd, 'debug': cmd}))
    sys.stdout.flush()
