import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import random
import perlin_noise
import numpy as np
from itertools import accumulate
import sys


FPS_RUN = 10
FPS_STOP = 60

generation = 0
game_started = True # 這個是方便跑實驗用的
# game_started = False 
stop_generation = 500

# 螞蟻的參數
# MAX_ITER = 5
Q = 100
weighted_dict = {1: 1, 2: 3, 3: 5}
# 1號 草地 2號 泥土 3號 沙子
EVAPORATE_RATE_1 = float(sys.argv[1])
EVAPORATE_RATE_2 = float(sys.argv[2])
EVAPORATE_RATE_3 = float(sys.argv[3])

ALPHA = int(sys.argv[4])  # mode 1(4, 2) # mode 2(3, 3) # mode 2(2, 4) alpha + beta = 6
BETA = int(sys.argv[5])  # (1, 5) (2, 4) (3, 3) (4, 2) (5, 1)
seed = int(sys.argv[6])
# print(f"seed: {seed}")
# print(seed)
NUMBER_OF_ANT = 200

# 相鄰的網格方向
direction = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1)]


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

background_image = pygame.image.load("background.jpg") 
home_image = pygame.image.load("home.jpg") 
food_image = pygame.image.load("cake.jpg") 

# 螞蟻與費洛蒙切換
show_ant = False
# 初始化 Pygame
pygame.init()

# 建立 Pygame 視窗
screen = pygame.display.set_mode((map_width + 200, map_height))
#background_color = (144, 238, 144)  # 
#screen.fill(background_color)
screen.blit(background_image, (0, 0))

pygame.display.set_caption("ACO Map")
clock = pygame.time.Clock()

# 隨機生成地圖，正規化地圖數據

random_seed = np.random.randint(seed)  # 使用不同的隨機種子
random.seed(seed)  # 使用不同的隨機種子
noise = perlin_noise.PerlinNoise(octaves=8, seed=100)  # 地圖的random seed先不要動
map_data = np.zeros((num_cols, num_rows))
label_map_data = np.zeros((num_cols, num_rows))

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

# 蟻群
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
            if (
                neighbor_x >= 0
                and neighbor_x < num_rows
                and neighbor_y >= 0
                and neighbor_y < num_cols
            ):
                neighbor_type = label_map_data[neighbor_x][neighbor_y]
                distance_data[i, j, k] = (
                    weighted_dict[current_type] + weighted_dict[neighbor_type]
                )


def update_pheromone(pheromone_data, delta_pheromone):
    for i in range(num_rows):
        for j in range(num_cols):
            if label_map_data[i, j] == 1:
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_1 + delta_pheromone[i, j]
                if pheromone_data[i, j] < 1e-5:
                    pheromone_data[i, j] =  1 / weighted_dict[1]
            elif label_map_data[i, j] == 2:
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_2 + delta_pheromone[i, j]
                if pheromone_data[i, j] < 1e-5:
                    pheromone_data[i, j] = 1 / weighted_dict[2]
            elif label_map_data[i, j] == 3:
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_3 + delta_pheromone[i, j]
                if pheromone_data[i, j] < 1e-5:
                    pheromone_data[i, j] = 1 / weighted_dict[3]


