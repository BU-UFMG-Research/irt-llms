import os
os.environ['TRANSFORMERS_CACHE'] = "cache/"

import argparse
import time
import pandas as pd
import torch
from models import LLAMA2, Mistral
from exam import ENEM

"""
LLAMA2 model config (7B, 13B, 70B):
GenerationConfig {
  "bos_token_id": 1,
  "do_sample": true,
  "eos_token_id": 2,
  "max_length": 4096,
  "pad_token_id": 0,
  "temperature": 0.6,
  "top_p": 0.9
}
"""

# Create an argparser
parser = argparse.ArgumentParser(description='Run model on ENEM exam')
parser.add_argument('--model', type=str, choices=["llama2", "mistral"], required=True, help='Model to run')
parser.add_argument('--model_size', type=str, choices=["7b", "13b"], required=True, help='Model size')
parser.add_argument('--enem_exam', type=str, required=True, help='ENEM exam to run')
parser.add_argument('--temperature', type=float, default=0.6, help='Temperature')
parser.add_argument('--answer_order', type=str, default="ABCDE", help='Answer order')
parser.add_argument('--question_order', type=str, default="original", choices=["original", "random"], help='Question order on ENEM exam. In random order, questions are shuffled using the seed to control the randomness')
parser.add_argument('--system_prompt_type', type=str, default="simple", choices=["simple", "cot"], help='System prompt type')
parser.add_argument("--language", type=str, default="pt-br", choices=["pt-br", "en"], help="Language of the exam")
parser.add_argument("--max_time", type=int, default=120, help="Max time in seconds to generate an answer")
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
print("Language: ", args.language)
print("Max time: ", args.max_time)
print("Seed: ", args.seed)
print("\n------------------\n")


# Get pytorch device
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# Load ENEM exam
enem = ENEM(args.enem_exam, answer_order=args.answer_order, question_order=args.question_order, seed=args.seed, language=args.language)

# Load model
if args.model == "llama2":
    model = LLAMA2(args.model_size, token, device, max_time=args.max_time, temperature=args.temperature, random_seed=args.seed)
elif args.model == "mistral":
    if args.model_size == "7b":
        model = Mistral(token, device, max_time=args.max_time, temperature=args.temperature, random_seed=args.seed)
    else:
        raise Exception("Model size not implemented for Mistral")
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

full_answers = []

for i in range(enem.get_enem_size()):
    print(f"Question {i}")
    st = time.time()
    question = enem.get_question(i)
    correct_answer = enem.get_correct_answer(i)

    if correct_answer == "anulada":
        # Voided question
        model_response_pattern += "V"
        correct_response_pattern += "V"
        model_response_binary_pattern += "0"
        full_answers.append("anulada")
        continue

    model_answer, model_full_answer = model.get_answer_from_question(question, system_prompt_type=args.system_prompt_type)
    
    # Remove the prompt from the full answer
    model_full_answer = model_full_answer.split("[/INST]")[-1]
    full_answers.append(model_full_answer)

    if model_answer is None or not model_answer in list("ABCDE"):
        # Raise warning when model answer is None
        print("Warning: model answer is None for question ", i)
        model_answer = "X"

    if model_answer == correct_answer:
        model_response_binary_pattern += "1"
        ctt_score += 1
    else:
        model_response_binary_pattern += "0"

    model_response_pattern += model_answer
    correct_response_pattern += correct_answer

    print(f"Time: {time.time()-st} seconds\n")

end_time = time.time()

# Save results to file
filename = f"enem-experiments-results/{args.model}-{args.model_size}-{args.temperature}-{args.enem_exam}-{args.answer_order}-{args.question_order}-{args.seed}-{args.system_prompt_type}-{args.max_time}-{args.language}.parquet"
df = pd.DataFrame({"MODEL_NAME": [args.model], "MODEL_SIZE": [args.model_size], "TEMPERATURE": [args.temperature], "ANSWER_ORDER": [args.answer_order], "QUESTION_ORDER": [args.question_order], "SEED": [args.seed], "PROMPT_TYPE": [args.system_prompt_type], "CTT_SCORE": [ctt_score], "CO_PROVA": [args.enem_exam], "TX_RESPOSTAS": [model_response_pattern], "TX_GABARITO": [correct_response_pattern], "RESPONSE_PATTERN": [model_response_binary_pattern], "TOTAL_RUN_TIME_SEC": [end_time-start_time], "AVG_RUN_TIME_PER_ITEM_SEC": [(end_time-start_time)/enem.get_enem_size()], "MAX_TIME_SEC": [args.max_time], "LANGUAGE": [args.language]})
df.to_parquet(filename)

# Saving the full answers to a parquet file (each answer is a row)
filename = f"enem-experiments-results/{args.model}-{args.model_size}-{args.temperature}-{args.enem_exam}-{args.answer_order}-{args.question_order}-{args.seed}-{args.system_prompt_type}-{args.max_time}-{args.language}-full-answers.parquet"
df = pd.DataFrame({"FULL_ANSWER": full_answers})
df.to_parquet(filename)
