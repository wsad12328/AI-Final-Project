import pygame
import random
import perlin_noise
import numpy as np
from itertools import accumulate
import sys


FPS = 2
# 螞蟻的參數
MAX_ITER = 2
EVAPORATE_RATE_1 = 0.5
EVAPORATE_RATE_2 = 0.5
EVAPORATE_RATE_3 = 0.5
Q = 100
ALPHA = 2
BETA = 4
NUMBER_OF_ANT = 200

# 相鄰的網格方向
direction = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1)]
weighted_dict = {1:1,2:3,3:5}

# 定義地圖大小和網格大小
map_width = 1000
map_height = 1000
grid_size = 25

num_rows = map_height // grid_size
num_cols = map_width // grid_size

# 載入素材圖片
grass_image = pygame.image.load("grass.png")
soil_image = pygame.image.load("soil.png")
sand_image = pygame.image.load("sand.png")

grass_ant_image = pygame.image.load("grassants.png")
soil_ant_image = pygame.image.load("soilants.png")
sand_ant_image = pygame.image.load("sandants.png")

#螞蟻與費洛蒙切換
show_ant = True
# 初始化 Pygame
pygame.init()

# 建立 Pygame 視窗
screen = pygame.display.set_mode((map_width, map_height))
pygame.display.set_caption("ACO Map")
clock = pygame.time.Clock()

# 隨機生成地圖，正規化地圖數據
random_seed = np.random.randint(1000)  # 使用不同的隨機種子
noise = perlin_noise.PerlinNoise(octaves=5, seed=100)
map_data = np.zeros((num_cols, num_rows))
label_map_data =  np.zeros((num_cols, num_rows))

for i in range(num_cols):
    for j in range(num_rows):
        map_data[i, j] = noise([i / 50, j / 50])

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

def map_value(value, in_min, in_max, out_min, out_max):
    #映射
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#蟻群
pheromone_data = np.ones((num_rows, num_cols))
distance_data = np.full((num_rows, num_cols, 8), -1, dtype=float)
for i in range(num_rows):
    for j in range(num_cols):
        current_x = i
        current_y = j
        current_type = label_map_data[current_x][current_y]
        for k in range(8):
            neighbor_x = current_x + direction[k][0]
            neighbor_y = current_y + direction[k][1]
            if(neighbor_x >= 0 and neighbor_x < num_rows and neighbor_y >= 0 and neighbor_y < num_cols):
                neighbor_type = label_map_data[neighbor_x][neighbor_y]
                distance_data[i, j, k] = (weighted_dict[current_type] + weighted_dict[neighbor_type])


def update_pheromone(delta_pheromone):
    for i in range(num_rows):
        for j in range(num_cols):
            if(label_map_data[i, j] == 1):
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_1 + delta_pheromone[i, j] * (1 - EVAPORATE_RATE_1)
            elif(label_map_data[i, j] == 2):
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_2 + delta_pheromone[i, j] * (1 - EVAPORATE_RATE_2)
            elif(label_map_data[i, j] == 3):
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_3 + delta_pheromone[i, j] * (1 - EVAPORATE_RATE_3)

