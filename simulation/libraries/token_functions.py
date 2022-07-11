from collections import Counter
import numpy as np
from scipy import ndimage


def assignOrder(order):
    def do_assignment(to_func):
        to_func.order = order
        return to_func
    return do_assignment


class TokenFunctions:
    """
        Explanation of token functions
        1) Exploring area ->    x amount of tokens for first discovery
                                x/n amount of tokens for second discovery
                                Not sure if we should add more layers in this token function
        2) Communicating location of Point of Interest (POI) -> x amount of tokens based on the certainty level of the discovery
        Example: Drone 2 knows 60% sure it found a human at location (2,4). It gets awarded 0.6*n amount of tokens.
        3) Verifying POI -> Certainty level = phi -> amount of tokens equal to phi*n. Where n is the parameter to optimise
        4)

    """
    def __init__(self, weights=None):
        self.function_count = len(self.get_functions())
        if weights is None:
            weights = [1/self.function_count] * self.function_count
        self.weights = weights
        self.tokens = {}

    # ==================================================================================================================
    @assignOrder(0)
    def exploring_area(self, known_map: dict, interest_dictionary: dict, position=None) -> dict:
        w = self.weights[getattr(self.exploring_area, "order")]
        self.tokens = {key: w * (1 / (known_map[key] + 1) - 0.1) for key in known_map.keys()}
        return self.tokens

    @assignOrder(1)
    def verifying_poi(self, known_map: dict, interest_dictionary: dict, position=None) -> dict:
        w = self.weights[getattr(self.verifying_poi, "order")]
        tokens = {}
        for key in known_map.keys():
            if key in interest_dictionary.keys():
                number_of_measurements = (interest_dictionary[key]['detected'] + interest_dictionary[key]['verified'] +
                                          interest_dictionary[key]['rejected'] + interest_dictionary[key]['potential'])
                if interest_dictionary[key]['detected'] > 0 and \
                   interest_dictionary[key]['rejected'] == 0 and \
                   interest_dictionary[key]['verified'] == 0:
                    tokens[key] = w * 1 / number_of_measurements
            else:
                tokens[key] = 0
        c = Counter(self.tokens)
        c.update(Counter(tokens))
        self.tokens = dict(c)
        return self.tokens

    @assignOrder(2)
    def checking_potential_poi(self, known_map: dict, interest_dictionary: dict, position=None) -> dict:
        w = self.weights[getattr(self.checking_potential_poi, "order")]
        tokens = {}
        for key in known_map.keys():
            if key in interest_dictionary.keys():
                number_of_measurements = (interest_dictionary[key]['detected'] + interest_dictionary[key]['verified'] +
                                          interest_dictionary[key]['rejected'] + interest_dictionary[key]['potential'])
                if interest_dictionary[key]['potential'] > 0 and \
                   interest_dictionary[key]['rejected'] == 0 and \
                   interest_dictionary[key]['verified'] == 0:
                    tokens[key] = w * 1 / number_of_measurements
            else:
                tokens[key] = 0
        c = Counter(self.tokens)
        c.update(Counter(tokens))
        self.tokens = dict(c)
        return self.tokens

    @assignOrder(3)
    def resolve_poi(self, known_map: dict, interest_dictionary: dict, position=None) -> dict:
        w = self.weights[getattr(self.resolve_poi, "order")]
        tokens = {}
        for key in known_map.keys():
            if key in interest_dictionary.keys():
                number_of_measurements = (interest_dictionary[key]['detected'] + interest_dictionary[key]['verified'] +
                                          interest_dictionary[key]['rejected'] + interest_dictionary[key]['potential'])
                ratio_confirming = (interest_dictionary[key]['detected'] +
                                    interest_dictionary[key]['verified']) / number_of_measurements
                tokens[key] = w * 4 * ratio_confirming * (1 - ratio_confirming) / number_of_measurements
            else:
                tokens[key] = 0
        c = Counter(self.tokens)
        c.update(Counter(tokens))
        self.tokens = dict(c)
        return self.tokens

    @assignOrder(4)
    def density(self, known_map: dict, interest_dictionary: dict, position=None) -> dict:
        w = self.weights[getattr(self.density, "order")]
        size = (max([key[0] for key in self.tokens.keys()]), max([key[1] for key in self.tokens.keys()]))
        arr = np.zeros(size)
        for key in self.tokens.keys():
            i = key[0]
            j = key[1]
            arr[i-1,j-1] = self.tokens[i, j]

        l = 5  # size of the kernel
        sig = 1  # the size of the blur

        ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
        gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
        kernel = np.outer(gauss, gauss)
        kernel /= np.sum(kernel)  # normalized

        arr = w*ndimage.convolve(arr, kernel)

        tokens = {}
        for i in range(len(arr)):
            for j in range(len(arr[i])):
                tokens[(i+1, j+1)] = arr[i, j]

        c = Counter(self.tokens)
        c.update(Counter(tokens))
        self.tokens = dict(c)
        return self.tokens

    @assignOrder(5)
    def distance(self, known_map: dict, interest_dictionary: dict, position) -> dict:
        w = self.weights[getattr(self.distance, "order")]
        tokens = {}
        for key in self.tokens.keys():
            distance = ((key[0] - position[0])**2 + (key[1] - position[1])**2)**0.5
            tokens[key] = self.tokens[key] * w**distance
        self.tokens = tokens
        return self.tokens

    # ==================================================================================================================
    def set_weights(self, weights) -> None:
        self.weights = weights

    def get_functions(self) -> list:
        return sorted([getattr(self, field) for field in dir(self) if hasattr(getattr(self, field), "order")],
                       key=(lambda field: field.order))

