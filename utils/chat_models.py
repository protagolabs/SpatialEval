from abc import ABC, abstractmethod
from typing import (
    List, Dict, Generator
)
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
from .msg_utils import get_token_num, get_oai_fees
# from ..utils.logger_utils import logger as chat_logger

OAI_MODEL_3_5 = "gpt-3.5-turbo-0613"
OAI_MODEL_4 = "gpt-4"

class ChatModel(ABC):
    @abstractmethod
    def stream_response(self, messages: List[Dict]) -> Generator[str, None, None]:
        """
        """

    @abstractmethod
    def response(self, messages: List[Dict]) -> str:
        """
        """

class OpenAIChatModel(ChatModel):
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.0, **kwargs) -> None:
        self.model = model
        self.temperature = temperature
        self.kwargs = {}

    @retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
    def stream_response(self, messages: List[Dict]) -> Generator[str, None, None]:

        rbody_generator = openai.ChatCompletion.create(model=self.model, messages=messages, stream=True,
                                                       temperature=self.temperature)

        prompt_tokens = get_token_num(messages=messages)
        completion_tokens = 0
        for chunk in rbody_generator:
            content = chunk["choices"][0]["delta"].get("content", "")
            # print(content, end="", flush=True)
            completion_tokens += get_token_num(content)
            yield content

        fees = get_oai_fees(model_name=self.model, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
        # print (f"model name: {self.model}")
        # chat_logger.info(
        #     f"[OpenAIChatModel][fees] {fees}, Prompt tokens: {prompt_tokens}, completion tokens: {completion_tokens}")

    @retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
    def response(self, messages: List[Dict], functions=None, function_call="auto") -> str:

        if functions:
            rbody = openai.ChatCompletion.create(model=self.model, messages=messages, stream=False,
                                             temperature=self.temperature, functions=functions, function_call=function_call)
        else:
            rbody = openai.ChatCompletion.create(model=self.model, messages=messages, stream=False,
                                             temperature=self.temperature)

        prompt_tokens = rbody['usage']['prompt_tokens']
        completion_tokens = rbody['usage']['completion_tokens']
        # print (f"model name: {self.model}")
        fees = get_oai_fees(model_name=self.model, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
        # chat_logger.info(
        #     f"[OpenAIChatModel][fees] {fees}, Prompt tokens: {prompt_tokens}, completion tokens: {completion_tokens}")

        # print (rbody)
        if "function_call" in rbody.choices[0]['message']:
            return rbody.choices[0]['message']['function_call']["arguments"]
        return rbody.choices[0].message.content

class ClaudeChatModel(ChatModel):
    def stream_response(self, messages: List[Dict]) -> Generator[str, None, None]:
        raise NotImplementedError
    def response(self, messages: List[Dict]) -> str:
        raise NotImplementedError

class GaiaChatModel(ChatModel):
    model = "Gaia-v0.1"
    base_url = ""
    header = {}
    target_role = "Gaia"
    def stream_response(self, messages: List[Dict]) -> Generator[str, None, None]:
        rbody_generator = openai.ChatCompletion.create(openai_api_base=self.base_url, headers=self.header, 
                                                        model=self.model, messages=messages, stream=True, temperature=self.temperature, 
                                                        target_role=self.target_role)
        for chunk in rbody_generator:
            content = chunk["choices"][0]["delta"].get("content", "")
            # print(content, end="", flush=True)
            yield content

    def response(self, messages: List[Dict]) -> str:
        raise NotImplementedError
