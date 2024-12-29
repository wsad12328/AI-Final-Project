from ant_base import AntBase
from utils.constants import Q, num_rows, num_cols

class AntWorker(AntBase):
    def __init__(self, distance_data, pheromone_data, ALPHA, BETA):
        super().__init__(distance_data, pheromone_data, ALPHA, BETA)

    def run_path(self):
        death_flag = False
        while not self.has_reached_goal() and not self.is_dead(death_flag):
            death_flag = self.select()
        return death_flag

    def has_reached_goal(self):
        return self.current_city[0] == num_rows - 1 and self.current_city[1] == num_cols - 1

    def is_dead(self, death_flag):
        return death_flag or self.move_count > num_rows * num_cols

    def release_pheromone(self, delta_pheromone):
        for city in self.path:
            self.add_pheromone(delta_pheromone, city)

    def add_pheromone(self, delta_pheromone, city):
        delta_pheromone[city[0]][city[1]] += (Q / self.totol_distance)