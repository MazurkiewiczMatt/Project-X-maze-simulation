import unittest
import numpy as np
from libraries.ledger import Ledger


class LedgerTest(unittest.TestCase):
    def test_ledger_update_map(self):
        average = lambda x, y: np.average([x, y], axis=0).tolist()
        ledger1 = Ledger('ledger1', [0, 0, 0, 0], average)
        self.assertEqual(ledger1.map, [0, 0, 0, 0])
        ledger1.update_map(lambda x: [1, 1, 1, 1], time=0)
        self.assertEqual(ledger1.map, [1, 1, 1, 1])

    def test_ledger_synchronization(self):
        average = lambda x, y: np.average([x, y], axis=0).tolist()
        ledger1 = Ledger('ledger1', [0, 0, 0, 0], average)
        ledger2 = Ledger('ledger2', [0, 0, 0, 0], average)
        ledger1.update_map(lambda x: [1, 1, 1, 1], time=0)
        ledger2.receive(ledger1, time=0)
        self.assertEqual(ledger2.map, [0.5, 0.5, 0.5, 0.5])
        self.assertEqual(ledger2.ledger[ledger2.current_block][0], "Broadcast received")
        preceding_blocks = ledger2.ledger[ledger2.current_block][2]
        self.assertEqual(len(preceding_blocks), 2)


if __name__ == '__main__':
    unittest.main()
