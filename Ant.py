import pygame
import numpy as np

# Set the random seed
np.random.seed(42)

# Define the map size
num_rows = 40
num_cols = 40

# Generate a 40x40 array with values 1, 2, or 3
map_data = np.random.randint(1, 4, size=(num_rows, num_cols))

# Initialize Pygame
pygame.init()

# Set the window size and display the window
win_size = (1000, 1000)
win = pygame.display.set_mode(win_size)
pygame.display.set_caption("Random Map")

# Define different colors for each value
tile_colors = {
    1: (0, 255, 0),    # Green for grass
    2: (139, 69, 19),   # Brown for soil
    3: (255, 255, 0)    # Yellow for sand
}

# Set the size of each grid cell
tile_size = win_size[0] // num_cols, win_size[1] // num_rows

grass_image = pygame.image.load("grass.png")
soil_image = pygame.image.load("soil.png")
sand_image = pygame.image.load("sand.png")
print()
# Main loop
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # Draw the map
#     for i in range(num_rows):
#         for j in range(num_cols):
#             if map_data[i, j] == 1:
#                 win.blit(grass_image, (j * tile_size, i * tile_size))
#                 # pygame.draw.rect(win, tile_colors[map_data[i, j]], (j * tile_size[0], i * tile_size[1], tile_size[0], tile_size[1]))
#             elif map_data[i, j] == 2:
#                 win.blit(soil_image, (j * tile_size, i * tile_size))
#                 # pygame.draw.rect(win, tile_colors[map_data[i, j]], (j * tile_size[0], i * tile_size[1], tile_size[0], tile_size[1]))
#             elif map_data[i, j] == 3:
#                 win.blit(sand_image, (j * tile_size, i * tile_size))  
#                 # pygame.draw.rect(win, tile_colors[map_data[i, j]], (j * tile_size[0], i * tile_size[1], tile_size[0], tile_size[1]))

#     pygame.display.flip()

# # Close Pygame
# pygame.quit()