# print(label_map_data)
class Ant:
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
            if (
                x_coordinate >= 0
                and x_coordinate < num_rows
                and y_coordiante >= 0
                and y_coordiante < num_cols
            ):
                if self.legal_city[x_coordinate][y_coordiante]:
                    distance = distance_data[
                        self.current_city[0], self.current_city[1], i
                    ]
                    # print(distance)
                    prob = (
                        pheromone_data[x_coordinate][y_coordiante] ** ALPHA
                        + (1 / distance) ** BETA
                    )
                    # select_candidate_direction.append(direction[i])
                    select_candidate_direction.append(i)
                    select_candidate_probability.append(prob)

        # 輪盤法
        # print(f"direct: {select_candidate_direction}")
        if len(select_candidate_probability) != 0:
            # print(self.legal_city)
            for i in range(len(select_candidate_probability)):
                total_prob += select_candidate_probability[i]

            for i in range(len(select_candidate_probability)):
                select_candidate_probability[i] = (
                    select_candidate_probability[i] / total_prob
                )

            select_candidate_probability = list(
                accumulate(select_candidate_probability)
            )
            # print(select_candidate_probability)
            random_value = random.uniform(0, 1)
            index = 0
            for accumulate_prob in select_candidate_probability:
                if random_value > accumulate_prob:
                    index += 1
            # print(f"option: {index}")
            next_x = (
                self.current_city[0] + direction[select_candidate_direction[index]][0]
            )
            next_y = (
                self.current_city[1] + direction[select_candidate_direction[index]][1]
            )
            # print(next_x, next_y)
            self.totol_distance += distance_data[
                self.current_city[0],
                self.current_city[1],
                select_candidate_direction[index],
            ]
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

        while (
            self.current_city[0] != num_rows - 1 or self.current_city[1] != num_cols - 1
        ):
            if death_flag == True:
                # print("LOST")
                break
            elif self.move_count > num_rows * num_cols:
                # print("DEAD")
                break

            death_flag = self.select()
        return death_flag

    def release_pheromone(self, delta_pheromone):
        # print(self.path)
        for city in self.path:
            delta_pheromone[city[0]][city[1]] += (Q / self.totol_distance )
            # if label_map_data[city[0]][city[1]] == 1:
            #     delta_pheromone[city[0]][city[1]] += (
            #         Q / self.totol_distance 
            #     )
            # elif label_map_data[city[0]][city[1]] == 2:
            #     delta_pheromone[num_rows - 1][num_cols - 1] += (
            #         Q / self.totol_distance 
            #     )
            # elif label_map_data[city[0]][city[1]] == 3:
            #     delta_pheromone[num_rows - 1][num_cols - 1] += (
            #         Q / self.totol_distance
            #     )


best_value = sys.maxsize
best_solution = []
font_color = (0, 0, 0)

def draw_generation_count():
    fontbar = pygame.font.Font(None, 40)
    generation_text = fontbar.render(f"Generation", True, font_color)
    generation_value = fontbar.render(f"{generation}", True,font_color)
    screen.blit(generation_text,(1020, 10))
    screen.blit(generation_value,(1080, 60))

def draw_best_path_count():
    fontbar = pygame.font.Font(None, 40)
    generation_text = fontbar.render(f"Best path", True,font_color)

    if best_value == 9223372036854775807:
        generation_value = fontbar.render(f"step : 0", True, font_color)
    else:
        generation_value = fontbar.render(f"step : {best_value}", True,font_color)

    screen.blit(generation_text,(1030, 110))
    screen.blit(generation_value,(1020, 160))

def draw_variable():
    fontbar = pygame.font.Font(None, 40)

    grass_E_text = fontbar.render(f"grass", True, font_color)
    grass_E = fontbar.render(f"{EVAPORATE_RATE_1:.1f}", True,font_color)
    soil_E_text = fontbar.render(f"soil ", True, font_color)
    soil_E = fontbar.render(f"{EVAPORATE_RATE_2:.1f}", True, font_color)
    sand_E_text = fontbar.render(f"sand ", True, font_color)
    sand_E = fontbar.render(f"{EVAPORATE_RATE_3:.1f}", True, font_color)

    ALPHA_B_text = fontbar.render(f"alpha", True, font_color)
    ALPHA_B = fontbar.render(f"{ALPHA:.1f}", True,font_color)
    BETA_B_text = fontbar.render(f"beta", True, font_color)
    BETA_B = fontbar.render(f"{BETA:.1f}", True, font_color)

    stop_generation_text = fontbar.render(f"stop", True, font_color)
    stop_generation_value = fontbar.render(f"{stop_generation}", True, font_color)

    screen.blit(grass_E_text,(1065, 400))
    screen.blit(grass_E,(1080, 450))
    screen.blit(soil_E_text,(1075, 500))
    screen.blit(soil_E,(1080, 550))
    screen.blit(sand_E_text,(1070, 600))
    screen.blit(sand_E,(1080, 650))

    screen.blit(ALPHA_B_text,(1065, 700))
    screen.blit(ALPHA_B,(1080, 750))
    screen.blit(BETA_B_text,(1070, 800))
    screen.blit(BETA_B,(1080, 850))

    screen.blit(stop_generation_text,(1070, 900))
    screen.blit(stop_generation_value,(1080, 950))



font = pygame.font.Font(None, 30)
button_color = (173, 216, 230)
side_color = (70, 130, 180)
# 定義工具列按鈕的顏色和位置
button_width = 185
button_height = 90

