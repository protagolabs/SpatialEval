
import random
import string
import sys
import json
from pydantic import BaseModel, Field

class Grid2dPoint(BaseModel):
    marks: str = Field(..., length=1)
    x: str = Field(..., regex="[a-z]")
    y: int = Field(..., ge=0)

def draw_empty_grid(n):
    s = "  "
    for i in range(n):
        s += chr( ord("a") + i ) + " "
    s += "\n"

    for i in range(n):
        s += str(i) + " "
        for j in range(n):
            s += ". "
        s += "\n"
    return s

def generate_random_triplets(k, n):
    """
    Generate k random triplets (mark, x, y) in N*N grid.
    """
    triplets = []
    letters = string.ascii_uppercase

    while len(triplets) <= k:
        letter = random.choice(letters)
        x = random.randint(0, n-1)
        y = random.randint(0, n-1)

        triplets.append((letter, chr( ord("a")+x ), y))

    return triplets

def generate_unique_sets(n_samples, k, n):
    """Generate unique sets of triplets.
    
    Args:
        n_samples (int): The number of unique sets to generate.
        k (int): The number of triplets in each set.
        n (int): The maximum size of the 2d-grid.
    """

    unique_sets = set()

    while len(unique_sets) < n_samples:
        triplets = generate_random_triplets(k, n)
        unique_sets.add(tuple(triplets))

    points2chat_sets = []
    for triplets in unique_sets:
        pos2char_dct = {}
        for ele in triplets:
            pos2char_dct[(ele[1], ele[2])] = ele[0]
        points2chat_sets.append(pos2char_dct)

    return points2chat_sets

def points_to_str(points):
    s = ""
    for (x, y), v in points.items():
        s += f"{v}: {x}, {y}\n"
    return s

def draw_points_on_grid(triplets, n):
    # triplets to dict

    # Draw the top axis
    s = "  "
    for i in range(n):
        s += chr( ord("a") + i ) + " "
    s += "\n"

    # Draw the grid
    for i in range(n):
        # Draw the left axis
        s += str(i) + " "
        for j in range(n):
            x = chr( ord("a") + j )
            y = i
            if (x,y) in triplets:
                s += f"{triplets[(x,y)]} "
            else:
                s += ". "
        s += "\n"

    return s

def unit_test():
    points_set = generate_unique_sets(10, 3, 5)
    print (points_set)

    points = {('a', 0): 'M', ('e', 3): 'Q', ('e', 4): 'U'}
    print(draw_points_on_grid(points, 5))

    print (points_to_str(points=points))
    print (draw_empty_grid(5))

if __name__ == "__main__":
    # n_samples=10, k = 3, n = 5

    n_samples = int(sys.argv[1])
    k = int(sys.argv[2])
    n = int(sys.argv[3])

    assert n < 26, "n must be less than 26 in current experiment."

    # n_samples = 50
    # k = 10
    # n = 10
    points_sets = generate_unique_sets(n_samples=n_samples, k=k, n=n)
    examples = []
    for _sets in points_sets:
        points_str = points_to_str(_sets)
        empty_grid = draw_empty_grid(n)
        ground_truth = draw_points_on_grid(_sets, n)
        examples.append(
            {   
                "points": points_str,
                "empty_grid": empty_grid,
                "ground_truth": ground_truth,
                "N": n,
            }
        )
    with open(f"./data/2d_grid_samples{n_samples}_points{k}_size{n}.json", "w") as f:
        json.dump(examples, f, indent=4)
    
