
import csv
import math

csv_file_path = 'newgrid_2.csv'
csv_output_file_path = 'newgrid_2_with_columns.csv'

mapsize = []
percentage = []
num_obstacles = []
obstacles = []
dmethod = []
astar = []
min_steps = []
gpt4output = []
gpt4summary = []
gpt4 = []
length = []




with open(csv_file_path, 'r', newline='') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        mapsize.append(row['mapsize'])
        percentage.append(row['percentage'])
        num_obstacles.append(row['Num_obstacles'])
        obstacles.append(eval(row['obstacles']))
        dmethod.append(eval(row['dmethod']))
        astar.append(eval(row['astar']))
        min_steps.append(row['#minimum steps'])
        gpt4output.append(row['gpt4output'])
        gpt4summary.append(row['gpt4summary'])
        
        
        try:
            gpt4.append(eval(row['gpt4']))
        except:
            gpt4.append([])

        length.append(row['length'])


def calculate_distance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


reason_list = []
check_list = []

#Compare
for i, (o_coords, d_coords, a_coords, g_coords) in enumerate(zip(obstacles, dmethod, astar, gpt4)):

    if len(g_coords) > 3:
        valid_distance = all(
                calculate_distance(g_coords[j], g_coords[j + 1]) == 1
                for j in range(len(g_coords) - 1)
            )

        if valid_distance:
            if g_coords[0] == d_coords[0] and g_coords[-1] == d_coords[-1]:
                no_overlap = all(coord not in o_coords for coord in g_coords)
                if no_overlap:
                    if len(g_coords) == len(d_coords):
                        reason_list.append(f"Row {i + 1}: Correct - shortest path")
                        check_list.append("Y")
                    else:
                        reason_list.append(f"Row {i + 1}: Wrong - Path but not the shortest path")
                        check_list.append("N")
                else:
                    reason_list.append(f"Row {i + 1}: Wrong - Over the obstacles")
                    check_list.append("N")
            else:
                reason_list.append(f"Row {i + 1}: Wrong - invalid path - 1")
                check_list.append("N")
        else:
            reason_list.append(f"Row {i + 1}: Wrong - Distance is not 1")
            check_list.append("N")
    else:
        reason_list.append(f"Row {i + 1}: Wrong - Invalid path - 2")
        check_list.append("N")


with open(csv_output_file_path, 'w', newline='') as output_file:
    fieldnames = ['mapsize', 'percentage', 'Num_obstacles', 'obstacles', 'dmethod', 'astar',
                  '#minimum steps', 'gpt4output', 'gpt4summary', 'gpt4', 'gpt4length',
                  'reason', 'check']
    csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)

    csv_writer.writeheader()
    for i in range(len(mapsize)):
        csv_writer.writerow({
            'mapsize': mapsize[i],
            'percentage': percentage[i],
            'Num_obstacles': num_obstacles[i],
            'obstacles': str(obstacles[i]),
            'dmethod': str(dmethod[i]),
            'astar': str(astar[i]),
            '#minimum steps': min_steps[i],
            'gpt4output': gpt4output[i],
            'gpt4summary': gpt4summary[i],
            'gpt4': str(gpt4[i]),
            'gpt4length': length[i],
            'reason': reason_list[i],
            'check': check_list[i]
        })

    


        
