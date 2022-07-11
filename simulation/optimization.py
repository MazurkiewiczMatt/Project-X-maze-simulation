from numpy.random import randint
from numpy.random import rand
import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def decode(bounds, n_bits, bitstring):
    """
    Decode bitstring to numbers
    :param bounds:    range of inputs
    :param n_bits:    bits per variable
    :param bitstring: encoded bitstring
    :return: decoded outputs
    """
    decoded = list()
    largest = 2 ** n_bits
    for i in range(len(bounds)):
        # extract the substring
        start, end = i * n_bits, (i * n_bits) + n_bits
        substring = bitstring[start:end]
        # convert bitstring to a string of chars
        chars = ''.join([str(s) for s in substring])
        # convert string to integer
        integer = int(chars, 2)
        # scale integer to desired range
        value = bounds[i][0] + (integer / largest) * (bounds[i][1] - bounds[i][0])
        # store
        decoded.append(value)
    return decoded


def selection(pop, scores, k):
    """
    Tournament selection
    :param pop:     current population
    :param scores:  objective function results for p in population
    :param k:       number of selected candidates
    :return:        selected candidates
    """
    # first random selection
    selection_ix = randint(len(pop))
    for ix in randint(0, len(pop), k - 1):
        # check if better (e.g. perform a tournament)
        if scores[ix] < scores[selection_ix]:
            selection_ix = ix
    return pop[selection_ix]


def crossover(p1, p2, r_cross):
    """
    Crossover two parents to generate a child
    :param p1:       bitstring parent 1
    :param p2:       bitstring parent 2
    :param r_cross:  crossover rate
    :return:         bitstring child
    """
    # children are copies of parents by default
    c1, c2 = p1.copy(), p2.copy()
    # check for recombination
    if rand() < r_cross:
        # select crossover point that is not on the end of the string
        pt = randint(1, len(p1) - 2)
        # perform crossover
        c1 = p1[:pt] + p2[pt:]
        c2 = p2[:pt] + p1[pt:]
    return [c1, c2]


def mutation(bitstring, r_mut):
    """
    Mutation operator
    :param bitstring:  mutated bitstring
    :param r_mut:      mutation rate
    :return:
    """
    for i in range(len(bitstring)):
        # check for a mutation
        if rand() < r_mut:
            # flip the bit
            bitstring[i] = 1 - bitstring[i]


def genetic_algorithm(objective, metric, bounds, n_bits, n_iter, n_pop, r_cross, r_mut, k):
    """
    Stochastic genetic optimization algorithm
    :param objective:  objective function to minimize
    :param metric:     metric for objective function
    :param bounds:     boundaries of the inputs
    :param n_bits:     number of bits per input variable
    :param n_iter:     total number of generations
    :param n_pop:      size of the population per iteration
    :param r_cross:    crossover rate
    :param r_mut:      mutation rate
    :param k:          number of selections per population
    :return:
    """
    # initial population of random bitstring
    pop = [randint(0, 2, n_bits*len(bounds)).tolist() for _ in range(n_pop)]
    # keep track of best solution
    best, best_eval = 0, objective(metric, decode(bounds, n_bits, pop[0]))
    # enumerate generations
    for gen in range(n_iter):
        # decode population
        decoded = [decode(bounds, n_bits, p) for p in pop]
        # evaluate all candidates in the population
        scores = [objective(metric, d) for d in decoded]
        # check for new best solution
        for i in range(n_pop):
            if scores[i] < best_eval:
                best, best_eval = pop[i], scores[i]
                logging.info(" > %d, new best f(%s) = %.3f" % (gen,  decode(bounds, n_bits, pop[i]), scores[i]))
        # select parents
        selected = [selection(pop, scores, k) for _ in range(n_pop)]
        # create the next generation
        children = list()
        for i in range(0, n_pop, 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i+1]
            # crossover and mutation
            for c in crossover(p1, p2, r_cross):
                # mutation
                mutation(c, r_mut)
                # store for next generation
                children.append(c)
        # replace population
        pop = children
    logging.info("======= DONE =======")
    decoded = decode(bounds, n_bits, best)
    logging.info('f(%s) = %f' % (decoded, best_eval))
    return [best, best_eval]
