# utils/constants.py

FPS_RUN = 10
FPS_STOP = 60

Q = 100
weighted_dict = {1: 1, 2: 3, 3: 5}

# 相鄰的網格方向
direction = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1)]

# 定義地圖大小和網格大小
map_width = 1000
map_height = 1000
grid_size = 25

num_rows = map_height // grid_size
num_cols = map_width // grid_size