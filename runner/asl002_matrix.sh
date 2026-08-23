#!/bin/bash
# ASL-002 across canonical matrix — one process per model, sequential per provider group
cd /root/agentseolab
M=24; S=20260823
python3 -u runner/asl002_swap.py cf @cf/meta/llama-3.3-70b-instruct-fp8-fast $M $S
python3 -u runner/asl002_swap.py cf @cf/mistralai/mistral-small-3.1-24b-instruct $M $((S+1))
python3 -u runner/asl002_swap.py cf @cf/qwen/qwen3-30b-a3b-fp8 $M $((S+2))
python3 -u runner/asl002_swap.py cf @cf/openai/gpt-oss-20b $M $((S+3))
python3 -u runner/asl002_swap.py cf @cf/google/gemma-4-26b-a4b-it $M $((S+4))
python3 -u runner/asl002_swap.py or nvidia/nemotron-3-super-120b-a12b:free $M $((S+5))
python3 -u runner/asl002_swap.py oc ox-alpha-free $M $((S+6))
python3 -u runner/asl002_swap.py oc mimo-v2.5 $M $((S+7))
echo "ASL002 MATRIX COMPLETE"
