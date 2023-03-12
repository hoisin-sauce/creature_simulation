import math
import random
from collections import deque
import heapq


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

    def mutate(self, weight_chance, weight_range):
        for i in range(len(self.node_weights)):
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
        else:
            for node, weights in zip(self.nodes, default_weights):
                node.set_weights(weights[1:], bias_weight=weights[0])

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

    def get_weights(self):
        return [[node.bias_weight, *node.node_weights] for node in self.nodes]


class Network:
    def __init__(self, _shape: list, default_weights=None):
        self.layers = list()
        self.shape = _shape[:]
        shape = _shape[:]
        shape.reverse()
        if default_weights is not None:
            d_w = None if len(default_weights) < 1 else default_weights[0]
            self.layers.append(Layer(None, shape[0], default_weights=d_w, is_output=True))
            shape.pop(0)
            default_weights.pop(0)
            for i, weights in zip(shape, default_weights):
                self.layers.append(Layer(self.layers[-1], i, default_weights=weights))
        else:
            self.layers.append(Layer(None, shape[0], default_weights=None, is_output=True))
            shape.pop(0)
            for i in shape:
                self.layers.append(Layer(self.layers[-1], i))
        self.fitness = 0

    def run_network(self, inputs):
        return self.layers[-1].run_layer(inputs)

    def mutate_network(self, weight_chance, weight_range):
        for layer in self.layers:
            layer.mutate_layer(weight_chance, weight_range)

    def duplicate_network(self):
        weights = [layer.get_weights() for layer in self.layers]
        return Network(self.shape, default_weights=weights)


if __name__ == "__main__":
    # test_data
    test_data = [[a, b, a + b] for a in range(-100, 100) for b in range(-100, 100)]

    def fitness(network: Network):
        # print(network.run_network([1, 1])[0])
        return sum([
            math.sqrt(
                (test[2] - network.run_network([test[0], test[1]])[0])**2)
            for test in test_data]) / len(test_data)

    # generate 99 networks
    # run all networks to get fitness
    # delete lower 66 networks
    # create 2 clones of each of remaining 33
    # mutate clones
    # repeat untill average fitness < 0.01

    networks = [Network([2, 4, 4, 4, 4, 4, 1]) for _ in range(99)]
    mean_fitness = 100
    inc = 0
    while mean_fitness > 0.1:
        total_fit = 0
        sorted_networks = []
        for i, network in enumerate(networks):
            print(i)
            network.fitness = fitness(network)
            heapq.heappush(sorted_networks, (network.fitness, network))
            total_fit += network.fitness
        mean_fitness = total_fit / len(networks)

        surviving_networks = []
        while sorted_networks:
            surviving_networks.append(heapq.heappop(sorted_networks)[1])
        networks = surviving_networks[:33]


        additional_clones = list()

        for network in networks:
            net1, net2 = [network.duplicate_network() for _ in range(2)]
            net1.mutate_network(0.1, [-0.02, 0.02])
            net2.mutate_network(0.1, [-0.02, 0.02])
            additional_clones.append(net1)
            additional_clones.append(net2)

        networks.extend(additional_clones)
        inc += 1
        print(f"{inc} : {mean_fitness}")

    [print(networks[i].run_network([1, 1])) for i in range(99)]
    print(len(additional_clones))
    print(inc)

