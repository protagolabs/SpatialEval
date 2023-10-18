from langchain.schema import (
    AIMessage,
    BaseMessage,
    ChatGeneration,
    ChatMessage,
    ChatResult,
    HumanMessage,
    SystemMessage,
)
import tiktoken
from langchain.prompts.chat import ChatMessagePromptTemplate
from typing import Dict, List, Union

# dollars per 1k tokens, REF: https://openai.com/pricings
OAI_PRICE_DICT = {
    "gpt-4": {
        "prompt": 0.03,
        "completion": 0.06
    },
    "gpt-4-32k": {
        "prompt": 0.06,
        "completion": 0.12
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

def convert_message_to_dict(message: BaseMessage) -> Dict:
    """ 根据传入的 BaseMessage, 创建包含 role和content 两个key的字典. 如果 BaseMessage 中有 name, 则也加入字典中.

    Args:
        message (BaseMessage): _description_

    Raises:
        ValueError: _description_

    Returns:
        Dict: _description_
    """

    if isinstance(message, ChatMessage):
        message_dict = {"role": message.role, "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    else:
        raise ValueError(f"Got unknown type {message}")
    if "name" in message.additional_kwargs:
        message_dict["name"] = message.additional_kwargs["name"]
    return message_dict

def get_token_num(messages: Union[str, List[Dict], List[str], List[BaseMessage]], model_name="gpt-3.5-turbo") -> int:
    if not messages:
        return 0
    
    encoding = tiktoken.encoding_for_model(model_name)
    if isinstance(messages, str):
        return len(encoding.encode(messages))
    elif isinstance(messages, list) and isinstance(messages[0], str):
        return sum([len(encoding.encode(m)) for m in messages])
    elif isinstance(messages, list) and isinstance(messages[0], dict):
        pass
    elif isinstance(messages, list) and isinstance(messages[0], BaseMessage):
        messages = [convert_message_to_dict(m) for m in messages]
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

def convert_qa_to_lctemplate(pairs: List[Dict]) -> List[ChatMessagePromptTemplate]:
    lc_templates = []
    for _pair in pairs:
        lc_templates.extend(
            [
                ChatMessagePromptTemplate.from_template(template=_pair["question"], role="user"),
                ChatMessagePromptTemplate.from_template(template=_pair["response"], role="assistant")
            ]
        )
    return lc_templates

def get_oai_fees(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    if model_name.startswith("gpt-4-32k"):
        model_name = "gpt-4-32k"
    elif model_name.startswith("gpt-4"):
        model_name = "gpt-4"
    elif model_name.startswith("gpt-3.5-turbo-16k"):
        model_name = "gpt-3.5-turbo-16k"
    elif model_name.startswith("gpt-3.5-turbo"):
        model_name = "gpt-3.5-turbo"
    else:
        raise ValueError(f"Unknown model name {model_name}")

    print (f"Model name used for billing: {model_name}")
    if model_name not in OAI_PRICE_DICT:
        return -1
    return (OAI_PRICE_DICT[model_name]["prompt"] * prompt_tokens + OAI_PRICE_DICT[model_name]["completion"] * completion_tokens) / 1000

def get_oai_embedding_fees(text: Union[str, List[str]], model_name: str="text-embedding-ada-002") -> float:
    if isinstance(text, str):
        text = [text]
    
    tokens = get_token_num(text, model_name=model_name)
    return tokens * 0.0001 / 1000

def message_to_str(messages_list):
    s = "[START]\n"
    for i, cur_dct in enumerate(messages_list):
        s += f"[Turn] {i} [{cur_dct['role']}]: {cur_dct['content']}\n"
    s += "[END]\n"
    return s