button_x = 1010
plus_x = 1010
minus_x = 1145

def check_button_click(x, y):
    if start_pause_button.collidepoint(x, y):
        return 1
    elif clear_button.collidepoint(x, y):
        return 2
    elif plus_1.collidepoint(x, y):
        return 11
    elif plus_2.collidepoint(x, y):
        return 12
    elif plus_3.collidepoint(x, y):
        return 13
    elif plus_4.collidepoint(x, y):
        return 14
    elif plus_5.collidepoint(x, y):
        return 15
    elif plus_6.collidepoint(x, y):
        return 16
    elif minus_1.collidepoint(x, y):
        return 21
    elif minus_2.collidepoint(x, y):
        return 22
    elif minus_3.collidepoint(x, y):
        return 23
    elif minus_4.collidepoint(x, y):
        return 24
    elif minus_5.collidepoint(x, y):
        return 25
    elif minus_6.collidepoint(x, y):
        return 26
# 定義工具列按鈕
start_pause_button = pygame.Rect(button_x, 200, button_width, button_height)
border_rect = start_pause_button.copy()
border_rect.inflate_ip(5, 5)  # 調整邊框的寬度
pygame.draw.rect(screen, side_color, border_rect, 5)  # 黑色邊框

clear_button = pygame.Rect(button_x,300, button_width, button_height)
border_rect = clear_button.copy()
border_rect.inflate_ip(5, 5)  # 調整邊框的寬度
pygame.draw.rect(screen, side_color, border_rect, 5)  # 黑色邊框

plus_1 = pygame.Rect(plus_x, 400, 50, 90)
plus_2 = pygame.Rect(plus_x, 500, 50, 90)
plus_3 = pygame.Rect(plus_x, 600, 50, 90)
plus_4 = pygame.Rect(plus_x, 700, 50, 90)
plus_5 = pygame.Rect(plus_x, 800, 50, 90)
plus_6 = pygame.Rect(plus_x, 900, 50, 90)

minus_1 = pygame.Rect(minus_x, 400, 50, 90)
minus_2 = pygame.Rect(minus_x, 500, 50, 90)
minus_3 = pygame.Rect(minus_x, 600, 50, 90)
minus_4 = pygame.Rect(minus_x, 700, 50, 90)
minus_5 = pygame.Rect(minus_x, 800, 50, 90)
minus_6 = pygame.Rect(minus_x, 900, 50, 90)



