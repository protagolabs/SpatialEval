from path_planning.grid import Grid
from path_planning.dijkstra import dijkstra
from path_planning.astar import a_star
import csv
import time
import tqdm
from utils.chat_models import OpenAIChatModel

def get_shortest_path(input_file_path, output_file_path):
    rows = []

    with open(input_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader, None) 

        for row in csv_reader:
            mapsize, percentage, Num_obstacles, obstacles = row
            x, y = map(int, mapsize.split(' * '))
            obs_coords = eval(obstacles) 

            g = Grid(x, y, obstacles=obs_coords)
            src = (0, 0)
            dest = (x-1, y-1)

            nodes = g.get_nodes()
            path1 = dijkstra(g, src, dest)
            path2 = a_star(g, src, dest)

            row.extend([str(path1), str(path2),len(path1)])
            rows.append(row)

    with open(output_file_path, 'w', newline='') as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(header + ['dmethod', 'astar', 'mini_len'])
        csv_writer.writerows(rows)

    print("New CSV file with path1 and path2 columns created:", output_file_path)


def get_gpt_answer(model_name="gpt-4"):
    i = 0

    # Read obstacle coordinates from a CSV file
    with open('RandomObs_with_paths.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        

        for row in tqdm(csv_reader):
            i = i+1
            obs_coordinates = eval(row['obstacles'])
            x, y = map(int, row['mapsize'].split(' * ')) 


            p1 = f"A {x} * {y} grid map with {(x)*(y)} blue dots(with x from 0 to {x} and y from 0 to {y}) representing coordinates and lines connecting them. Each adjacent coordinate is connected by a blue straight line, either horizontally or vertically, and the distance of 1. The grid starts from (0,0) at the bottom left and goes up to"
            p2 = f"{x-1} * {y-1} at the top right. Obstacles on the grid are represented by the absence of blue dots at specific coordinates, as well as the missing adjacent blue lines connecting them. The coordinates with obstacles are:"
            p3 = str(obs_coordinates)
            p4 = f" with x and y from 0 to {x-1}, corresponding to the coordinate system. Thus, I need to find the shortest path from (0,0)"
            p5 = f"to {x-1} * {y-1} to solve this problem you are required 1. moving each step either horizontally or vertically and avoiding obstacles by distance of 1. 2. don't recap the problem, please get straight to solve it 3. you will get the history of this problem which you did before 4. only need text-based path coordinates results "

            my_content = p1 + p2 + p3 + p4 + p5
            request_message = [
                    {"role": "system", "content": "You are a math specialist."},
                    {"role": "user", "content": f"Solve the math problem: {my_content}."}
            ]

            chat_model = OpenAIChatModel(model_name=model_name, temperature=0, seed=2023)
            answer = chat_model.response(messages=request_message)
            print("startxinyao")
            print(f"{i}")
            print(f"Math problem: {my_content}")
            print(f"Math specialist's answer: {answer}")
            print("endxinyao")

            # Extract the path coordinates
            message_to_exact_answer = [
                {"role": "user", "content": f"extract the math answer and form the path coordinates to a list, :{answer}, I only need the coordinate path answer(begin with [ and end with ]), don't recap the problem or give me ideas of soling the problem."},
            ]
            final_answer = chat_model.response(messages=message_to_exact_answer)
            print("starthu")
            print(final_answer)
            print("endhu")
            time.sleep(1)


if __name__ == "__main__":
    input_file_path = 'RandomObs.csv'  
    output_file_path = 'RandomObs_with_paths.csv' 
    get_shortest_path(input_file_path, output_file_path)