# print(label_map_data)
class Ant():
    def __init__(self):
        self.path = []
        self.move_count = 0
        self.totol_distance = 0
        self.current_city = (0, 0)
        self.legal_city = np.ones((num_cols, num_rows))
        self.path.append(self.current_city)
        self.legal_city[self.current_city[0]][self.current_city[1]] = False
        self.move_count += 1
    def select(self):
        total_prob = 0
        select_candidate_direction = []
        select_candidate_probability = []
        # print(f"current city{self.current_city}")
        
        for i in range(len(direction)):
            x_coordinate = self.current_city[0] + direction[i][0]
            y_coordiante = self.current_city[1] + direction[i][1]
            if(x_coordinate >= 0 and x_coordinate < num_rows and y_coordiante >= 0 and y_coordiante < num_cols):
                if(self.legal_city[x_coordinate][y_coordiante]):
                    distance = distance_data[self.current_city[0], self.current_city[1], i]
                    # print(distance)
                    prob = pheromone_data[x_coordinate][y_coordiante] ** ALPHA + (1 / distance) ** BETA
                    # select_candidate_direction.append(direction[i])
                    select_candidate_direction.append(i)
                    select_candidate_probability.append(prob)
                    
        # 輪盤法
        # print(f"direct: {select_candidate_direction}")
        if(len(select_candidate_probability) != 0):
            # print(self.legal_city)
            for i in range(len(select_candidate_probability)):
                total_prob += select_candidate_probability[i]

            for i in range(len(select_candidate_probability)):
                select_candidate_probability[i] = select_candidate_probability[i] / total_prob
            
            select_candidate_probability = list(accumulate(select_candidate_probability))
            # print(select_candidate_probability)
            random_value = random.uniform(0, 1)
            index = 0
            for accumulate_prob in select_candidate_probability:
                if random_value > accumulate_prob:
                    index += 1
            # print(f"option: {index}")
            next_x = self.current_city[0] + direction[select_candidate_direction[index]][0]
            next_y = self.current_city[1] + direction[select_candidate_direction[index]][1]
            # print(next_x, next_y)
            self.totol_distance += distance_data[self.current_city[0], self.current_city[1], select_candidate_direction[index]]
            self.current_city = (next_x, next_y)
            # print(f"current point: {self.current_city}")
            self.path.append(self.current_city)
            # print(self.path)
            self.legal_city[self.current_city[0]][self.current_city[1]] = False
            # # print(self.legal_city)
            self.move_count += 1
        else:
            # print(self.current_city)
            return True

    def run_path(self):
        death_flag = False

        while(self.current_city[0] != num_rows-1 or self.current_city[1] != num_cols-1):
            if(death_flag == True):
                #print("LOST")
                break
            elif(self.move_count > num_rows*num_cols):
                #print("DEAD")
                break

            death_flag = self.select()
        return death_flag
    
    def release_pheromone(self,delta_pheromone):
        # print(self.path)     
        for city in self.path:
            if(label_map_data[city[0]][city[1]] == 1):
                delta_pheromone[city[0]][city[1]] += (Q / self.totol_distance * (1 - EVAPORATE_RATE_1))
            elif(label_map_data[city[0]][city[1]] == 2):
                delta_pheromone[num_rows-1][num_cols-1] += (Q / self.totol_distance * (1 - EVAPORATE_RATE_2))
            elif(label_map_data[city[0]][city[1]] == 3):
                delta_pheromone[num_rows-1][num_cols-1] += (Q / self.totol_distance * (1 - EVAPORATE_RATE_3))

best_value = sys.maxsize
best_solution = []

# 主迴圈
running = True
while running:
    clock.tick(FPS)
    # 取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # 按下空格键，切换開始
            show_ant = not show_ant

    # 更新遊戲
    #for i in range(MAX_ITER):
        delta_pheromone = np.zeros((num_cols, num_rows))
        for j in range(NUMBER_OF_ANT):
            ant = Ant()
            Update_bool = ant.run_path()
            if(not Update_bool):
                ant.release_pheromone(delta_pheromone)
            if ant.totol_distance < best_value and not(Update_bool):
                best_value = ant.totol_distance
                best_solution = ant.path
        update_pheromone(delta_pheromone)

    print(f"Best value: {best_value}")
    #print(best_solution)
    # 畫面顯示
            
    # 繪製地圖
    for i in range(num_cols):
        for j in range(num_rows):
            value = map_data[i, j]
            if (i, j) in best_solution:
                if value < 0.4:
                    screen.blit(grass_ant_image, (j * grid_size, i * grid_size))
                elif value < 0.7:
                    screen.blit(soil_ant_image, (j * grid_size, i * grid_size))
                else:
                    screen.blit(sand_ant_image, (j * grid_size, i * grid_size))
                #color = (0, 0, 0)
                #pygame.draw.rect(screen, color, (j * grid_size, i * grid_size, grid_size, grid_size))

            else:
                if value < 0.4:
                    screen.blit(grass_image, (j * grid_size, i * grid_size))
                elif value < 0.7:
                    screen.blit(soil_image, (j * grid_size, i * grid_size))
                else:
                    screen.blit(sand_image, (j * grid_size, i * grid_size))
            
            if show_ant == False:
                if pheromone_data[i, j] > 0.005 :
                    color = (255, 255, 255)
                    pygame.draw.rect(screen, color, (j * grid_size, i * grid_size, grid_size, grid_size))

                    #if pheromone_data[i, j] > 0.005:
                        #circle_size = int(map_value(pheromone_data[i, j], 0.005, 10, 0, 20))
                        #print(circle_size)
                        #pygame.draw.circle(screen, (255, 255, 255),  (i * grid_size + grid_size/2, j * grid_size + grid_size/2) ,  circle_size/2)
        # 更新顯示
    pygame.display.update()

# 關閉 Pygame
pygame.quit()
