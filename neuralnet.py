import math
import random
from collections import deque


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
        return 1/(1+math.e ** (x * -1))


class Weights:
    @staticmethod
    def generate_random_weights(output_layer):
        weights = tuple()
        for _ in range(output_layer.node_count):
            weights += random.uniform(0, 1)
        return weights


class Node:
    def __init__(self, bias_weight=1, node_weights=None, activation_function=None):
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

    def set_weights(self, weights):
        self.node_weights = weights


class Layer:
    def __init__(self, output_layer, node_count, default_weights=None, is_output=False):
        self.output_layer = output_layer
        self.is_output = is_output

        self.nodes = tuple()
        for _ in node_count:
            self.nodes += Node()

        self.node_count = node_count

        if default_weights is None:
            for node in self.nodes:
                node.set_weights(Weights.generate_random_weights(output_layer))

    def run_layer(self, weight_inputs):
        output_values = list()
        weight_inputs_sorted_to_nodes = split_list(weight_inputs, self.node_count)
        if self.is_output:
            return [sum(weights) for weights in weight_inputs_sorted_to_nodes]
        for weights, node in zip(weight_inputs_sorted_to_nodes, self.nodes):
            output_values.append(*node.output_values(sum(weights)))

        return self.output_layer.run_layer(output_values)



