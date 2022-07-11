from libraries.ledger import Ledger
from libraries.agent_map import AgentMap
import random


class Agent:
    def __init__(self, id, agent, ground_truth, interest_map, map_update_function, token_fcn, god_mode=False, search_depth=5, communication_range=1, point_of_interest_threshold=5, potential_point_of_interest_threshold=4):
        self.id = id
        self.agent = agent
        agent_map = AgentMap(id, ground_truth, interest_map, god_mode=god_mode, token_fcn=token_fcn)
        self.ledger = Ledger(self.id, agent_map, map_update_function)
        self.ground_truth = ground_truth
        self.search_depth = search_depth
        self.chosen_path = ''
        self.time_since_last_receiving = 0
        self.local_time = 0
        self.communication_range = communication_range
        self.point_of_interest_threshold = point_of_interest_threshold
        self.potential_point_of_interest_threshold = potential_point_of_interest_threshold

    def observe_spot(self, location):
        agent_map = self.ledger.map
        agent_map.observe(self.ground_truth, location)
        self.ledger.update_map(lambda x: agent_map, time=self.local_time)

    def observe(self):
        loc = self.agent.position
        locs = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                n_loc = (loc[1] + i, loc[0] + j)
                if 0 < n_loc[0] <= self.ground_truth.rows and 0 < n_loc[1] <= self.ground_truth.cols:
                    locs.append(n_loc)
        found_points_of_interest = [self.ledger.ledger[key][1]['point'] for key in self.ledger.ledger.keys() if ("Detected point of interest" in self.ledger.ledger[key][0] or "Detected potential point of interest" in self.ledger.ledger[key][0]) and self.ledger.ledger[key][1]['observer'] != self.id]
        for l in locs:
            self.observe_spot(l)
            observed_value = self.ledger.map.interest_map[l] + (random.random()-0.5)*2
            if l in found_points_of_interest:
                if observed_value > self.point_of_interest_threshold:
                    self.ledger.add_block(self.ledger.current_block, "Verified point of interest at (" + str(l[0]) + ", " +
                                          str(l[1]) + ")", {'point': l, 'observer': self.id, 'time': self.local_time,
                                                            'value': self.ledger.map.interest_map[l]})
                else:
                    self.ledger.add_block(self.ledger.current_block, "Didn't detect point of interest at (" + str(l[0]) + ", " +
                                          str(l[1]) + ")", {'point': l, 'observer': self.id, 'time': self.local_time,
                                                            'value': self.ledger.map.interest_map[l]})
            else:
                if observed_value > self.point_of_interest_threshold:
                    self.ledger.add_block(self.ledger.current_block, "Detected point of interest at (" + str(l[0]) + ", " +
                                          str(l[1]) + ")", {'point': l, 'observer': self.id, 'time': self.local_time,
                                                            'value': self.ledger.map.interest_map[l]})
                elif observed_value > self.potential_point_of_interest_threshold:
                    self.ledger.add_block(self.ledger.current_block, "Detected potential point of interest at (" + str(l[0]) + ", " +
                                          str(l[1]) + ")", {'point': l, 'observer': self.id, 'time': self.local_time,
                                                            'value': self.ledger.map.interest_map[l]})

    def update(self):
        self.local_time += 1
        self.time_since_last_receiving += 1
        if self.chosen_path == '':
            token_map = self.ledger.map.token_map(self.ledger.points_of_interest(observer_to_skip = self.id), self.agent.position)
            moves = self.generate_n_moves(token_map, n=5, m=self.search_depth)
            best_move = ''
            best_score = -100
            for key in moves.keys():
                if moves[key][0] > best_score:
                    best_move = key
                    best_score = moves[key][0]
            self.chosen_path = best_move

        best_move = self.chosen_path
        if best_move != '':
            move = best_move[0]

            if move == 'N' and self.agent.position[1]>1:
                self.agent.position = (self.agent.position[0], self.agent.position[1] - 1)
            if move == 'S' and self.agent.position[1]<self.ledger.map.dimensions[0]:
                self.agent.position = (self.agent.position[0], self.agent.position[1] + 1)
            if move == 'E' and self.agent.position[0]<self.ledger.map.dimensions[1]:
                self.agent.position = (self.agent.position[0] + 1, self.agent.position[1])
            if move == 'W'  and self.agent.position[0]>1:
                self.agent.position = (self.agent.position[0] - 1, self.agent.position[1])

        self.observe()

        token_map = self.ledger.map.token_map(self.ledger.points_of_interest(observer_to_skip = self.id), self.agent.position)
        moves = self.generate_n_moves(token_map, n=5, m=self.search_depth)
        best_move = ''
        best_score = -100
        for key in moves.keys():
            if moves[key][0] > best_score:
                best_move = key
                best_score = moves[key][0]
        self.chosen_path = best_move

    def broadcast(self, agents):
        position = self.agent.position
        for agent in agents.keys():
            if not (agents[agent].id == self.id):
                l = agents[agent].agent.position
                if l[0] - self.communication_range <= position[0] <= l[0] + self.communication_range and l[1] - self.communication_range <= position[1] <= l[1] + self.communication_range:
                    agents[agent].ledger.receive(self.ledger, time=self.local_time)
                    agents[agent].time_since_last_receiving = 0

                    my_map = self.ledger.map.known_map
                    their_map = agents[agent].ledger.map.known_map

                    for spot in my_map.keys():
                        if my_map[spot] > their_map[spot]:
                            agents[agent].ledger.map.maze_map[spot] = self.ledger.map.maze_map[spot]
                            agents[agent].ledger.map.known_map[spot] = self.ledger.map.known_map[spot]

    def generate_n_moves(self, token_map, n=1, m=1, prefix='', starting_position=None, value=0):
        if starting_position is None:
            starting_position = (self.agent.position[1], self.agent.position[0])
        moves = {}
        for key in self.ledger.map.maze_map[starting_position].keys():
            if self.ledger.map.maze_map[starting_position][key] == 1:
                sequence = prefix + key
                new_position = starting_position
                if key == 'N':
                    if starting_position[0] > 1:
                        new_position = (starting_position[0] - 1, starting_position[1])
                elif key == 'S':
                    if starting_position[0] < self.ledger.map.dimensions[0]:
                        new_position = (starting_position[0] + 1, starting_position[1])
                elif key == 'E':
                    if starting_position[1] < self.ledger.map.dimensions[1]:
                        new_position = (starting_position[0], starting_position[1] + 1)
                elif key == 'W':
                    if starting_position[1] > 1:
                        new_position = (starting_position[0], starting_position[1] - 1)
                v = value + token_map[new_position]
                if n > 1:
                    next_moves = self.generate_n_moves(token_map, n=n - 1, prefix=sequence,
                                                       starting_position=new_position, value=v)
                else:
                    next_moves = {sequence: (v, new_position)}
                moves.update(next_moves)
        if m > 1:
            best_N = ''
            best_N_score = -100
            best_E = ''
            best_E_score = -100
            best_W = ''
            best_W_score = -100
            best_S = ''
            best_S_score = -100
            for move in moves.keys():
                if move[0] == 'N':
                    if moves[move][0] > best_N_score or best_N == '':
                        best_N = move
                        best_N_score = moves[move][0]
                        best_N_starting_position = moves[move][1]
                if move[0] == 'E':
                    if moves[move][0] > best_E_score or best_E == '':
                        best_E = move
                        best_E_score = moves[move][0]
                        best_E_starting_position = moves[move][1]
                if move[0] == 'W':
                    if moves[move][0] > best_W_score or best_W == '':
                        best_W = move
                        best_W_score = moves[move][0]
                        best_W_starting_position = moves[move][1]
                if move[0] == 'S':
                    if moves[move][0] > best_S_score or best_S == '':
                        best_S = move
                        best_S_score = moves[move][0]
                        best_S_starting_position = moves[move][1]
            best_moves = []
            if best_N != '':
                best_moves.append((best_N, best_N_score, best_N_starting_position))
            if best_E != '':
                best_moves.append((best_E, best_E_score, best_E_starting_position))
            if best_W != '':
                best_moves.append((best_W, best_W_score, best_W_starting_position))
            if best_S != '':
                best_moves.append((best_S, best_S_score, best_S_starting_position))
            moves = {}
            for move in best_moves:
                sub_moves = self.generate_n_moves(token_map, n=n, m=m-1, prefix=move[0],
                                                       starting_position=move[2], value=move[1])
                moves.update(sub_moves)

        return moves
