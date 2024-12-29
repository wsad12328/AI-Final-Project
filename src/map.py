# src/map.py

import numpy as np
import perlin_noise

class Map:
    def __init__(self, width, height, grid_size, seed):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.num_rows = height // grid_size
        self.num_cols = width // grid_size
        self.seed = seed
        self.direction = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1)]
        self.map_data = self.generate_map()
        self.label_map_data = self.label_map()

    def generate_map(self):
        noise = perlin_noise.PerlinNoise(octaves=8, seed=self.seed)
        map_data = np.zeros((self.num_cols, self.num_rows))
        for i in range(self.num_cols):
            for j in range(self.num_rows):
                map_data[i, j] = noise([i / 50, j / 50])
        map_data = (map_data - np.min(map_data)) / (np.max(map_data) - np.min(map_data))
        return map_data

    def label_map(self):
        label_map_data = np.zeros((self.num_cols, self.num_rows))
        for i in range(self.num_cols):
            for j in range(self.num_rows):
                value = self.map_data[i, j]
                if value < 0.4:
                    label_map_data[i, j] = 1  # 草地顏色
                elif value < 0.7:
                    label_map_data[i, j] = 2  # 泥土顏色
                else:
                    label_map_data[i, j] = 3  # 沙子顏色
        return label_map_data