from typing import List, Dict, Union
import tiktoken

encodings = {
    "gpt-3.5-turbo": tiktoken.encoding_for_model(model_name="gpt-3.5-turbo")
}

OAI_PRICE_DICT = {
    "gpt-4o": {
        "prompt": 0.005,
        "completion": 0.015
    },
    "gpt-4-turbo":{
        "prompt": 0.01,
        "completion": 0.03
    },
    "gpt-4-vision": {
        "prompt": 0.01,
        "completion": 0.03
    },
    "gpt-4-0125": {
        "prompt": 0.01,
        "completion": 0.03
    },
    "gpt-4-1106": {
        "prompt": 0.01,
        "completion": 0.03
    },
    "gpt-4": {
        "prompt": 0.03,
        "completion": 0.06
    },
    "gpt-4-32k": {
        "prompt": 0.06,
        "completion": 0.12
    },
    "gpt-3.5-turbo-1106": {
        "prompt": 0.001,
        "completion": 0.002
    },
    "gpt-3.5-turbo": {
        "prompt": 0.0015,
        "completion": 0.002
    },
    "gpt-3.5-turbo-16k": {
        "prompt": 0.003,
        "completion": 0.004
    }
}

def get_token_num(messages: Union[str, List[Dict], List[str]], model_name="gpt-3.5-turbo") -> int:
    if not messages:
        return 0
    if model_name not in encodings:
        encodings[model_name] = tiktoken.encoding_for_model(model_name)
    encoding = encodings[model_name]
    if isinstance(messages, str):
        return len(encoding.encode(messages))
    elif isinstance(messages, list) and isinstance(messages[0], str):
        return sum([len(encoding.encode(m)) for m in messages])
    elif isinstance(messages, list) and isinstance(messages[0], dict):
        pass
    else:
        raise ValueError(f"Got unknown type {type(messages)}, messages: {messages}")

    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

def get_oai_fees(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    if model_name.startswith("gpt-4o"):
        model_name = "gpt-4o"
    elif model_name.startswith("gpt-4-turbo"):
        model_name = "gpt-4-turbo"
    elif model_name.startswith("gpt-4-vision"):
        model_name = "gpt-4-vision"
    elif model_name.startswith("gpt-4-1106"):
        model_name = "gpt-4-1106"
    elif model_name.startswith("gpt-4-0125"):
        model_name = "gpt-4-0125"
    elif model_name.startswith("gpt-4-32k"):
        model_name = "gpt-4-32k"
    elif model_name.startswith("gpt-4"):
        model_name = "gpt-4"
    elif model_name.startswith("gpt-3.5-turbo-16k"):
        model_name = "gpt-3.5-turbo-16k"
    elif model_name.startswith("gpt-3.5-turbo"):
        model_name = "gpt-3.5-turbo"
    else:
        raise ValueError(f"Unknown model name {model_name}")

    # print (f"Model name used for billing: {model_name}")
    if model_name not in OAI_PRICE_DICT:
        return -1
    return (OAI_PRICE_DICT[model_name]["prompt"] * prompt_tokens + OAI_PRICE_DICT[model_name]["completion"] * completion_tokens) / 1000