def draw_toolbar():
    font = pygame.font.Font(None, 40)
    # 繪製開始/暫停按鈕
    start_pause_text = font.render("Start/Pause", True, font_color)
    pygame.draw.rect(screen, (173, 216, 230), start_pause_button)
    screen.blit(start_pause_text, (button_x + 15, 230))

    clear_button_text = font.render("Clear", True, font_color)
    pygame.draw.rect(screen, button_color, clear_button)
    screen.blit(clear_button_text, (button_x + 50, 330))

    plus_text = font.render("+", True, font_color)
    pygame.draw.rect(screen, button_color, plus_1)
    pygame.draw.rect(screen, button_color, plus_2)
    pygame.draw.rect(screen, button_color, plus_3)
    pygame.draw.rect(screen, button_color, plus_4)
    pygame.draw.rect(screen, button_color, plus_5)
    pygame.draw.rect(screen, button_color, plus_6)
    screen.blit(plus_text, (plus_x + 15, 430))
    screen.blit(plus_text, (plus_x + 15, 530))
    screen.blit(plus_text, (plus_x + 15, 630))
    screen.blit(plus_text, (plus_x + 15, 730))
    screen.blit(plus_text, (plus_x + 15, 830))
    screen.blit(plus_text, (plus_x + 15, 930))

    minus_text = font.render("-", True, font_color)
    pygame.draw.rect(screen, button_color, minus_1)
    pygame.draw.rect(screen, button_color, minus_2)
    pygame.draw.rect(screen, button_color, minus_3)
    pygame.draw.rect(screen, button_color, minus_4)
    pygame.draw.rect(screen, button_color, minus_5)
    pygame.draw.rect(screen, button_color, minus_6)
    screen.blit(minus_text, (minus_x + 20, 430))
    screen.blit(minus_text, (minus_x + 20, 530))
    screen.blit(minus_text, (minus_x + 20, 630))
    screen.blit(minus_text, (minus_x + 20, 730))
    screen.blit(minus_text, (minus_x + 20, 830))
    screen.blit(minus_text, (minus_x + 20, 930))

    border_rect = start_pause_button.copy()
    border_rect.inflate_ip(5, 5)  # 調整邊框的寬度
    pygame.draw.rect(screen, side_color, border_rect, 5)  # 黑色邊框
    border_rect = clear_button.copy()
    border_rect.inflate_ip(5, 5)  # 調整邊框的寬度
    pygame.draw.rect(screen, side_color, border_rect, 5)  # 黑色邊框
    border_rect = plus_1.copy()
    border_rect.inflate_ip(5, 5) 
    pygame.draw.rect(screen, side_color, border_rect, 5)  
    border_rect = plus_2.copy()
    border_rect.inflate_ip(5, 5)  
    pygame.draw.rect(screen, side_color, border_rect, 5) 
    border_rect = plus_3.copy()
    border_rect.inflate_ip(5, 5)  
    pygame.draw.rect(screen, side_color, border_rect, 5)
    border_rect = plus_4.copy()
    border_rect.inflate_ip(5, 5)  
    pygame.draw.rect(screen, side_color, border_rect, 5)  
    border_rect = plus_5.copy()
    border_rect.inflate_ip(5, 5)  
    pygame.draw.rect(screen, side_color, border_rect, 5) 
    border_rect = plus_6.copy()
    border_rect.inflate_ip(5, 5)  
    pygame.draw.rect(screen, side_color, border_rect, 5)  

    border_rect = minus_1.copy()
    border_rect.inflate_ip(5, 5) 
    pygame.draw.rect(screen, side_color, border_rect, 5)  
    border_rect = minus_2.copy()
    border_rect.inflate_ip(5, 5)  
    pygame.draw.rect(screen, side_color, border_rect, 5) 
    border_rect = minus_3.copy()
    border_rect.inflate_ip(5, 5)  
    pygame.draw.rect(screen, side_color, border_rect, 5)  
    border_rect = minus_4.copy()
    border_rect.inflate_ip(5, 5) 
    pygame.draw.rect(screen, side_color, border_rect, 5)  
    border_rect = minus_5.copy()
    border_rect.inflate_ip(5, 5) 
    pygame.draw.rect(screen, side_color, border_rect, 5)   
    border_rect = minus_6.copy()
    border_rect.inflate_ip(5, 5) 
    pygame.draw.rect(screen, side_color, border_rect, 5) 






#初始化
def initialize():
    #screen.fill(background_color)
    screen.blit(background_image, (0, 0))
    for i in range(num_cols):
        for j in range(num_rows):
            if i == 0 and j == 0:
                screen.blit(home_image, (j * grid_size, i * grid_size))
            elif i == num_cols-1 and j == num_rows-1:
                screen.blit(food_image, (j * grid_size, i * grid_size))
            else:
                value = map_data[i, j]
                if value < 0.4:
                    screen.blit(grass_image, (j * grid_size, i * grid_size))
                elif value < 0.7:
                    screen.blit(soil_image, (j * grid_size, i * grid_size))
                else:
                    screen.blit(sand_image, (j * grid_size, i * grid_size))
    draw_toolbar()
    draw_variable()
    draw_generation_count()
    draw_best_path_count()
    pygame.display.update()

