import time
import traceback
from abc import ABC, abstractmethod
from typing import (
    List, Dict, Generator
)

from openai import OpenAI, AsyncOpenAI
from .msg_utils import get_oai_fees, get_token_num
import asyncio
import os
import logging as logger
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChatModel(ABC):
    @abstractmethod
    def stream_response(self, messages: List[Dict]) -> Generator[str, None, None]:
        """
        """

    @abstractmethod
    def response(self, messages: List[Dict]) -> str:
        """
        """

LLAMA_3_INSTRUCT_MODELS = [
    "Meta-Llama-3-8B-Instruct",
]


class HFChatModel(ChatModel):
    def __init__(self, model: str, temperature: float = 0.0, top_p=1.0) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(
            model,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        self.temperature = temperature
        self.top_p = top_p
        self.model_name = model.strip("/")[-1]

        if self.model_name in LLAMA_3_INSTRUCT_MODELS:
            self.terminators = [
                self.tokenizer.eos_token_id,
                self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]
        else:
            self.terminators = self.tokenizer.eos_token_id

    def response(self, messages: List[Dict]):
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        outputs = self.model.generate(
            input_ids,
            max_new_tokens=256,
            eos_token_id=self.terminators,
            do_sample=True if self.temperature > 0 else False,
            temperature=self.temperature,
            top_p=0.9,
        )
        response = outputs[0][input_ids.shape[-1]:]
        return self.tokenizer.decode(response, skip_special_tokens=True), {"fees": 0}

    def stream_response(self):
        raise NotImplementedError


class OpenAIChatModel(ChatModel):
    def __init__(self, model: str = "gpt-4-turbo-2024-04-09", temperature: float = 0.0, seed=2023, api_key=None, **kwargs) -> None:
        self.model = model
        self.temperature = temperature
        self.seed = 2023
        self.api_key = api_key
        self.kwargs = {}

    def stream_response(self, messages: List[Dict]) -> Generator[str, None, None]:
        for i in range(3):
            try:
                if self.api_key is None:
                    client = OpenAI(api_key=OPENAI_API_KEY)
                else:
                    client = OpenAI(api_key=self.api_key)

                rbody_generator = client.chat.completions.create(model=self.model, messages=messages, stream=True,
                                                                seed=self.seed, timeout=10,
                                                                temperature=self.temperature)
                for chunk in rbody_generator:
                    yield chunk.choices[0].delta.content
                break
            except Exception as e:
                logger.warning(f"exception happened in response process:{str(e)}")
                print(f"[OpenAI_API][Retry] Timeout, Failed after {i + 1} times")
                time.sleep(1)

    async def astream_response(self, messages: List[Dict]):
        for i in range(3):
            try:
                if self.api_key is None:
                    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
                else:
                    client = AsyncOpenAI(api_key=self.api_key)

                rbody_generator = await client.chat.completions.create(model=self.model,
                                                                        messages=messages,
                                                                        stream=True,
                                                                        seed=self.seed,
                                                                        timeout=10,
                                                                        temperature=self.temperature)
            
                chunk_index = 0
                async for chunk in rbody_generator:
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_index == 0:
                        prompt_tokens = get_token_num(messages=messages, model_name=self.model)
                        completion_tokens = get_token_num(chunk.choices[0].delta.content)
                        fees = get_oai_fees(model_name=self.model, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
                        cost = {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "fees": fees
                        }
                        yield chunk.choices[0].delta.content, cost
                    else:                    
                        completion_tokens = get_token_num(chunk.choices[0].delta.content)
                        fees = get_oai_fees(model_name=self.model, prompt_tokens=0, completion_tokens=completion_tokens)
                        cost = {
                            "prompt_tokens": 0,
                            "completion_tokens": completion_tokens,
                            "fees": fees
                        }
                        yield chunk.choices[0].delta.content, cost
                    chunk_index += 1

                break
            except Exception as e:
                logger.warning(f"exception happened in response process:{str(e)}")
                print(f"[OpenAI_API][Retry] Timeout, Failed after {i + 1} times")
                await asyncio.sleep(1)  # 使用异步版本的sleep

    async def aresponse(self, messages: List[Dict]):
        for i in range(3):
            try:
                if self.api_key is None:
                    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
                else:
                    client = AsyncOpenAI(api_key=self.api_key)
                rbody = await client.chat.completions.create(model=self.model, messages=messages, stream=False,
                                                                seed=self.seed, timeout=60,
                                                                temperature=self.temperature)
                prompt_tokens = rbody.usage.prompt_tokens
                completion_tokens = rbody.usage.completion_tokens

                fees = get_oai_fees(model_name=self.model, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
                cost = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "fees": fees
                }
                return rbody.choices[0].message.content, cost
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                logger.warning(f"exception happened in response process:{str(e)}")
                print (f"[OpenAI_API][Retry] Timeout, Failed after {i+1} times")
                await asyncio.sleep(1)

    def response(self, messages: List[Dict], tools=None, tool_choice="auto") -> str:
        for i in range(3):
            try:
                if self.api_key is None:
                    client = OpenAI(api_key=OPENAI_API_KEY)
                else:
                    client = OpenAI(api_key=self.api_key)

                if tools:
                    rbody = client.chat.completions.create(model=self.model, messages=messages, stream=False,
                                                            seed=self.seed, timeout=30,
                                                            temperature=self.temperature, tools=tools, tool_choice=tool_choice)
                else:
                    rbody = client.chat.completions.create(model=self.model, messages=messages, stream=False,
                                                            seed=self.seed, timeout=30,
                                                            temperature=self.temperature)

                prompt_tokens = rbody.usage.prompt_tokens
                completion_tokens = rbody.usage.completion_tokens
                fees = get_oai_fees(model_name=self.model, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
                # chat_logger.info(
                #     f"[OpenAIChatModel][fees] {fees}, Prompt tokens: {prompt_tokens}, completion tokens: {completion_tokens}")
                cost = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "fees": fees
                }

                if hasattr(rbody.choices[0].message, "tool_calls") and rbody.choices[0].message.tool_calls:
                    return rbody.choices[0].message.tool_calls[0].function.arguments, cost
                return rbody.choices[0].message.content, cost
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                logger.warning(f"exception happened in response process:{str(e)}")
                print (f"[OpenAI_API][Retry] Timeout, Failed after {i+1} times")
                time.sleep(1)
        raise