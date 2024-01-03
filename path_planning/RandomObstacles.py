import random
import csv

# Create a CSV file to store the data
with open('RandomObs.csv', mode='w', newline='') as file:
    # Define the CSV writer
    csv_writer = csv.writer(file)
    
    # Write the header row
    csv_writer.writerow(['mapsize', 'percentage', 'Num_obstacles', 'obstacles'])
    
    for j in range(0,10): # 10 groups of each 

    # Define the ranges
        for i in range(0, 9):
            XYmax = i + 2
            
            percentages = [0, 0.05, 0.10, 0.15, 0.20, 0.25]
            coordinates_by_percentage = {percentage: {'coordinates': [], 'num_coordinates': 0} for percentage in percentages}
            for percentage in percentages:
                num_coordinates = int(((XYmax + 1) ** 2 * percentage))
                coordinates_list = []  

                while len(coordinates_list) < num_coordinates:
                    x = random.randint(0, XYmax)
                    y = random.randint(0, XYmax)
                    if (x, y) != (0, 0) and (x, y) != (XYmax, XYmax):
                        if (x, y) not in coordinates_list: #regenerate points if repeating
                            coordinates_list.append((x, y))
                        else:
                            continue
                    else: 
                        continue

                coordinates_by_percentage[percentage]['coordinates'] = coordinates_list
                coordinates_by_percentage[percentage]['num_coordinates'] = len(coordinates_list)

                list_name = f"list_mapSize_{XYmax}*{XYmax}_percentage_{percentage}%"
                locals()[list_name] = coordinates_list

            for percentage in percentages:
                map_size = f"{XYmax+1} * {XYmax+1}"
                num_coordinates = coordinates_by_percentage[percentage]['num_coordinates']
                coordinates_list = coordinates_by_percentage[percentage]['coordinates']

                # Print the coordinates data
                # print(f"mapsize: {map_size}")
                # print(f"percentage: {percentage * 100}%")
                # print(f"# obstacles: {num_coordinates}")
                # print(f"{coordinates_list}")
                

                # Save the data to the CSV file
                csv_writer.writerow([map_size, f"{percentage * 100}%", num_coordinates, coordinates_list])

print("Coordinates data has been saved to 'RandomObs.csv'")
