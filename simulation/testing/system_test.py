import unittest
from simulation import Simulation
from libraries.token_functions import TokenFunctions


class SystemTest(unittest.TestCase):
    def test_simulation(self):
        '''
        Runs the simulation 5 times for 10 steps, and checks whether at least 10 cell measurements were made.
        '''
        for i in range(5):
            token_fcn = TokenFunctions()
            token_fcn.set_weights([0.5, 0.8, 0.2, 0.2, 0.4, 1])
            grid_shape = (15, 25)
            s = Simulation(dimensions=grid_shape, token_fcn=token_fcn)
            s.add_agent(1, search_depth=4)

            for i in range(10):
                s.update()
            known_map = s.agents[1].ledger.map.known_map
            explored_cells = sum([known_map[key] for key in known_map.keys()])
            self.assertTrue(explored_cells > 10)


if __name__ == '__main__':
    unittest.main()
