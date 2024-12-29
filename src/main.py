import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import random
import perlin_noise
import numpy as np  
from itertools import accumulate
import sys
from utils.argparser import parse_args  # 引入新的參數解析模塊
from ant_base import AntBase  # 引入 AntBase 類
from ant_worker import AntWorker  # 引入 AntWorker 類
from utils.constants import * # 引入常量
from map import Map  # 引入新的 Map 類


FPS_RUN = 10
FPS_STOP = 60
game_started = True
generation = 0
stop_generation = 0
best_value = sys.maxsize
best_solution = []
font_color = (0, 0, 0)

# 解析參數
args = parse_args()

grass_evaporation_rate = args.grass_evaporation_rate
soil_evaporation_rate = args.soil_evaporation_rate
sand_evaporation_rate = args.sand_evaporation_rate
ALPHA = args.alpha
BETA = args.beta
random_seed = args.random_seed
NUMBER_OF_ANT = args.num_ants



# 載入素材圖片
grass_image = pygame.image.load("images/grass.png")
soil_image = pygame.image.load("images/soil.png")
sand_image = pygame.image.load("images/sand.png")
grass_ant_image = pygame.image.load("images/grassants.png")
soil_ant_image = pygame.image.load("images/soilants.png")
sand_ant_image = pygame.image.load("images/sandants.png")
background_image = pygame.image.load("images/background.jpg")
home_image = pygame.image.load("images/home.jpg")
food_image = pygame.image.load("images/cake.jpg")
# 螞蟻與費洛蒙切換
show_ant = False
# 初始化 Pygame
pygame.init()

# 建立 Pygame 視窗
screen = pygame.display.set_mode((map_width + 200, map_height))
screen.blit(background_image, (0, 0))

pygame.display.set_caption("ACO Map")
clock = pygame.time.Clock()

# 隨機生成地圖，正規化地圖數據

np.random.randint(random_seed)  # 使用不同的隨機種子
random.seed(random_seed)  # 使用不同的隨機種子

# 創建地圖對象
map_obj = Map(map_width, map_height, grid_size, random_seed)
map_data = map_obj.map_data
label_map_data = map_obj.label_map_data


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
                pheromone_data[i, j] = pheromone_data[i, j] * grass_evaporation_rate + delta_pheromone[i, j]
                if pheromone_data[i, j] < 1e-5:
                    pheromone_data[i, j] =  1 / weighted_dict[1]
            elif label_map_data[i, j] == 2:
                pheromone_data[i, j] = pheromone_data[i, j] * soil_evaporation_rate + delta_pheromone[i, j]
                if pheromone_data[i, j] < 1e-5:
                    pheromone_data[i, j] = 1 / weighted_dict[2]
            elif label_map_data[i, j] == 3:
                pheromone_data[i, j] = pheromone_data[i, j] * sand_evaporation_rate + delta_pheromone[i, j]
                if pheromone_data[i, j] < 1e-5:
                    pheromone_data[i, j] = 1 / weighted_dict[3]

def draw_generation_count():
    fontbar = pygame.font.Font(None, 40)
    generation_text = fontbar.render(f"Generation", True, font_color)
    generation_value = fontbar.render(f"{generation}", True,font_color)
    screen.blit(generation_text,(1020, 10))
    screen.blit(generation_value,(1080, 60))

def draw_best_path_count():
    fontbar = pygame.font.Font(None, 40)
    generation_text = fontbar.render(f"Best path", True,font_color)

    if best_value == sys.maxsize:
        generation_value = fontbar.render(f"step : 0", True, font_color)
    else:
        generation_value = fontbar.render(f"step : {best_value}", True,font_color)

    screen.blit(generation_text,(1030, 110))
    screen.blit(generation_value,(1020, 160))

def draw_variable():
    fontbar = pygame.font.Font(None, 40)

    grass_E_text = fontbar.render(f"grass", True, font_color)
    grass_E = fontbar.render(f"{grass_evaporation_rate:.1f}", True,font_color)
    soil_E_text = fontbar.render(f"soil ", True, font_color)
    soil_E = fontbar.render(f"{soil_evaporation_rate:.1f}", True, font_color)
    sand_E_text = fontbar.render(f"sand ", True, font_color)
    sand_E = fontbar.render(f"{sand_evaporation_rate:.1f}", True, font_color)

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
                        best_value = sys.maxsize
                        best_solution = []
                    elif check_button_click(x, y) == 11:
                        grass_evaporation_rate += 0.1
                    elif check_button_click(x, y) == 21:
                        grass_evaporation_rate -= 0.1
                    elif check_button_click(x, y) == 12:
                        soil_evaporation_rate += 0.1
                    elif check_button_click(x, y) == 22:
                        soil_evaporation_rate -= 0.1
                    elif check_button_click(x, y) == 13:
                        sand_evaporation_rate += 0.1
                    elif check_button_click(x, y) == 23:
                        sand_evaporation_rate -= 0.1
                    elif check_button_click(x, y) == 14:
                        ALPHA += 1
                    elif check_button_click(x, y) == 24:
                        ALPHA -= 1
                    elif check_button_click(x, y) == 15:
                        BETA += 1
                    elif check_button_click(x, y) == 25:
                        BETA -= 1
                    elif check_button_click(x, y) == 16:
                        stop_generation += 50
                    elif check_button_click(x, y) == 26:
                        stop_generation -= 50
                    initialize()

        # 更新遊戲
        if game_started:
            if generation < stop_generation:
                delta_pheromone = np.zeros((num_cols, num_rows))
                ants = [AntWorker(distance_data, pheromone_data, ALPHA, BETA) for _ in range(NUMBER_OF_ANT)]
                
                for ant in ants:
                    Update_bool = ant.run_path()
                    if not Update_bool:
                        ant.release_pheromone(delta_pheromone)
                    if ant.totol_distance < best_value and not Update_bool:
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

                                # 更新顯示
                draw_toolbar()
                draw_variable()
                draw_generation_count()
                draw_best_path_count()
                pygame.display.update()
            else:
                game_started = not game_started
                # running = False # 這個是方便跑實驗用的
print(best_value)
# 關閉 Pygame
pygame.quit()
