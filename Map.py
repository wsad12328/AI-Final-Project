import pygame
import random
import perlin_noise
import numpy as np
from itertools import accumulate

FPS = 60
# 螞蟻的參數
EVAPORATE_RATE = 0.5
Q = 10
ALPHA = 0.5
BETA = 0.5
NUMBER_OF_ANT = 10

# 相鄰的網格方向
direction = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1)]
weighted_dict = {1:1,2:3,3:5}

# 定義地圖大小和網格大小
map_width = 1000
map_height = 1000
grid_size = 50

# 初始化 Pygame
pygame.init()

# 建立 Pygame 視窗
screen = pygame.display.set_mode((map_width, map_height))
pygame.display.set_caption("ACO Map")
clock = pygame.time.Clock()

# 隨機生成地圖
random_seed = np.random.randint(1000)  # 使用不同的隨機種子
# print(random_seed)
noise = perlin_noise.PerlinNoise(octaves=20, seed=100)
num_rows = map_height // grid_size
num_cols = map_width // grid_size
map_data = np.zeros((num_cols, num_rows))
label_map_data =  np.zeros((num_cols, num_rows))


for i in range(num_cols):
    for j in range(num_rows):
        map_data[i, j] = noise([i / 50, j / 50])

# 正規化地圖數據
map_data = (map_data - np.min(map_data)) / (np.max(map_data) - np.min(map_data))

for i in range(num_cols):
    for j in range(num_rows):
        value = map_data[i, j]
        if value < 0.4:
            label_map_data[i, j] = 1  # 草地顏色
        elif value < 0.7:
            label_map_data[i, j] = 2  # 泥土顏色
        else:
            label_map_data[i, j] = 3  # 沙子顏色

# 主迴圈
running = True
while running:
    clock.tick(FPS)
    # 取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # 更新遊戲
        
    # 畫面顯示
            
    # 繪製地圖
    for i in range(num_cols):
        for j in range(num_rows):
            value = map_data[i, j]
            if value < 0.4:
                color = (34, 139, 34)  # 草地顏色
            elif value < 0.7:
                color = (139, 69, 19)  # 泥土顏色
            else:
                color = (255, 204, 176)  # 沙子顏色
            pygame.draw.rect(screen, color, (j * grid_size, i * grid_size, grid_size, grid_size))

    # 更新顯示
    pygame.display.update()

# 關閉 Pygame
pygame.quit()
