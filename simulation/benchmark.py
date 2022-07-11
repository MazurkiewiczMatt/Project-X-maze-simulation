from simulation import Simulation
from libraries.token_functions import TokenFunctions
from optimization import genetic_algorithm


def coverage_metric(s):
    """
        Map exploration coverage per drone at a time step
    """
    score = 0
    for i in s.agents.keys():
        known_map = s.agents[i].ledger.map.known_map
        explored_cells = sum([1 for key in known_map.keys() if known_map[key] > 0])
        score += explored_cells
    return score/(len(s.agents.keys())*len(known_map.keys()))


def poi_metric(s):
    """
        Map point of interest exploration per drone at a time step (percentage of point of interests)
    """
    score = 0
    pois = 0
    for i in s.agents.keys():
        agent_poi = s.agents[i].ledger.points_of_interest(observer_to_skip=i)
        for key in s.interest_map:
            if s.interest_map[key] > s.interest_threshold:
                pois += 1
                if key in agent_poi.keys():
                    if agent_poi[key]['verified'] > agent_poi[key]['rejected']:
                        score += 1
                    elif agent_poi[key]['detected'] > 0:
                        score -= 0.5
                    else:
                        score -= 1
                else:
                    score -= 1
    return score/(len(s.agents.keys())*pois + 1)


def benchmark(metric, weights, runs=1, runtime=12, grid_shape=(15, 15), agents=4, search_depth=3):
    """ Benchmarks the system's behavior according to some specified metric """
    scores = []
    token_fcn = TokenFunctions(weights)
    for i in range(runs):
        s = Simulation(dimensions=grid_shape, token_fcn=token_fcn, map_mode='field')
        for j in range(agents):
            s.add_agent(j+1, search_depth=search_depth)
        for k in range(runtime):
            s.update()
        scores.append(metric(s))
    return -sum(scores)/len(scores)


metric = coverage_metric
n_token_fcn = len(TokenFunctions().get_functions())
bounds = []
for n in range(n_token_fcn):
    bounds.append([0, 1])
n_bits = 8
n_iter = 10
n_pop = 10
r_cross = 0.8
r_mut = 1.0 / (float(n_bits) * n_token_fcn)
k = 7


[best, score] = genetic_algorithm(benchmark, metric, bounds, n_bits, n_iter, n_pop, r_cross, r_mut, k)

