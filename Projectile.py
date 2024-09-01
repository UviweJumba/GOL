import pygame
import numpy as np

class Projectile:
    def __init__(self, screen, initial_positions, directions, velocity=1000):
        """
        Initialize the Projectile class.

        Parameters:
        - initial_positions (ndarray): Matrix of initial positions of shape (N, 2).
        - directions (ndarray): Matrix of directions of shape (N, 2), should be normalized.
        - velocity (float): Speed of each projectile.
        """
        self.screen = screen
        self.team_idx = 0

        self.positions = initial_positions #np.array([float(self.screen.get_width()/2), float(self.screen.get_width()/2)])
        self.directions = directions/np.linalg.norm(directions)
        self.velocity = velocity

        self.life_time = 6


    def update(self, dt=1/30):
        """
        Update the positions of the projectiles based on their directions, velocity, and time step.

        Parameters:
        - dt (float): Time step for integration.

        Returns:
        - positions (ndarray): Updated positions of shape (N, 2).
        """
        # Update positions
        

        displacement = self.directions * self.velocity * dt
        self.positions += displacement
        # print("pos: ", self.positions)
        # print("displacement: ",displacement)

        
        self.life_time -= 1

    def draw(self):

        pygame.draw.rect(self.screen, (220, 180, 140), (self.positions[0]%self.screen.get_width() , self.positions[1]%self.screen.get_height() , 7, 7)) #%self.screen.get_height(), %self.screen.get_width()