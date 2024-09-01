# game_logic.py

import numpy as np
import random
import pygame

class CompetitiveGameOfLife:
    def __init__(self, width=50, height=50, cell_types=[0, 1, 2, 3, 4]):
        """
        Initialize the game logic with a grid of given width, height, and cell types.
        
        Parameters:
            width (int): The width of the grid.
            height (int): The height of the grid.
            cell_types (list): List of integers representing different cell types.
        """
        self.width = width
        self.height = height
        self.cell_types = cell_types
        self.grid = np.zeros((height, width), dtype=int)  # Start with an empty grid (all cells dead)
        self.colors = {
            0: (248, 247, 230),   # Empty cells (Black)
            1: (243, 45, 81),  # Type 1 (Red)
            2: (81, 45, 243),  # Type 2 (Blue)
            3: (45, 243, 81),  # Type 3 (Green)
            4: (243, 245, 10), # Type 4 (Yellow)
        }

    def get_neighbors(self, x, y):
        """
        Get the neighboring cells for a cell at position (x, y).
        
        Parameters:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
            
        Returns:
            list: A list of neighboring cell values.
        """
        neighbors = [
            self.grid[(y-1)%self.height, (x-1)%self.width], self.grid[(y-1)%self.height, x], self.grid[(y-1)%self.height, (x+1)%self.width],
            self.grid[y, (x-1)%self.width],                                          self.grid[y, (x+1)%self.width],
            self.grid[(y+1)%self.height, (x-1)%self.width], self.grid[(y+1)%self.height, x], self.grid[(y+1)%self.height, (x+1)%self.width],
        ]
        return neighbors

    def apply_life_rules(self, x, y):
        """
        Apply the competitive life rules to the cell at position (x, y).
        
        Parameters:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
        """
        current_cell = self.grid[y, x]
        neighbors = self.get_neighbors(x, y)

        if current_cell == 0:  # If the cell is empty
            # Count the types of neighbors
            neighbor_counts = [neighbors.count(i) for i in self.cell_types[1:]]
            max_count = max(neighbor_counts)
            if max_count >= 3:  # Birth rule: 3 or more neighbors of the same type
                # Overwrite with the majority type or resolve randomly if there's a tie
                if neighbor_counts.count(max_count) > 1:
                    new_type = random.choice([i+1 for i in range(len(neighbor_counts)) if neighbor_counts[i] == max_count])
                else:
                    new_type = neighbor_counts.index(max_count) + 1
                self.grid[y, x] = new_type
        else:  # If the cell is alive
            # Count different neighbor types
            same_type_count = neighbors.count(current_cell)
            if same_type_count < 2 or same_type_count > 3:
                # Death by underpopulation or overpopulation
                self.grid[y, x] = 0
            elif len(set(neighbors)) > 2:  # Check if the cell is surrounded by different types
                self.grid[y, x] = 0

    def update_grid(self, paused):
        """
        Update the grid by applying the life rules to every cell.
        """
        if not paused:
            new_grid = self.grid.copy()
            for y in range(self.height):
                for x in range(self.width):
                    current_cell = self.grid[y, x]
                    neighbors = self.get_neighbors(x, y)

                    if current_cell == 0:  # If the cell is empty
                        # Count the types of neighbors
                        neighbor_counts = [neighbors.count(i) for i in self.cell_types[1:]]
                        max_count = max(neighbor_counts)
                        if max_count >= 3:  # Birth rule: 3 or more neighbors of the same type
                            # Overwrite with the majority type or resolve randomly if there's a tie
                            if neighbor_counts.count(max_count) > 1:
                                new_type = random.choice([i+1 for i in range(len(neighbor_counts)) if neighbor_counts[i] == max_count])
                            else:
                                new_type = neighbor_counts.index(max_count) + 1
                            new_grid[y, x] = new_type
                    else:  # If the cell is alive
                        # Count different neighbor types
                        same_type_count = neighbors.count(current_cell)
                        if same_type_count < 2 or same_type_count > 3:
                            # Death by underpopulation or overpopulation
                            new_grid[y, x] = 0
                        elif len(set(neighbors)) > 2:  # Check if the cell is surrounded by different types
                            new_grid[y, x] = 0

            self.grid = new_grid
        

    def reset_grid(self):
        """
        Reset the grid to an empty state (no living cells).
        """
        self.grid = np.zeros((self.height, self.width), dtype=int)

    def place_cell(self, x, y, cell_type):
        """
        Place a cell of the given type at the specified coordinates.
        
        Parameters:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
            cell_type (int): The type of cell to place.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = cell_type

    def remove_cell(self, x, y):
        """
        Place a cell of the given type at the specified coordinates.
        
        Parameters:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
            cell_type (int): The type of cell to place.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = 0

    def draw_grid(self, screen, cell_size=10, paused=False):
        """
        Draw the grid on the given Pygame screen.
        
        Parameters:
            screen (pygame.Surface): The Pygame screen to draw on.
            cell_size (int): The size of each cell in pixels.
        """
        for y in range(self.height):
            for x in range(self.width):
                if paused:
                    self.colors[0] = (148, 147, 150)
                else:
                    self.colors[0] = (248, 247, 230)

                color = self.colors[self.grid[y, x]]
                pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))