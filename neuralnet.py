import math
import random
from collections import deque
import copy


def chunks(l, n):
    """Yield n number of striped chunks from l."""
    for i in range(0, n):
        yield l[i::n]


def split_list(input_list, chunk_size):
    # Create a deque object from the input list
    deque_obj = deque(input_list)
    # While the deque object is not empty
    while deque_obj:
        # Pop chunk_size elements from the left side of the deque object
        # and append them to the chunk list
        chunk = []
        for _ in range(chunk_size):
            if deque_obj:
                chunk.append(deque_obj.popleft())

        # Yield the chunk
        yield chunk


class ActivationFunction:
    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.e ** (x * -1))


class Weights:
    @staticmethod
    def generate_random_weights(output_layer):
        if output_layer is not None:
            weights = list()
            for _ in range(output_layer.node_count):
                weights.append(random.uniform(-1, 1))
            return weights
        return [1]


class Node:
    def __init__(self, bias_weight=-1, node_weights=None, activation_function=None):
        if node_weights is None:
            node_weights = list()
        if activation_function is None:
            activation_function = ActivationFunction.sigmoid
        self.node_weights = node_weights
        self.bias_weight = bias_weight
        self.activation_function = activation_function

    def output_values(self, input_from_nodes):
        node_value = input_from_nodes + self.bias_weight
        output_value = self.activation_function(node_value)
        return [weight * output_value for weight in self.node_weights]

    def set_weights(self, weights, bias_weight=None):
        self.node_weights = weights
        if bias_weight is not None:
            self.bias_weight = bias_weight

    def mutate_node(self, weight_chance, weight_range):
        for i in range(self.node_weights):
            if random.uniform(0, 1) > weight_chance:
                self.node_weights[i] += random.uniform(*weight_range)


class Layer:
    def __init__(self, output_layer, node_count, default_weights=None, is_output=False):
        self.output_layer = output_layer
        self.is_output = is_output

        self.nodes = tuple()
        for _ in range(node_count):
            self.nodes += (Node(),)

        self.node_count = node_count

        if default_weights is None:
            for node in self.nodes:
                node.set_weights(Weights.generate_random_weights(output_layer))

    def run_layer(self, weight_inputs: list):
        if self.is_output:
            return weight_inputs
        output_values = list()
        for weight, node in zip(weight_inputs, self.nodes):
            output_values.append(node.output_values(weight))
        values_for_next_layer = [0] * self.output_layer.node_count
        for values in output_values:
            for i, value in enumerate(values):
                values_for_next_layer[i] += value

        return self.output_layer.run_layer(values_for_next_layer)

    def mutate_layer(self, weight_chance, weight_range):
        for node in self.nodes:
            node.mutate(weight_chance, weight_range)


class Network:
    def __init__(self, shape: list, default_weights=None):
        self.layers = list()
        shape.reverse()
        self.layers.append(Layer(None, shape[0], default_weights=default_weights, is_output=True))
        shape.pop(0)
        for i in shape:
            self.layers.append(Layer(self.layers[-1], i))

    def run_network(self, inputs):
        return self.layers[-1].run_layer(inputs)

    def mutate_network(self, weight_chance, weight_range):
        for layer in self.layers:
            layer.mutate_layer(weight_chance, weight_range)


if __name__ == "__main__":
    example_network = Network([1, 4, 4, 2])
    print(example_network.run_network((1,)))
