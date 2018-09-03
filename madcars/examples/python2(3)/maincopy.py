import json
import numpy as np
import sys


class Strategy:
    def __init__(self, epsilon, alpha=0.1, update_beta=0.05):
        self.dct = {}
        self.alpha = alpha
        self.beta = update_beta
        with open('state_reward.txt') as rfile:
            line = rfile.readline()
            line = line.replace('(','"[').replace(')',']"').replace("'",'"')
            self.state_reward = json.loads(line)
            self.state_reward = {
                tuple(json.loads(k)): v
                for k, v in self.state_reward.items()
            }
        with open('next_state.txt') as rfile:
            line = rfile.readline()
            line = line.replace('(','"[').replace(')',']"').replace("'",'"')
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
        with open('state_reward1.txt') as rfile:
            line = rfile.readline()
            line = line.replace('(','"[').replace(')',']"').replace("'",'"')
            self.state_reward1 = json.loads(line)
            self.state_reward1 = {
                tuple(json.loads(k)): v
                for k, v in self.state_reward1.items()
            }
        with open('next_state1.txt') as rfile:
            line = rfile.readline()
            line = line.replace('(','"[').replace(')',']"').replace("'",'"')
            self.next_state1 = json.loads(line)
            self.next_state1 = {
                tuple(json.loads(k)): {
                    kkk: {
                        tuple(json.loads(kk)): vv
                        for kk, vv in vvv.items()
                    }
                    for kkk, vvv in v.items()
                }
                for k, v in self.next_state1.items()
            }
        self.next_state.update(self.next_state1)
        self.state_reward.update(self.state_reward1)
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

    def set_state(self, state):
        params = state['params']
        if state['type'] != 'tick':
            if self.lives is not None:
                if self.lives > params['my_lives']:
                    self.reward = -1
                else:
                    self.reward = 1
                for state in self.previous_states:
                    if state in self.state_reward:
                        r = self.state_reward[state]
                        self.state_reward[state] = self.reward * self.beta + (1 - self.beta) * r
                    else:
                        self.state_reward[state] = self.reward
                self.previous_states.clear()
            self.lives = params['my_lives']
            self.next_step = ''
            return
        my_car = params['my_car']
        enemy_car = params['enemy_car']
        current_state = (my_car[2], self.signum(my_car[1], 0),# // 0.032 // 5,
                         self.signum(my_car[0][0], enemy_car[0][0]),
                         self.signum(my_car[0][1], enemy_car[0][1]),
                         int(params['deadline_position']//10))
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
            choice = np.random.choice(['next', 'random'], p=[1-self.alpha, self.alpha])
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


strategy = Strategy(0.02)

while True:
    z = json.loads(input())
    strategy.set_state(z)
    commands = ['left', 'right', 'stop']
    cmd = strategy.get_command()
    print(json.dumps({"command": cmd, 'debug': cmd}))
    sys.stdout.flush()
