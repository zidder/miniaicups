import numpy as np


class QLearning:
    def __init__(self, commands, *, random_ratio=0.02, update_ratio=0.05,
                 random_pick_last_ratio=None, **kwargs):
        self.last_ratio = random_pick_last_ratio
        self.alpha = random_ratio
        self.beta = update_ratio

        self.commands = commands

        self.next_state = {}
        self.state_reward = {}
        self.last_state = None
        self.last_command = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_reward(self, observation):
        raise NotImplementedError

    def set_observation(self, observation):
        reward = self.get_reward(observation)
        self.update_state_reward(observation, reward)
        self.chosen_command = self.get_best_command(observation)
        command = self.get_command()

    def get_command(self):
        if np.random.random() < self.alpha:
            p = np.zeros(len(self.commands))
            p[self.commands.index(self.last_command)] = self.last_ratio
            d = (1 - np.sum(p)) / (len(p) - 1)
            p = np.array([i if i else d for i in p])
            command = self.commands[np.random.choice(range(len(p)), p)]
            self.last_command = command
        else:
            self.last_command = self.chosen_command
        return self.last_command

    def get_best_command(self, observation):
        raise NotImplementedError

    def update_state_reward(self, reward):
        raise NotImplementedError
