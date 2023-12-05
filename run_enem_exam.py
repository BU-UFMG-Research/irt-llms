import argparse
import os
import time
import torch
from models import LLAMA2
from exam import ENEM
import pandas as pd

"""
Experimental Design Tentative
    - Model varies across Llama-2 (3 versions - 7B, 13B, 70B), MISTRAL, Sabia, (ChatGPT? GPT4? Huggingface models?)
    - Consistency of Machines as compared to Humans
        - Different ways of asking same questions
    - Robustness of Consistency of Machines
        - Different ways of asking same questions
        - When we find that certain cases are not robust, can we improve robustness (and possibly consistency) by using a consensus?
    - Prompting: basic, CoT, 
        - Does CoT improve robustness of consistency?
"""

# Create an argparser
parser = argparse.ArgumentParser(description='Run model on ENEM exam')
parser.add_argument('--model', type=str, choices=["llama2"], required=True, help='Model to run')
parser.add_argument('--model_size', type=str, choices=["7b"], required=True, help='Model size')
parser.add_argument('--enem_exam', type=str, required=True, help='ENEM exam to run')
parser.add_argument('--temperature', type=float, default=0.1, help='Temperature')
parser.add_argument('--answer_order', type=str, default="ABCDE", help='Answer order')
parser.add_argument('--question_order', type=str, default="original", choices=["original", "random"], help='Question order on ENEM exam. In random order, questions are shuffled using the seed to control the randomness')
parser.add_argument('--system_prompt_type', type=str, default=None, choices=["simple", "chain-of-thought", "llama2-paper"], help='System prompt type')
parser.add_argument("--seed", type=int, default=42, help="Random seed")

args = parser.parse_args()

# Check answer order
if len(args.answer_order) != 5 or "A" not in args.answer_order or "B" not in args.answer_order or "C" not in args.answer_order or "D" not in args.answer_order or "E" not in args.answer_order:
    raise Exception("Answer order must be 5 letters, e.g. ABCDE")

# Token: HF_TOKEN env variable
token = os.getenv("HF_TOKEN")

# Print args
print("Model: ", args.model)
print("Model size: ", args.model_size)
print("ENEM exam: ", args.enem_exam)
print("Temperature: ", args.temperature)
print("Answer order: ", args.answer_order)
print("Question order: ", args.question_order)
print("System prompt type: ", args.system_prompt_type)
print("Seed: ", args.seed)
print("\n------------------\n")


# Get pytorch device
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# Load ENEM exam
enem = ENEM(args.enem_exam, answer_order=args.answer_order, question_order=args.question_order, seed=args.seed)

# Load model
if args.model == "llama2":
    model = LLAMA2(args.model_size, token, device)
else:
    raise Exception("Model not implemented")

# Run model on ENEM exam and save results to file

# Saving model responses (letters and binary pattern), correct responses and ctt score
model_response_pattern = ""
correct_response_pattern = ""
model_response_binary_pattern = ""
ctt_score = 0

# Also measure time
start_time = time.time()

for i in range(enem.get_enem_size()):
    question = enem.get_question(i)
    model_answer = model.get_answer_from_question(question, temperature=args.temperature, system_prompt_type=args.system_prompt_type)
    correct_answer = enem.get_correct_answer(i)

    if model_answer is None or not model_answer in list("ABCDE"):
        # Raise warning when model answer is None
        print("Warning: model answer is None for question ", i)
        model_answer = "X"

    # TODO: How about the case where the model answer is "anulada" (voided)?
    if model_answer == correct_answer:
        model_response_binary_pattern += "1"
        ctt_score += 1
    else:
        model_response_binary_pattern += "0"

    model_response_pattern += model_answer
    correct_response_pattern += correct_answer

end_time = time.time()

# Save results to file
filename = f"enem-experiments-results/{args.model}-{args.model_size}-{args.temperature}-{args.enem_exam}.csv"
with open(filename, "w") as f:
    f.write("MODEL_NAME,MODEL_SIZE,TEMPERATURE,ANSWER_ORDER,QUESTION_ORDER,SEED,PROMPT_TYPE,CTT_SCORE,CO_PROVA,TX_RESPOSTAS,TX_GABARITO,RESPONSE_PATTERN,TOTAL_RUN_TIME_SEC,AVG_RUN_TIME_PER_ITEM_SEC")
    f.write("\n")
    f.write(f"{args.model},{args.model_size},{args.temperature},{args.answer_order},{args.question_order},{args.seed},{args.system_prompt_type},{ctt_score},{args.enem_exam},{model_response_pattern},{correct_response_pattern},{model_response_binary_pattern},{end_time-start_time},{(end_time-start_time)/enem.get_enem_size()}")