import json
import numpy as np
import sys


class Strategy:
    def __init__(self, epsilon, alpha=0.02, update_beta=0.05):
        self.dct = {}
        self.alpha = alpha
        self.beta = update_beta
        path = 'logger.txt'
        self.wfile = open(path, 'w')
        with open('state_reward.txt') as rfile:
            line = rfile.readline()
            line = line.replace('(', '"[').replace(')', ']"').replace("'", '"')
            self.state_reward = json.loads(line)
            self.state_reward = {
                tuple(json.loads(k)): v
                for k, v in self.state_reward.items()
            }
        with open('next_state.txt') as rfile:
            line = rfile.readline()
            line = line.replace('(', '"[').replace(')', ']"').replace(
                "u'", '"').replace("'", '"')
            self.next_state = json.loads(line)
            self.next_state = {
                tuple(json.loads(k)): {
                    kkk: {
                        tuple(json.loads(kk)): vv
                        for kk, vv in vvv.items()
                    }
                    for kkk, vvv in v.items()
                }
                for k, v in self.next_state.items()
            }
        self.wsr = open('state_reward.txt', 'w')
        self.wns = open('next_state.txt', 'w')

        self.commands = ['left', 'right', 'stop']
        self.param = epsilon

        self.last = 'stop'
        self.previous_states = []
        self.lives = None
        self.last_state = None

    @staticmethod
    def signum(a, b):
        if a > b:
            return 1
        if a < b:
            return -1
        return 0

    @staticmethod
    def dif_x(a, b):
        if abs(a-b) > 45:
            return 2 if a > b else -2
        if abs(a-b) > 15:
            return 1 if a > b else -1
        return 0

    @staticmethod
    def dif_y(a, b):
        if abs(a-b) > 30:
            return 2 if a > b else -2
        if abs(a-b) > 10:
            return 1 if a > b else -1
        return 0

    @staticmethod
    def angle(a):
        return int(a//0.1)

    def set_state(self, state):
        # self.write(state)
        # self.write(type(state))
        params = state['params']
        if state['type'] != 'tick':
            if self.lives is not None:
                if self.lives > params['my_lives']:
                    self.reward = -2
                else:
                    self.reward = 1
                for state in self.previous_states:
                    if state in self.state_reward:
                        r = self.state_reward[state]
                        self.state_reward[state] = self.reward * \
                            self.beta + (1 - self.beta) * r
                    else:
                        self.state_reward[state] = self.reward
                self.previous_states = []
            self.map = params['proto_map']['external_id']
            self.car = params['proto_car']['external_id']
            self.lives = params['my_lives']
            self.next_step = ''
            return
        my_car = params['my_car']
        enemy_car = params['enemy_car']
        current_state = (my_car[2], self.angle(my_car[1]),
                         int(my_car[0][0]//30), int(enemy_car[0][0]//30),
                         int(my_car[0][1]//30), int(enemy_car[0][1]//30),
                         int(params['deadline_position']//10),
                         self.car, self.map)
        if self.last_state is not None:
            if self.last_state not in self.next_state:
                self.next_state[self.last_state] = {}
            if self.last not in self.next_state[self.last_state]:
                self.next_state[self.last_state][self.last] = {}
            if current_state not in self.next_state[self.last_state][self.last]:
                self.next_state[self.last_state][self.last][current_state] = 0
            self.next_state[self.last_state][self.last][current_state] += 1
        self.last_state = current_state

        if current_state in self.next_state:
            self.next_step = ''
            best_reward = 0
            for k, v in self.next_state[current_state].items():
                total_count = 0
                total_reward = 0
                for state, count in v.items():
                    if state not in self.state_reward:
                        continue
                    total_count += count
                    total_reward += count * self.state_reward[state]
                if total_count == 0:
                    continue
                avg_reward = total_reward / total_count
                if avg_reward >= best_reward:
                    self.next_step = k
                    best_reward = avg_reward
        else:
            self.next_step = ''
        return

    def get_command(self):
        choice = 'random'
        if self.next_step:
            choice = np.random.choice(['next', 'random'], p=[
                                      1-self.alpha, self.alpha])
        if choice == 'random':
            if self.last == 'stop':
                p = np.array([.5, .5, 0])
            else:
                p = np.ones(3) * self.param
                p[self.commands.index(self.last)] += 1 - np.sum(p)
            command = np.random.choice(self.commands, p=p)
        else:
            command = self.next_step
        if command != self.next_step:
            self.previous_states = []
        self.previous_states.append(self.last_state)
        self.last = command
        return command

    def write(self, x):
        self.wfile.write(str(x)+'\n')

    def __del__(self):
        self.wsr.write(str(self.state_reward))
        self.wns.write(str(self.next_state))
        self.wfile.close()


strategy = Strategy(0.02)

while True:
    try:
        z = json.loads(raw_input())
    except EOFError:
        break
    strategy.set_state(z)
    commands = ['left', 'right', 'stop']
    cmd = strategy.get_command()
    print(json.dumps({"command": cmd, 'debug': cmd}))
    sys.stdout.flush()
