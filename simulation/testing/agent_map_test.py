import unittest
from libraries.agent_map import AgentMap
from libraries.token_functions import TokenFunctions
import pyamaze
import random


class AgentMapTest(unittest.TestCase):
    def test_initialization(self):
        m = pyamaze.maze(5, 5)
        m.CreateMaze()
        interest_map = {}
        for point in m.grid:
            interest_map[point] = random.random() * 10
        try:
            agent_map = AgentMap(0, m, interest_map, TokenFunctions())
        except Exception:
            self.fail("ERROR: unable to initialize an Agent Map object")

if __name__ == '__main__':
    unittest.main()