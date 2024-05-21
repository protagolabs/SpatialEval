#!/bin/bash

set -e
export PYTHONPATH=.:$PYTHONPATH

# MODELS="Qwen/CodeQwen1.5-7B-Chat Qwen/Qwen1.5-7B-Chat"
# MODELS="internlm/internlm2-chat-7b 01-ai/Yi-1.5-9B-Chat mistralai/Mixtral-8x7B-Instruct-v0.1"
# MODELS="deepseek-ai/DeepSeek-V2-Lite-Chat 01-ai/Yi-1.5-34B-Chat"
MODELS=(
    # "meta-llama/Llama-2-7b-chat-hf"
    # "meta-llama/Llama-2-13b-chat-hf"
    # "internlm/internlm2-chat-1_8b"
    # "internlm/internlm2-chat-20b"
    "deepseek-ai/DeepSeek-V2-Lite-Chat"
    "meta-llama/Meta-Llama-3-70B-Instruct"
    "deepseek-ai/DeepSeek-V2-Chat"
    "mistralai/Mixtral-8x7B-Instruct-v0.1"
)

for MODEL in $MODELS
do
    echo "Running $MODEL"
    python 2d_grid_point/eval_2d_grid.py --path=./data/exp01/2d_grid_samples50_points10_size10.json --model=$MODEL
done

# MODEL="01-ai/Yi-1.5-34B-Chat"
# echo "Running $MODEL"
# python 2d_grid_point/eval_2d_grid.py --path=./data/exp01/2d_grid_samples50_points10_size10.json --model=$MODEL

