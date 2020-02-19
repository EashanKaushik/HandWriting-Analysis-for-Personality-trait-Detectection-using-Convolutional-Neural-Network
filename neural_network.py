import numpy as np
import read_dataset as rd
from past.builtins import xrange
from numpy import exp, array, random, dot
import numpy as np

class NeuralNetwork():
    def __init__(self):
        random.seed(1)
        self.synaptic_weights = 2 * random.random((4, 5)) - 1

    def __sigmoid(self, x):
        return 1 / (1 + exp(-x))

    def __sigmoid_derivative(self, x):
        return x * (1 - x)

    def train(self, training_set_inputs, training_set_outputs, number_of_training_iterations):
        train_input=np.array(training_set_inputs)
        train_output=np.array(training_set_outputs)
        for iteration in xrange(number_of_training_iterations):
            
            output = self.think(train_input)

            error = train_output - output

            adjustment = dot(train_input.T, error * self.__sigmoid_derivative(output))

            self.synaptic_weights += adjustment

    def think(self, inputs):
        return self.__sigmoid(dot(inputs, self.synaptic_weights))





