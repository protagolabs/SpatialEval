from utils.chat_models import OAI_MODEL_4, OpenAIChatModel
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
    if pred == label:
        return 1

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Path to the json file.")
    parser.add_argument("--model", type=str, help="openai model name.", default="gpt-3.5-turbo-0613")
    args = parser.parse_args()
    return args

def extract_grid_from_response(response):
    extract_grid = re.compile(r"<grid>(.*)</grid>", re.DOTALL)
    grids = extract_grid.findall(response)
    # If we doesn't find any grid, return empty string
    if len(grids) == 0:
        return ""

    return grids[0]

if __name__ == "__main__":
    args = setup_args()
    path = args.path
    model = args.model
    assert os.path.exists(path), f"File {path} does not exist."

    chat_model = OpenAIChatModel(model, temperature=0.0)

    with open(path, "r") as f:
        test_set = json.load(f)

    correct = 0
    total_samples = len(test_set)

    for i, example in enumerate(test_set):
        prompt = baseline_prompt.format(**example)
        print (prompt)

        messages = [
            {
                "role": 'user',
                "content": prompt
            }
        ]

        resp = chat_model.response(messages=messages)
        print (resp)

        # 
        grid = extract_grid_from_response(resp)

        example["llm_prediction"] = resp
        example["llm_response"] = grid

        print (f"Progress: {i+1}/{total_samples}")
        if compare_grid(grid, label=example["ground_truth"]):
            correct += 1
            print (f"Correct: {correct}/{total_samples}")
            print ("Corret!")
        else:
            print (f"Error! \nGround truth:\n{example['ground_truth']}")
            # TODO: get error points number

    save_path = path.replace(".json", "_with_pred.json")
    with open(save_path, "w") as f:
        json.dump(test_set, f, indent=4)

    print (f"Accuracy: {correct}/{total_samples}")
    