from utils.chat_models import OpenAIChatModel, HFChatModel
import json, sys, os, re
import argparse

baseline_prompt = """There is a {N}*{N} grid:
<grid>
{empty_grid}
</grid>

Draw the following points on the grid:
{points}

You must wrap the grid with <grid> and </grid> tags.
"""

def compare_grid(pred, label):
    if pred.strip() == label.strip():
        return 1

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Path to the json file.")
    parser.add_argument("--model", type=str, help="openai model name.", default="gpt-3.5-turbo-0125")
    args = parser.parse_args()
    return args

def extract_grid_from_response(response):
    extract_grid = re.compile(r"<grid>(.*)</grid>", re.DOTALL)
    grids = extract_grid.findall(response)
    # If we doesn't find any grid, return empty string
    if len(grids) == 0:
        return ""

    return grids[0]

def parser_points_str(points_str):
    """
        Input: O: j, 7\nC: g, 7 
        Output: 
            [
                {"char": "O", "x": "j", "y": "7"},
                {"char": "C", "x": "g", "y": "7"}
            ]
    """
    lines = points_str.split("\n")
    triplet_points = []
    for l in lines:
        if l.strip():
            char, x, y = l.split(":")[0].strip(), l.split(":")[1].split(",")[0].strip(), l.split(":")[1].split(",")[1].strip()
            triplet_points.append({"char": char, "x": x, "y": y})
    return triplet_points

def extract_triplet_point(text_grid):
    """
        Input:
              a b c d e f g h i j 
            0 . . . . . . . . . . 
            1 . . . . . . . . G . 
            2 . . . D . . . . . . 

        Output:
            [
                {"char": "D", "x": "d", "y": "2"},
                {"char": "G", "x": "i", "y": "1"}
            ]

    """
    text_grid = text_grid.lstrip("\n")
    lines = text_grid.split("\n")
    triplet_points = []

    for i in range(1, len(lines)-1):
        for j in range(2, len(lines[i])-1):
            if lines[i][j] not in [".", " "]:
                triplet_points.append({"char": lines[i][j], "x": chr(ord('a')+(j//2-1)), "y": str(i-1)})
    return triplet_points

def compare_triplet_points(ground_turth: list[dict], prediction: list[dict]):
    """
        Input:
            ground_truth = [
                {"char": "O", "x": "j", "y": "7"},
                {"char": "C", "x": "g", "y": "7"}
            ]
            prediction = [
                {"char": "O", "x": "j", "y": "7"},
                {"char": "C", "x": "c", "y": "7"}
            ]
        Output:
            {
                "correct_count": 1
                "correct_points": [ {"char": "O", "x": "j", "y": "7"} ]
                "missing_points": [ {"char": "C", "x": "g", "y": "7"} ]
            }
    """
    correct_count = 0
    correct_points = []
    missing_points = []
    hash_prediction = {f"mark:{p['char']}_x:{p['x']}_y:{p['y']}": p for p in prediction}

    for g in ground_turth:
        if f"mark:{g['char']}_x:{g['x']}_y:{g['y']}" in hash_prediction:
            correct_count += 1
            correct_points.append(g)
        else:
            missing_points.append(g)
            
    return {"correct_count": correct_count, "correct_points": correct_points, "missing_points": missing_points}

def calculate_mean_points_recall(pred_data):
    points_recall_list = []

    for example in pred_data:
        ground_truth = parser_points_str(example['points'])
        prediction = extract_triplet_point(example['llm_final_answer'])
        result = compare_triplet_points(ground_truth, prediction)
        points_recall_list.append(result['correct_count']/len(ground_truth))
        
    return {
        "mean_points_recall": (sum(points_recall_list)/len(points_recall_list))
    }

if __name__ == "__main__":
    args = setup_args()
    path = args.path
    model = args.model
    assert os.path.exists(path), f"File {path} does not exist."

    os.makedirs("tmp/exp01", exist_ok=True)

    # 1. Init Model
    if model.startswith("gpt-"):
        chat_model = OpenAIChatModel(model, temperature=0.0)
    else:
        chat_model = HFChatModel(model, temperature=0.0)

    if "/" in model:
        model_name = model.split("/")[-1]
    else:
        model_name = model

    with open(path, "r") as f:
        test_set = json.load(f)

    correct = 0
    total_samples = len(test_set)
    total_fees = 0

    for i, example in enumerate(test_set):
        prompt = baseline_prompt.format(**example)
        print (prompt)

        messages = [
            {
                "role": 'user',
                "content": prompt
            }
        ]

        resp, cost = chat_model.response(messages=messages)
        total_fees += cost['fees']
        print (resp)

        # 
        grid = extract_grid_from_response(resp)

        example["llm_prediction"] = resp
        example["llm_final_answer"] = grid

        print (f"Progress: {i+1}/{total_samples}")
        if compare_grid(grid, label=example["ground_truth"]):
            correct += 1
            print (f"Correct: {correct}/{total_samples}")
            print ("Corret!")
        else:
            print (f"Error! \nGround truth:\n{example['ground_truth']}")
            # TODO: get error points number

    save_path = path.replace(".json", f"_{model_name}.json")
    with open(save_path, "w") as f:
        json.dump(test_set, f, indent=4)

    print (f"Accuracy: {correct}/{total_samples}")
    print (f"mean points recall: {calculate_mean_points_recall(test_set)}")

    if model_name.startswith("gpt-") or model_name.startswith("claude"):
        print (f"Total fees: {total_fees}")

    # Save metric 
    with open(f"./tmp/exp01/evaluation_{model_name}.json", "w") as f:
        metric = {
            "accuracy": correct/total_samples,
            "mean_points_recall": calculate_mean_points_recall(test_set)['mean_points_recall']
        }
        if model_name.startswith("gpt-") or model_name.startswith("claude"):
            metric["total_fees"] = total_fees
        json.dump(metric, f, indent=4)
    
    print (f"Model_name: {model_name}, evaluation result: ./tmp/exp01/evaluation_{model_name}.json")