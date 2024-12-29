import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Ant Colony Optimization")
    parser.add_argument("--grass_evaporation_rate", type=float, default=0.6, help="Evaporation rate for grass")
    parser.add_argument("--soil_evaporation_rate", type=float, default=0.6, help="Evaporation rate for soil")
    parser.add_argument("--sand_evaporation_rate", type=float, default=0.6, help="Evaporation rate for sand")
    parser.add_argument("--alpha", type=int, default=3, help="Alpha parameter")
    parser.add_argument("--beta", type=int, default=3, help="Beta parameter")
    parser.add_argument("--random_seed", type=int, default=1000, help="Random seed")
    parser.add_argument("--num_ants", type=int, default=200, help="Number of ants")
    return parser.parse_args()