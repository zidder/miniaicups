import numpy as np


class Layer:
    def __init__(self, input_layers, number_of_neurons):
        self.n = number_of_neurons
        self.input_layers = input_layers
        self.start_end = {}
        self.m = 0
        start = 0
        end = 0
        for ind, layer in enumerate(input_layers):
            self.m += layer.n
            end += layer.n
            self.start_end[ind] = [start, end]
            start = end


class LinearLayer(Layer):
    def __init__(self, input_layers, number_of_neurons, *, W=None, b=None):
        super().__init(input_layers, number_of_neurons)
        self.b = b or self._init_b()
        self.W = W or self._init_W()

    def _init_b(self):
        return np.random.normal(0, 1, self.n)

    def _init_W(self):
        return np.random.normal(0, 1, (self.n, self.m))

    def gradient_input(self, grad, *, ind=None):
        if len(grad.shape) == 2:
            return np.array([self.gradient_input(i, ind=ind) for i in grad])
        else:
            g = np.zeros((self.m, self.n))
            for i in range(self.m):
                g[i] = grad * W[:, i]
            if ind is None:
                return g
            start, end = self.start_end[ind]
            return g[start:end, :]

    def gradient_W(self, grad, X):
        pass

    def gradient_b(self, grad, X):
        pass

    def result(self, X):
        return np.dot(self.W, X) + self.b
