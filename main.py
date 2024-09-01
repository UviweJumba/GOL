# main.py

import pygame
from pygame.locals import *
from multiprocessing import Pool
from multiprocessing import Process
from threading import Thread
import numpy as np
from game_logic import CompetitiveGameOfLife
from BoidIntegrator import BoidIntegrator as BI
from Projectile import Projectile

class Game:
    def __init__(self, width=50, height=50, cell_size=10):
        """
        Initialize the Pygame window and game state.
        
        Parameters:
            width (int): The width of the grid.
            height (int): The height of the grid.
            cell_size (int): The size of each cell in pixels.
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen = pygame.display.set_mode((width * cell_size, height * cell_size))
        pygame.display.set_caption("Competitive Game of Life")
        self.clock = pygame.time.Clock()
        self.game = CompetitiveGameOfLife(width=width, height=height)
        self.current_cell_type = 1  # Start with the first cell type (1)
        self.running = True
        self.paused = True

        self.show_boids = False

        self.player = Player(self.screen, (243, 45, 81), np.array([0.0, 0.0])) #width/2, height/2
        self.p_ddot = np.zeros((2))

        self.flock_p = BI(self.screen, self.player.x)
        self.flock_e = BI(self.screen, np.array([width+100, height+200]), col=(0,0,255))

        self.group_fire = True

        self.bullets = []

    def handle_events(self):
        """
        Handle user input events like key presses and mouse clicks.
        """

        keys = pygame.key.get_pressed()
        self.p_ddot = np.array([ (-keys[K_a] or keys[K_d]) , (-keys[K_w] or keys[K_s]) ])  * 500
        # print("acc = ", self.p_ddot)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    print("zero")
                    self.current_cell_type = 0
                elif event.key == pygame.K_1:
                    self.current_cell_type = 1
                elif event.key == pygame.K_2:
                    self.current_cell_type = 2
                elif event.key == pygame.K_3:
                    self.current_cell_type = 3
                elif event.key == pygame.K_4:
                    self.current_cell_type = 4
                elif event.key == pygame.K_r:
                    self.game.reset_grid()
                elif event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_e:
                    x = ( self.player.x[0] ) // self.cell_size
                    y = ( self.player.x[1] ) // self.cell_size

                    x = int(x)
                    y = int(y)

                    print("x= ",x)

                    if self.game.grid[int(y), int(x)] == 0:    
                        self.game.place_cell(x, y, self.current_cell_type)

                    elif self.game.grid[int(y), int(x)] == self.current_cell_type:
                        self.game.remove_cell(x, y)
                    
                    elif self.game.grid[int(y), int(x)] != 0:
                        pass
                
                elif event.key == pygame.K_SPACE:
                    if self.group_fire:
                        for i in range(0, self.flock_p.X.shape[0]):
                            self.bullets.append(Projectile(self.screen, self.flock_p.X[i].copy(), self.flock_p.X_dot[i].copy()))
                            self.bullets.append(Projectile(self.screen, self.player.x.copy(), self.player.x_dot.copy()))
                    else:
                        self.bullets.append(Projectile(self.screen, self.player.x.copy(), self.player.x_dot.copy()))


            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                x, y = pygame.mouse.get_pos()
                x //= self.cell_size
                y //= self.cell_size

                self.game.place_cell(x, y, self.current_cell_type)

                # if self.game.grid[y, x] == 0:    
                #     self.game.place_cell(x, y, self.current_cell_type)

                
                # elif self.game.grid[y, x] != self.current_cell_type:
                #     pass

            if pygame.mouse.get_pressed()[1]:  # Left mouse button
                print("Right click")
                x, y = pygame.mouse.get_pos()
                x //= self.cell_size
                y //= self.cell_size

                if self.game.grid[y, x] == self.current_cell_type:
                    self.game.remove_cell(x, y)
                
                elif self.game.grid[y, x] != self.current_cell_type:
                    pass

    def update(self):
        """
        Update the game state if the game is not paused.
        """

        player_proc = Thread(target=self.player.update, args=(1/30, self.p_ddot))
        flockp_proc = Thread(target=self.flock_p.update, args=(1/30, self.player.x))
        flocke_proc = Thread(target=self.flock_e.update, args=(1/30, None))
        board_proc = Thread(target=self.game.update_grid, args=(self.paused,))

        # if self.show_boids:

        #     player_proc.start()
        #     flockp_proc.start()
        #     flocke_proc.start()
        # else:
        board_proc.start()
        

        # for b in self.bullets:
        #     b.update()

        #     if b.life_time == 0:
        #         self.bullets.pop(self.bullets.index(b))
        #         del b
        
        # print(len(self.bullets))

    
        

    def draw(self):
        """
        Draw the current game state to the screen.
        """
        
        self.screen.fill((255, 255, 255))  # Fill background with white
        self.game.draw_grid(self.screen, cell_size=self.cell_size, paused=self.paused)
        
        # for b in self.bullets:
            
        #     b.draw()

        # if self.show_boids:
        #     self.flock_p.draw()
        #     self.flock_e.draw()
        #     self.player.draw()
        
        pygame.display.flip()

    def run(self):
        """
        The main game loop that runs the game.
        """
        while self.running:
            self.flock_e.set_adversary_positions(self.flock_p.X)
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # Adjust the frame rate to control the speed of the game

        pygame.quit()

class Player:

    def __init__(self, screen, col, x_0):
        self.screen = screen
        self.color = col
        rng = np.random.default_rng()
        self.x = x_0
        self.x_dot = rng.random((2))

        # print("x = ", self.x)
        # print("v = ", self.x_dot)


    def update(self, dt, u):
        self.x_dot += u*dt
        if np.linalg.norm(self.x_dot) > 100:
            self.x_dot = 100* (self.x_dot / np.linalg.norm(self.x_dot))

        self.x += self.x_dot*dt
        

        self.x = self.x % self.screen.get_width()


    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.x[0] , self.x[1] , 10, 10))


if __name__ == "__main__":
    pygame.init()
    game = Game(width=150, height=150, cell_size=5)
    game.run()