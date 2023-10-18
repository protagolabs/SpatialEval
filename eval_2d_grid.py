from utils.chat_models import OAI_MODEL_4, OpenAIChatModel
import json

baseline_prompt = """There is a {N}*{N} grid:
```
{empty_grid}
```

Draw the following points on the grid:
{points}

"""




chat_model = OpenAIChatModel(OAI_MODEL_4, temperature=1.0)

path = "data/2d_grid_samples50_points10_size10.json"

with open(path, "r") as f:
    test_set = json.load(f)

for example in test_set[:1]:
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
