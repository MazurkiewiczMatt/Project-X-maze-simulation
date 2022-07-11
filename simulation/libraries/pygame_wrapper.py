import pygame


def calculate_GUI_scale(screen: pygame.Surface, settings: dict):
    """
    Calculate the scale for the maze, and offsets for the (1, 1) point.

    Parameters
    ----------
    screen : pygame.Surface
        The surface on which the maze will be drawn.
    settings : dict
        Dictionary with video settings.

    Returns
    -------
    (offset_x, offset_y) : tuple
        Pixel values for offsets of (1, 1) point of the maze
    g_size : float
        Scale of the maze.

    """
    size = screen.get_size()
    width = size[0] - 2 * settings['margin']
    height = size[1] - 2 * settings['margin'] - settings['GUI_bar']
    grid_wide = settings['grid_shape'][1]
    grid_high = settings['grid_shape'][0]
    g_size = min(width // grid_wide, height // grid_high)
    offset_x = (size[0] - g_size * grid_wide) // 2
    offset_y = (size[1] - g_size * grid_high+ settings['GUI_bar']) // 2
    return (offset_x, offset_y), g_size


def draw_GUI(screen: pygame.Surface, s, selected_agent, show_tokens, settings: dict) -> None:
    margin = 8
    res = screen.get_size()
    GUI_box = (margin, margin), (res[0]-2*margin, settings['GUI_bar']-2*margin)
    # draw the outline around the GUI
    pygame.draw.rect(screen, settings['color'], GUI_box, width=1)
    # write text
    GUI_font = pygame.font.SysFont("Courier New", 20)
    GUI_subfont = pygame.font.SysFont("Courier New", 15)
    if selected_agent == 0:
        mode_text_content = 'View: System overview'
        desc_text_content = "Press '1' through '5' to select agent"
    else:
        mode_text_content = 'View: Agents[' + str(selected_agent) + ']'
        desc_text_content = "Press '0' for system overview, 't' for toggle token heatmap"
        if show_tokens:
            mode_text_content += '(token heatmap)'
    mode_text = GUI_font.render(mode_text_content, False, settings['color'])
    desc_text = GUI_subfont.render(desc_text_content, False, settings['color'])
    u_text = GUI_font.render("Press 'u' to update", False, settings['color'])
    screen.blit(mode_text, (4 * margin, margin + (settings['GUI_bar'] - 2 * margin) // 4 - 10))
    screen.blit(desc_text, (4 * margin, margin + 2.5 * (settings['GUI_bar'] - 2 * margin) // 4 - 7.5))
    screen.blit(u_text, (res[0]-2*margin-250, margin + 2*(settings['GUI_bar'] - 2 * margin) // 4 - 10))


def draw_cell_walls(screen: pygame.Surface, cell: tuple, cell_walls: dict, settings: dict):
    if not cell_walls['N']:
        pygame.draw.line(screen, settings['color'],
                         (settings['offset'][0] + settings['g_size'] * (cell[1] - 1),
                          settings['offset'][1] + settings['g_size'] * (cell[0] - 1)),
                         (settings['offset'][0] + settings['g_size'] * (cell[1]),
                          settings['offset'][1] + settings['g_size'] * (cell[0] - 1)))
    if not cell_walls['S']:
        pygame.draw.line(screen, settings['color'],
                         (settings['offset'][0] + settings['g_size'] * (cell[1] - 1),
                          settings['offset'][1] + settings['g_size'] * (cell[0])),
                         (settings['offset'][0] + settings['g_size'] * (cell[1]),
                          settings['offset'][1] + settings['g_size'] * (cell[0])))
    if not cell_walls['W']:
        pygame.draw.line(screen, settings['color'],
                         (settings['offset'][0] + settings['g_size'] * (cell[1] - 1),
                          settings['offset'][1] + settings['g_size'] * (cell[0])),
                         (settings['offset'][0] + settings['g_size'] * (cell[1] - 1),
                          settings['offset'][1] + settings['g_size'] * (cell[0] - 1)))
    if not cell_walls['E']:
        pygame.draw.line(screen, settings['color'],
                         (settings['offset'][0] + settings['g_size'] * (cell[1]),
                          settings['offset'][1] + settings['g_size'] * (cell[0])),
                         (settings['offset'][0] + settings['g_size'] * (cell[1]),
                          settings['offset'][1] + settings['g_size'] * (cell[0] - 1)))


def draw_known_map(screen: pygame.Surface, known_map: dict, settings: dict) -> None:
    """
    Draw a known_map of an AgentMap (consult AgentMap Class for more information) onto the pygame surface

    Parameters
    ----------
    screen : pygame.Surface
        The surface on which the known map will be drawn.
    known_map : dict
        A dictionary with keys being amaze.maze.grid entries, with values representing how many times was the square
        visited.
    settings : dict
        Dictionary with video settings.

    """
    for key in known_map.keys():
        if known_map[key] == 0:  # if the cell is unexplored
            pygame.draw.rect(screen, settings['unknown_color'],
                             ((settings['offset'][0] + settings['g_size'] * (key[1] - 1),
                               settings['offset'][1] + settings['g_size'] * (key[0] - 1)),
                              (settings['g_size'], settings['g_size'])), width=0)


def draw_token_map(screen: pygame.Surface, token_map: dict, settings: dict) -> None:
    """
    Draw a known_map of an AgentMap (consult AgentMap Class for more information) onto the pygame surface

    Parameters
    ----------
    screen : pygame.Surface
        The surface on which the known map will be drawn.
    known_map : dict
        A dictionary with keys being amaze.maze.grid entries, with values representing token value of visiting the cell.
    settings : dict
        Dictionary with video settings.

    """
    for key in token_map.keys():
        v = (token_map[key]-min(token_map.values()))/(max(token_map.values())-min(token_map.values())+0.01)
        # it's not bulletproof, but adding 0.01 avoids division by zero errors
        c = (int(255*v), 0, int(255*(1-v)))

        pygame.draw.rect(screen, c,
                         ((settings['offset'][0] + settings['g_size'] * (key[1] - 1),
                           settings['offset'][1] + settings['g_size'] * (key[0] - 1)),
                          (settings['g_size'], settings['g_size'])), width=0)


def draw_maze_map(screen: pygame.Surface, maze_map: dict, settings: dict) -> None:
    """
    Draw a maze_map of an AgentMap (consult AgentMap Class for more information) onto the pygame surface

    Parameters
    ----------
    screen : pygame.Surface
        The surface on which the known map will be drawn.
    maze_map : dict
        A dictionary with keys being amaze.maze.grid entries, with values being dictionaries saying whether particular
        direction is accessible (without a wall).
    settings : dict
        Dictionary with video settings.

    """

    # draw the outline around the maze
    pygame.draw.rect(screen, settings['color'], (settings['offset'], (settings['grid_shape'][1] * settings['g_size'],
                                                                      settings['grid_shape'][0] * settings['g_size'])),
                     width=3)

    # draw the walls
    for key in maze_map.keys():
        draw_cell_walls(screen, key, maze_map[key], settings)


def draw_agent(screen: pygame.Surface, agent, settings: dict, active=False, path_on=True):
    """
    Draw an agent onto the pygame surface

    Parameters
    ----------
    screen : pygame.Surface
        The surface on which the known map will be drawn.
    agent : Agent
        An agent object. Consult Agent Class for more information.
    settings : dict
        Dictionary with video settings.
    active : bool
        Whether the agent should be highlighted
    path_on : bool
        Whether the planned path of the agents is drawn

    """
    if active:
        c = settings['color_active']
    else:
        c = settings['color']
    l = agent.agent.position

    if path_on:
        path = agent.chosen_path
        point1 = l
        for move in path:
            if move == 'N':
                point2 = (point1[0], point1[1] - 1)
            if move == 'S':
                point2 = (point1[0], point1[1] + 1)
            if move == 'E':
                point2 = (point1[0] + 1, point1[1])
            if move == 'W':
                point2 = (point1[0] - 1, point1[1])
            pygame.draw.line(screen, (255, 0, 0), (settings['offset'][0] + settings['g_size'] * (point1[0] - 0.5),
                                                   settings['offset'][1] + settings['g_size'] * (point1[1] - 0.5)),
                             (settings['offset'][0] + settings['g_size'] * (point2[0] - 0.5),
                              settings['offset'][1] + settings['g_size'] * (point2[1] - 0.5)))
            point1 = point2

    pygame.draw.circle(screen, c, (settings['offset'][0] + settings['g_size'] * (l[0] - 0.5),
                                   settings['offset'][1] + settings['g_size'] * (l[1] - 0.5)), 0.2 * settings['g_size'])

def draw_points_of_interest(screen: pygame.Surface, interest_map: dict, settings:dict, threshold=5, potential_threshold=4):
    for key in interest_map.keys():
        if interest_map[key] > threshold:
            pygame.draw.circle(screen, (200, 20, 20), (settings['offset'][0] + settings['g_size'] * (key[1] - 0.5),
                                           settings['offset'][1] + settings['g_size'] * (key[0] - 0.5)),
                               0.1 * settings['g_size'])
        elif interest_map[key] > potential_threshold:
            pygame.draw.circle(screen, (100, 100, 20), (settings['offset'][0] + settings['g_size'] * (key[1] - 0.5),
                                           settings['offset'][1] + settings['g_size'] * (key[0] - 0.5)),
                               0.1 * settings['g_size'])


def draw_detected_points_of_interest(screen: pygame.Surface, interest_dictionary: dict, settings: dict):
    PoI_font = pygame.font.SysFont("Courier New", 12)
    for key in interest_dictionary.keys():
        PoI_text_content = str(interest_dictionary[key]['detected'])
        if PoI_text_content != '0':
            PoI_text = PoI_font.render(PoI_text_content, False, (110, 130, 130))
            screen.blit(PoI_text, (settings['offset'][0] + settings['g_size'] * (key[1] - 0.8),
                                               settings['offset'][1] + settings['g_size'] * (key[0] - 0.8)))
        PoI_text_content = str(interest_dictionary[key]['verified'])
        if PoI_text_content != '0':
            PoI_text = PoI_font.render(PoI_text_content, False, (20, 200, 20))
            screen.blit(PoI_text, (settings['offset'][0] + settings['g_size'] * (key[1] - 0.4),
                                   settings['offset'][1] + settings['g_size'] * (key[0] - 0.8)))
        PoI_text_content = str(interest_dictionary[key]['potential'])
        if PoI_text_content != '0':
            PoI_text = PoI_font.render(PoI_text_content, False, (90, 120, 100))
            screen.blit(PoI_text, (settings['offset'][0] + settings['g_size'] * (key[1] - 0.8),
                                   settings['offset'][1] + settings['g_size'] * (key[0] - 0.4)))
        PoI_text_content = str(interest_dictionary[key]['rejected'])
        if PoI_text_content != '0':
            PoI_text = PoI_font.render(PoI_text_content, False, (200, 20, 20))
            screen.blit(PoI_text, (settings['offset'][0] + settings['g_size'] * (key[1] - 0.4),
                                   settings['offset'][1] + settings['g_size'] * (key[0] - 0.4)))
