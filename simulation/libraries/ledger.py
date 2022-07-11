import random
import string
from typing import Any


def random_key() -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))


class Ledger:
    def __init__(self, id, default_map, map_update_function):
        self.id: str = id
        self.ledger: dict = {}
        self.map = default_map
        self.map_update_function = map_update_function
        self.current_block = self.add_block([], "Mission start")

    def add_block(self, last_keys, content: Any, metadata: dict = {}):
        """ Add a block to the ledger """
        key = random_key()
        self.ledger[key] = (content, metadata, last_keys)
        return key

    def receive(self, r_ledger, time) -> None:
        """ Update the ledger with another ledger """
        self.ledger.update(r_ledger.ledger)
        self.current_block = self.add_block([self.current_block, r_ledger.current_block], "Broadcast received",
                                            {'broadcaster': r_ledger.id, 'time': time})
        self.map = self.map_update_function(self.map, r_ledger.map)

    def update_map(self, observation, time) -> None:
        """ Update the map with an observation """
        # self.current_block = self.add_block([self.current_block], "Map updated", {'agent': self.name, 'time': time})
        self.map = observation(self.map)

    def points_of_interest(self, observer_to_skip = False):
        points_of_interest = {}
        for key in self.ledger.keys():
            if "Detected point of interest" in self.ledger[key][0]:
                if observer_to_skip == False or self.ledger[key][1]['observer'] != observer_to_skip:  # don't count my own detections, since I can't verify them anyway
                    if self.ledger[key][1]['point'] in points_of_interest.keys():
                        points_of_interest[self.ledger[key][1]['point']]['detected'] += 1
                    else:
                        points_of_interest[self.ledger[key][1]['point']] = {'detected': 1, 'verified': 0, 'rejected': 0, 'potential': 0}
            elif "Detected potential point of interest" in self.ledger[key][0]:
                if observer_to_skip == False or self.ledger[key][1]['observer'] != observer_to_skip:  # don't count my own detections, since I can't verify them anyway
                    if self.ledger[key][1]['point'] in points_of_interest.keys():
                        points_of_interest[self.ledger[key][1]['point']]['potential'] += 1
                    else:
                        points_of_interest[self.ledger[key][1]['point']] = {'detected': 0, 'verified': 0, 'rejected': 0,
                                                                            'potential': 1}
            elif "Verified point of interest" in self.ledger[key][0]:
                if self.ledger[key][1]['point'] in points_of_interest.keys():
                    points_of_interest[self.ledger[key][1]['point']]['verified'] += 1
                else:
                    points_of_interest[self.ledger[key][1]['point']] = {'detected': 0, 'verified': 1, 'rejected': 0, 'potential': 0}
            elif "Didn't detect point of interest" in self.ledger[key][0]:
                if self.ledger[key][1]['point'] in points_of_interest.keys():
                    points_of_interest[self.ledger[key][1]['point']]['rejected'] += 1
                else:
                    points_of_interest[self.ledger[key][1]['point']] = {'detected': 0, 'verified': 0, 'rejected': 1, 'potential': 0}
        return points_of_interest

