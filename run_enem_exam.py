import argparse
import os
import time
import torch
from models import LLAMA2
from exam import ENEM
import pandas as pd

# Create an argparser
parser = argparse.ArgumentParser(description='Run model on ENEM exam')
parser.add_argument('--model', type=str, choices=["llama2"], required=True, help='Model to run')
parser.add_argument('--model_size', type=str, choices=["7b"], required=True, help='Model size')
parser.add_argument('--enem_exam', type=str, required=True, help='ENEM exam to run')
parser.add_argument('--temperature', type=float, default=0.1, help='Temperature')

args = parser.parse_args()

# Token: HF_TOKEN env variable
token = os.getenv("HF_TOKEN")

# Print args
print("Model: ", args.model)
print("Model size: ", args.model_size)
print("ENEM exam: ", args.enem_exam)

# Get pytorch device
device = "cuda" if torch.cuda.is_available() else "mps" if torch.cuda.is_mps_supported else "cpu"

# Load ENEM exam
enem = ENEM(args.enem_exam)

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
    prompt = enem.format_enem_prompt(i)
    model_answer = model.get_answer_from_prompt(prompt, temperature=args.temperature)
    correct_answer = enem.get_correct_answer(i)

    if model_answer is None:
        # Raise warning when model answer is None
        print("Warning: model answer is None for question ", i)
        model_answer = "Z"

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
    f.write("MODEL_NAME,MODEL_SIZE,TEMPERATURE,ANSWER_ORDER,QUESTION_TEMPLATE_SEQ,CTT_SCORE,CO_PROVA,TX_RESPOSTAS,TX_GABARITO,RESPONSE_PATTERN,TOTAL_RUN_TIME_SEC,AVG_RUN_TIME_PER_ITEM_SEC")
    f.write("\n")
    f.write(f"{args.model},{args.model_size},{args.temperature},1,1,{ctt_score},{args.enem_exam},{model_response_pattern},{correct_response_pattern},{model_response_binary_pattern},{end_time-start_time},{(end_time-start_time)/enem.get_enem_size()}")