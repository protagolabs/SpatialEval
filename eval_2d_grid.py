from utils.chat_models import OAI_MODEL_4, OpenAIChatModel
import json, sys, os, re

baseline_prompt = """There is a {N}*{N} grid:
<grid>
{empty_grid}
</grid>
```

Draw the following points on the grid:
{points}

"""

def compare_grid(pred, label):
    if pred == label:
        return 1

if __name__ == "__main__":
    chat_model = OpenAIChatModel(OAI_MODEL_4, temperature=0.0)

    # path = "data/2d_grid_samples50_points10_size10.json"
    path = sys.argv[1]
    assert os.path.exists(path), f"File {path} does not exist."

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

        resp = ""
        rgenerator = chat_model.stream_response(messages=messages)
        for text_chunk in rgenerator:
            resp += text_chunk
            print (text_chunk, end="", flush=True)
        print ()

        # resp = chat_model.response(messages=messages)
        # print (resp)

        extract_grid = re.compile(r"<grid>(.*)</grid>", re.DOTALL)
        grid = extract_grid.findall(resp)[0]
        print (grid)
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
    