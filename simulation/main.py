from simulation import Simulation
from libraries.token_functions import TokenFunctions
from interactive_visualization import start_interactive_visualization
import pygame

token_fcn = TokenFunctions()
token_fcn.set_weights([0.5, 0.8, 0.2, 0.2, 0.4, 1])
#token_fcn.set_weights([0.1875, 0.3203125, 0.0546875, 0.55859375, 0.81640625, 0.78125])
grid_shape = (15, 25)
s = Simulation(dimensions=grid_shape, token_fcn=token_fcn)

s.add_agent(1, search_depth=4)
s.add_agent(2, search_depth=4)
s.add_agent(3, search_depth=4)
s.add_agent(4, search_depth=4)

graphics_settings = {'margin': 20, 'color': pygame.Color(255, 255, 255), 'color_active': pygame.Color(50, 255, 255),
                     'unknown_color': pygame.Color(30, 30, 30), 'background_color': pygame.Color(0, 0, 0),
                     'grid_shape': grid_shape, 'GUI_bar': 100}

start_interactive_visualization(s, graphics_settings)

