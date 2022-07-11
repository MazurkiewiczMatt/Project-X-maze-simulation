from pyamaze import maze, agent
from libraries.token_functions import TokenFunctions
import numpy as np
from libraries.agent import Agent
import random


class Simulation:
    def __init__(self, dimensions: tuple, token_fcn: TokenFunctions, loops: float = 1, enable_keys: bool = True, map_mode='maze'):
        """
        Create a 2D maze
        :param dimensions: tuple with two elements
        :param loops     : complexity, between 0 and 1
        """
        self.m = maze(dimensions[0], dimensions[1])
        self.m.CreateMaze(loopPercent=loops)
        if map_mode == 'maze':
            pass
        elif map_mode == 'field':
            for key in self.m.maze_map.keys():
                boundaries = {'E': 1, 'W': 1, 'N': 1, 'S': 1}
                if key[0] == 1:
                    boundaries['N'] = 0
                if key[0] == dimensions[0]:
                    boundaries['S'] = 0
                if key[1] == 1:
                    boundaries['W'] = 0
                if key[1] == dimensions[1]:
                    boundaries['E'] = 0
                self.m.maze_map[key] = boundaries
        else:
            raise ValueError

        self.agents = {}
        self.dimensions = dimensions
        self.enable_keys = enable_keys
        self.time = 0
        self.token_fcn = token_fcn

        self.communication_range = 5

        self.interest_map = {}
        for point in self.m.grid:
            self.interest_map[point] = random.random()*10

        self.interest_threshold = 9.2
        self.potential_interest_threshold = 8.2

    def start_maze(self) -> None:
        """ Obsolete, runs the simulation in tkinter """
        self.m.run()

    def random_position(self):
        """ Returns a random position on the maze """
        return [np.random.randint(1, self.dimensions[1] + 1),
         np.random.randint(1, self.dimensions[0] + 1)]

    def add_agent(self, id, pos=None, search_depth=5) -> None:
        if id not in self.agents.keys():
            if pos is None:
                pos = self.random_position()
            self.agents[id] = Agent(id, agent(self.m), self.m, self.interest_map, lambda x, y: x,
                                    search_depth=search_depth,
                                    communication_range=self.communication_range,
                                    point_of_interest_threshold=self.interest_threshold,
                                    potential_point_of_interest_threshold=self.potential_interest_threshold,
                                    token_fcn = self.token_fcn)
            self.agents[id].agent.position = pos
            if self.enable_keys:  # for start_maze visualization in tkinter
                self.m.enableArrowKey(self.agents[id].agent)

    def update(self):
        for agent in self.agents.keys():
            self.agents[agent].update()
            self.agents[agent].broadcast(self.agents)
            self.time += 1
