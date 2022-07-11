import unittest
from libraries.pygame_wrapper import calculate_GUI_scale
import pygame


class PygameWrapperTest(unittest.TestCase):
    def test_ledger_update_map(self):
        settings = {'margin': 20, 'grid_shape': (1, 1), 'GUI_bar': 5}
        screen = pygame.display.set_mode((100, 100))
        offset, g_size = calculate_GUI_scale(screen, settings)
        self.assertEqual(55, g_size)
        self.assertEqual((32, 25), offset)


if __name__ == '__main__':
    unittest.main()
