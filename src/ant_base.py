import numpy as np
import random
from itertools import accumulate
from utils.constants import direction, num_rows, num_cols

class AntBase:
    def __init__(self, distance_data, pheromone_data, alpha, beta):
        self.distance_data = distance_data
        self.pheromone_data = pheromone_data
        self.alpha = alpha
        self.beta = beta
        self.initialize_ant()

    def initialize_ant(self):
        self.path = []
        self.move_count = 0
        self.totol_distance = 0
        self.current_city = (0, 0)
        self.legal_city = np.ones((num_cols, num_rows))
        self.path.append(self.current_city)
        self.legal_city[self.current_city[0]][self.current_city[1]] = False
        self.move_count += 1

    def select(self):
        select_candidate_direction, select_candidate_probability = self.get_candidates()
        if len(select_candidate_probability) != 0:
            index = self.roulette_wheel_selection(select_candidate_probability)
            self.move_to_next_city(select_candidate_direction[index])
        else:
            return True

    def get_candidates(self):
        select_candidate_direction = []
        select_candidate_probability = []
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
                    distance = self.distance_data[
                        self.current_city[0], self.current_city[1], i
                    ]
                    prob = (
                        self.pheromone_data[x_coordinate][y_coordiante] ** self.alpha
                        + (1 / distance) ** self.beta
                    )
                    select_candidate_direction.append(i)
                    select_candidate_probability.append(prob)
        return select_candidate_direction, select_candidate_probability

    def roulette_wheel_selection(self, probabilities):
        total_prob = sum(probabilities)
        probabilities = [prob / total_prob for prob in probabilities]
        probabilities = list(accumulate(probabilities))
        random_value = random.uniform(0, 1)
        index = 0
        for accumulate_prob in probabilities:
            if random_value > accumulate_prob:
                index += 1
        return index

    def move_to_next_city(self, direction_index):
        next_x = self.current_city[0] + direction[direction_index][0]
        next_y = self.current_city[1] + direction[direction_index][1]
        self.totol_distance += self.distance_data[
            self.current_city[0],
            self.current_city[1],
            direction_index,
        ]
        self.current_city = (next_x, next_y)
        self.path.append(self.current_city)
        self.legal_city[self.current_city[0]][self.current_city[1]] = False
        self.move_count += 1