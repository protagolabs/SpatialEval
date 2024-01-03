import re
import csv

fff = "your_file"
input_file_path = f'{fff}.txt'
output_file_path = f'{fff}.csv'

answers = []
alternative_answers = []

answer_pattern = r'startxinyao(.*?)endxinyao'
alternative_pattern = r'starthu(.*?)endhu'


with open(input_file_path, 'r') as file:
    file_contents = file.read()

answers.extend(re.findall(answer_pattern, file_contents, re.DOTALL))
alternative_answers.extend(re.findall(alternative_pattern, file_contents, re.DOTALL))


max_length = max(len(answers), len(alternative_answers))

csv_data = []

for i in range(max_length):
    row = []
    
    if i < len(answers):
        row.append(answers[i])
    else:
        row.append('')  

    if i < len(alternative_answers):
        row.append(alternative_answers[i])
    else:
        row.append('')  
    
    csv_data.append(row)

with open(output_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Answer', 'Alternative Answer'])
    csv_writer.writerows(csv_data)

print(f'{len(answers)} answers and {len(alternative_answers)} alternative answers extracted and saved to {output_file_path}.')




##Cleanup path = 只需要把包含o and ...的去掉 -wrong_just for backup

import ast

input_csv_path = f"{fff}.csv"
output_csv_path = f"{fff}_cleanup.csv"  

with open(input_csv_path, 'r', newline='') as input_csv_file: 
    csv_reader = csv.reader(input_csv_file)
    with open(output_csv_path, 'w', newline='') as output_csv_file:
        csv_writer = csv.writer(output_csv_file)
        for row in csv_reader:
            if "o" in row[1] or "..." in row[1] or "a" in row[1]:
                alternative_answer = []
                length = 0
                output_row = [row[0], row[1], alternative_answer, length]

            elif row[1].count("[") > 1:
                alternative_answer = []
                length = 0
                output_row = [row[0], row[1], alternative_answer, length]

            else:
                alternative_answer = row[1]
                length = len(ast.literal_eval(row[1]))
                output_row = [row[0], row[1], alternative_answer, length]
                    

            csv_writer.writerow(output_row)

            
                