initialize()
# 主迴圈
running = True
while running:
    if game_started:
        clock.tick(FPS_RUN)
        button_color = (255,0,0)
    else:
        clock.tick(FPS_STOP)
        button_color = (173, 216, 230)
    draw_toolbar()
    pygame.display.update()
    # 取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # 按下空格键，切换費洛蒙顯示
            show_ant = not show_ant

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if check_button_click(x, y) == 1:
                game_started = not game_started
            else:
                if game_started == False:
                    if check_button_click(x, y) == 2:
                        generation = 0
                        pheromone_data = np.ones((num_rows, num_cols))
                        #distance_data = np.full((num_rows, num_cols, 8), -1, dtype=float)
                        best_value = sys.maxsize
                        best_solution = []
                    elif check_button_click(x, y) == 11:
                        EVAPORATE_RATE_1 += 0.1
                    elif check_button_click(x, y) == 21:
                        EVAPORATE_RATE_1 -= 0.1
                    elif check_button_click(x, y) == 12:
                        EVAPORATE_RATE_2 += 0.1
                    elif check_button_click(x, y) == 22:
                        EVAPORATE_RATE_2 -= 0.1
                    elif check_button_click(x, y) == 13:
                        EVAPORATE_RATE_3 += 0.1
                    elif check_button_click(x, y) == 23:
                        EVAPORATE_RATE_3 -= 0.1
                    elif check_button_click(x, y) == 14:
                        ALPHA += 1
                    elif check_button_click(x, y) == 24:
                        ALPHA -= 1
                    elif check_button_click(x, y) == 15:
                        BETA += 1
                    elif check_button_click(x, y) == 25:
                        BETA -= 1
                    elif check_button_click(x, y) == 16:
                        stop_generation += 500
                    elif check_button_click(x, y) == 26:
                        stop_generation -= 500
                    initialize()

        # 更新遊戲
    if game_started:
        if generation < stop_generation:
            # for i in range(MAX_ITER):
            delta_pheromone = np.zeros((num_cols, num_rows))
            for j in range(NUMBER_OF_ANT):
                ant = Ant()
                Update_bool = ant.run_path()
                if not Update_bool:
                    ant.release_pheromone(delta_pheromone)
                if ant.totol_distance < best_value and not (Update_bool):
                    best_value = ant.totol_distance
                    best_solution = ant.path
            update_pheromone(pheromone_data, delta_pheromone)
            
            # 畫面顯示
            log_pheromone_data = np.log(pheromone_data)
            min_pheromone = np.min(log_pheromone_data)
            max_pheromone = np.max(log_pheromone_data)
            normalize_pheromone_data = (log_pheromone_data - min_pheromone) / (
                max_pheromone - min_pheromone
            )
            # 繪製地圖
            #screen.fill(background_color)
            screen.blit(background_image, (0, 0))
            generation += 1
            for i in range(num_cols):
                for j in range(num_rows):
                    value = map_data[i, j]
                    if (i, j) in best_solution:
                        if i == 0 and j == 0:
                            screen.blit(home_image, (j * grid_size, i * grid_size))
                        elif i == num_cols-1 and j == num_rows-1:
                            screen.blit(food_image, (j * grid_size, i * grid_size))
                        else:
                            if value < 0.4:
                                screen.blit(grass_ant_image, (j * grid_size, i * grid_size))
                            elif value < 0.7:
                                screen.blit(soil_ant_image, (j * grid_size, i * grid_size))
                            else:
                                screen.blit(sand_ant_image, (j * grid_size, i * grid_size))
                        # color = (0, 0, 0)
                        # pygame.draw.rect(screen, color, (j * grid_size, i * grid_size, grid_size, grid_size))

                    else:
                        if i == 0 and j == 0:
                            screen.blit(home_image, (j * grid_size, i * grid_size))
                        elif i == num_cols-1 and j == num_rows-1:
                            screen.blit(food_image, (j * grid_size, i * grid_size))
                        else:
                            if value < 0.4:
                                screen.blit(grass_image, (j * grid_size, i * grid_size))
                            elif value < 0.7:
                                screen.blit(soil_image, (j * grid_size, i * grid_size))
                            else:
                                screen.blit(sand_image, (j * grid_size, i * grid_size))

                    if show_ant == False:
                        if normalize_pheromone_data[i, j] > 1e-1:
                            transparency = 150
                            color = pygame.Color = (255, 0, 0, transparency)

                            circle_size = (grid_size / 2) * normalize_pheromone_data[i, j]

                            # 創建帶有 alpha 通道的 Surface
                            circle_surface = pygame.Surface((2 * circle_size, 2 * circle_size), pygame.SRCALPHA)
                            pygame.draw.circle(circle_surface, color, (circle_size, circle_size), circle_size)
                
                            # 將帶有 alpha 通道的 Surface 貼到畫面上
                            screen.blit(circle_surface, (j * grid_size, i * grid_size))

                            
                            #pygame.draw.circle(screen,color,(j * grid_size + grid_size / 2, i * grid_size + grid_size / 2),circle_size)
                # 更新顯示
            draw_toolbar()
            draw_variable()
            draw_generation_count()
            draw_best_path_count()
            pygame.display.update()
        else:
            # game_started = not game_started
            running = False # 這個是方便跑實驗用的
print(best_value)
# 關閉 Pygame
pygame.quit()
