import random
import numpy as np
from itertools import accumulate
import sys

# 螞蟻的參數
MAX_ITER = 400
EVAPORATE_RATE_1 = 0.9
EVAPORATE_RATE_2 = 0.6
EVAPORATE_RATE_3 = 0.3
Q = 100
ALPHA = 2
BETA = 2
NUMBER_OF_ANT = 250
num_rows = 40
num_cols = 40


# 相鄰的網格方向
direction = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1)]
weighted_dict = {1:1,2:3,3:5}

np.random.seed(1000)
label_map_data = np.random.randint(1, 4, size=(num_rows, num_cols))

np.fill_diagonal(label_map_data, 1)
print(label_map_data)
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
# print(distance_data)

# for i in range(num_rows):
#     for j in range(num_cols):
#         print(label_map_data[i, j],end=" ")
#     print()


def update_pheromone():
    for i in range(num_rows):
        for j in range(num_cols):
            if(label_map_data[i, j] == 1):
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_1
            elif(label_map_data[i, j] == 2):
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_2
            elif(label_map_data[i, j] == 3):
                pheromone_data[i, j] = pheromone_data[i, j] * EVAPORATE_RATE_3



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
        
        # for i in range(num_rows):
        #     for j in range(num_cols):
        #         print(self.legal_city[i, j],end=" ")
        #     print()
        
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
                    
                    # print(select_candidate_probability)
        # print(select_candidate_direction)
        # 輪盤法
        # print(f"direct: {select_candidate_direction}")
        # print("=================")
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
                break
            elif(self.move_count > num_rows*num_cols):
                break

            death_flag = self.select()
        return death_flag
    
    def release_pheromone(self):
        # print(self.path)     
        for city in self.path:
            if(label_map_data[city[0]][city[1]] == 1):
                pheromone_data[city[0]][city[1]] += (Q / self.totol_distance * (1 - EVAPORATE_RATE_1))
            elif(label_map_data[city[0]][city[1]] == 2):
                pheromone_data[num_rows-1][num_cols-1] += (Q / self.totol_distance * (1 - EVAPORATE_RATE_2))
            elif(label_map_data[city[0]][city[1]] == 3):
                pheromone_data[num_rows-1][num_cols-1] += (Q / self.totol_distance * (1 - EVAPORATE_RATE_3))

best_value = sys.maxsize
best_solution = []
for i in range(MAX_ITER):
    for j in range(NUMBER_OF_ANT):
        ant = Ant()
        Update_bool = ant.run_path()
        if(not Update_bool):
            ant.release_pheromone()
        if ant.totol_distance < best_value and not(Update_bool):
            best_value = ant.totol_distance
            best_solution = ant.path
    update_pheromone()
# for i in range(num_rows):
#     for j in range(num_cols):
#         print(pheromone_data[i, j],end=" ")
#     print()

print(f"Best value: {best_value}")
print(best_solution)

        



