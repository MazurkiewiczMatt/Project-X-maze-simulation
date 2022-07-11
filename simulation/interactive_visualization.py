import pygame
import sys
from libraries.pygame_wrapper import calculate_GUI_scale, draw_known_map, draw_agent, draw_maze_map, draw_token_map, draw_GUI, draw_points_of_interest, draw_detected_points_of_interest


def start_interactive_visualization(s, settings: dict):
    pygame.init()

    fps = 60
    fpsClock = pygame.time.Clock()

    width, height = 1000, 650
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    drawn_maze = s.m.maze_map
    selected_agent = 0
    show_tokens = False

    while True:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # select agent
                if event.key == pygame.K_0:
                    selected_agent = 0
                    drawn_maze = s.m.maze_map
                if event.key == pygame.K_1:
                    if 1 in s.agents.keys():
                        selected_agent = 1
                        drawn_maze = s.agents[1].ledger.map.maze_map
                if event.key == pygame.K_2:
                    if 2 in s.agents.keys():
                        selected_agent = 2
                        drawn_maze = s.agents[2].ledger.map.maze_map
                if event.key == pygame.K_3:
                    if 3 in s.agents.keys():
                        selected_agent = 3
                        drawn_maze = s.agents[3].ledger.map.maze_map
                if event.key == pygame.K_4:
                    if 4 in s.agents.keys():
                        selected_agent = 4
                        drawn_maze = s.agents[4].ledger.map.maze_map
                if event.key == pygame.K_5:
                    if 5 in s.agents.keys():
                        selected_agent = 5
                        drawn_maze = s.agents[5].ledger.map.maze_map
                # movement of selected drone
                """
                if event.key == pygame.K_RIGHT:
                    if not (selected_agent == 0) and (selected_agent in s.agents.keys()):
                        l = s.agents[selected_agent].agent.position
                        if (1 <= l[0] < settings['grid_shape'][1]) and s.m.maze_map[(l[1], l[0])]['E']:
                            s.agents[selected_agent].agent.position = (l[0] + 1, l[1])
                if event.key == pygame.K_LEFT:
                    if not (selected_agent == 0) and (selected_agent in s.agents.keys()):
                        l = s.agents[selected_agent].agent.position
                        if (1 < l[0] <= settings['grid_shape'][1]) and s.m.maze_map[(l[1], l[0])]['W']:
                            s.agents[selected_agent].agent.position = (l[0] - 1, l[1])
                if event.key == pygame.K_UP:
                    if not (selected_agent == 0) and (selected_agent in s.agents.keys()):
                        l = s.agents[selected_agent].agent.position
                        if (1 < l[1] <= settings['grid_shape'][0]) and s.m.maze_map[(l[1], l[0])]['N']:
                            s.agents[selected_agent].agent.position = (l[0], l[1] - 1)
                if event.key == pygame.K_DOWN:
                    if not (selected_agent == 0) and (selected_agent in s.agents.keys()):
                        l = s.agents[selected_agent].agent.position
                        if (1 <= l[1] < settings['grid_shape'][0]) and s.m.maze_map[(l[1], l[0])]['S']:
                            s.agents[selected_agent].agent.position = (l[0], l[1] + 1)
                """
                # debugging tools
                if event.key == pygame.K_b:
                    if not (selected_agent == 0) and (selected_agent in s.agents.keys()):
                        print(s.agents[selected_agent].ledger.ledger)
                if event.key == pygame.K_n:
                    if not (selected_agent == 0) and (selected_agent in s.agents.keys()):
                        print(s.agents[selected_agent].chosen_path)
                # visualizations
                if event.key == pygame.K_t:
                    if not (selected_agent == 0) and (selected_agent in s.agents.keys()):
                        show_tokens = not(show_tokens)
                # update
                if event.key == pygame.K_u:
                    s.update()

        # calculate scale for the visualization, in case the window size changes
        offset, g_size = calculate_GUI_scale(screen, settings)
        settings['offset'] = offset
        settings['g_size'] = g_size

        if not (selected_agent == 0):
            draw_known_map(screen, s.agents[selected_agent].ledger.map.known_map, settings)
            if show_tokens:
                draw_token_map(screen, s.agents[selected_agent].ledger.map.token_map(
                    s.agents[selected_agent].ledger.points_of_interest(observer_to_skip = selected_agent), s.agents[selected_agent].agent.position), settings)
        draw_maze_map(screen, drawn_maze, settings)
        for agent in s.agents.keys():
            draw_agent(screen, s.agents[agent], settings, active=(agent == selected_agent), path_on=True)
        if selected_agent == 0:
            draw_points_of_interest(screen, s.interest_map, settings, threshold=s.interest_threshold, potential_threshold=s.potential_interest_threshold)
        else:
            draw_detected_points_of_interest(screen, s.agents[selected_agent].ledger.points_of_interest(), settings)
        draw_GUI(screen, s, selected_agent, show_tokens, settings)

        pygame.display.flip()
        fpsClock.tick(fps)
