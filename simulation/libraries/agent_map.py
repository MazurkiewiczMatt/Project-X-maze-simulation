from functools import reduce


class AgentMap:
    def __init__(self, id, ground_truth, interest_map, token_fcn, god_mode=False):
        """
        Initialize Agent Map.

        Parameters
        ----------
        ground_truth : pyamaze.maze
            pyamaze maze, with the .grid and .maze_map dictionaries as properties describing the maze layout
        interest_map : dict
            Dictionary, with keys the same as maze_map or known_map (that is a tuple refering to a location in pyamaze
            maze

        """
        self.grid = ground_truth.grid
        self.maze_map = {}
        self.known_map = {}
        self.interest_map = {}
        self.reference_interest_map = interest_map  # AgentMap saves an interest_map from ground truth for reference
        self.dimensions = (ground_truth.rows, ground_truth.cols)
        self.id = id
        self.token_functions = token_fcn

        if not god_mode:
            for element in self.grid:
                # if the drone isn't all knowing
                self.maze_map[element] = {'E': 1, 'W': 1, 'N': 1, 'S': 1}
                self.known_map[element] = 0
                self.interest_map[element] = 0
        else:
            # if it is, set all readings at ground truth
            self.maze_map = ground_truth.maze_map
            self.interest_map = interest_map
            for element in self.grid:
                self.known_map[element] = 1

    def observe(self, ground_truth, location):
        """
        Update AgentMap with a ground truth value at selected location. Increases known_map at this location by 1.

        Parameters
        ----------
        ground_truth : pyamaze.maze
            pyamaze maze, with the .grid and .maze_map dictionaries as properties describing the maze layout
        location : tuple
            Position in the maze, that is, an element of pyamaze.maze.grid, such as (1, 1)

        """
        self.maze_map[location] = ground_truth.maze_map[location]
        self.known_map[location] += 1
        self.interest_map[location] = self.reference_interest_map[location]

    def token_map(self, interest_dictionary, position):
        fcn = self.token_functions.get_functions()
        for f in fcn:
            tokens = f(self.known_map, interest_dictionary, position)
        return tokens
