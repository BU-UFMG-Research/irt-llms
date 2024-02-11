import gc
import os

import numpy as np
os.environ['HF_HOME'] = "cache/"
os.environ['TRANSFORMERS_CACHE'] = "cache/"

import argparse
import time
import pandas as pd
import torch
from models import LLAMA2, Mistral, RandomModel, GPT
from exam import ENEM
from transformers import set_seed

# Create an argparser
parser = argparse.ArgumentParser(description='Run model on ENEM exam')
# LLMs args
parser.add_argument('--model', type=str, choices=["llama2", "mistral", "random", "gpt-3.5-turbo-0613"], required=True, help='Model to run')
parser.add_argument('--model_size', type=str, choices=["7b", "13b", "8x7b"], help='Model size')
parser.add_argument('--temperature', type=float, help='Temperature')
parser.add_argument('--system_prompt_type', type=str, choices=["few-shot", "zs-cot"], help='System prompt type')
# ENEM args
parser.add_argument('--enem_exam', type=str, required=True, help='ENEM exam to run')
parser.add_argument('--exam_type', type=str, help='ENEM exam type. It can be the default exam or a shuffled exam. If shuffled, the seed is used to control the randomness')
parser.add_argument('--question_order', default="original", type=str, choices=["original", "random"], help='Question order on ENEM exam. In random order, questions are shuffled using the seed to control the randomness')
parser.add_argument("--language", type=str, choices=["pt-br", "en"], help="Language of the exam")
parser.add_argument("--number_options", type=int, choices=range(2, 6), help="Number of options to use in the exam")
# Other args
parser.add_argument("--seed", type=int, required=True, help="Random seed")

args = parser.parse_args()

# Token: HF_TOKEN env variable
token = os.getenv("HF_TOKEN")

if args.seed == -1:
    seeds = [2724839799, 224453832, 1513448043, 745130168, 730262723, 4040595804, 362978403, 418235748, 444231693, 3113980281]
else:
    seeds = [args.seed]

for seed in seeds:
    # Set seed
    set_seed(seed)

    # Print args
    print("Model: ", args.model)
    print("Model size: ", args.model_size)
    print("Temperature: ", args.temperature)
    print("System prompt type: ", args.system_prompt_type)
    print("ENEM exam: ", args.enem_exam)
    print("Exam type: ", args.exam_type)
    print("Question order: ", args.question_order)
    print("Language: ", args.language)
    print("Number of options: ", args.number_options)
    print("Seed: ", seed)
    print("\n------------------\n")

    print("Execution started\n")


    # Get pytorch device
    device = "cuda"

    # Load ENEM exam
    enem = ENEM(args.enem_exam, exam_type=args.exam_type, question_order=args.question_order, seed=seed, language=args.language, number_options=args.number_options)

    # Load model
    if args.model == "llama2":
        model = LLAMA2(args.model_size, token, device, temperature=args.temperature, random_seed=seed)
    elif args.model == "mistral":
        if args.model_size == "7b" or args.model_size == "8x7b":
            model = Mistral(args.model_size, token, device, temperature=args.temperature, random_seed=seed)
        else:
            raise Exception("Model size not implemented for Mistral")
    elif args.model == "random":
        model = RandomModel()
    elif args.model == "gpt-3.5-turbo-0613":
        model = GPT(args.model, temperature=args.temperature, random_seed=args.seed)
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
    correct_answers = []
    parsed_answers = []

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
            correct_answers.append("anulada")
            parsed_answers.append("anulada")
            continue
        
        model_answer, model_full_answer = model.get_answer_from_question(question, system_prompt_type=args.system_prompt_type, language=args.language)

        full_answers.append(model_full_answer)
        correct_answers.append(correct_answer)
        parsed_answers.append(model_answer)

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

    # Remap answer pattern to original order
    if args.exam_type.startswith("shuffle"):
        model_response_pattern_remapped = enem.remapping_answer_pattern(model_response_pattern)
        correct_response_pattern_remapped = enem.remapping_answer_pattern(correct_response_pattern)

        # Swap variables (TX_RESPOSTAS AND TX_GABARITO have to be in the original order)
        model_response_pattern, model_response_pattern_remapped = model_response_pattern_remapped, model_response_pattern
        correct_response_pattern, correct_response_pattern_remapped = correct_response_pattern_remapped, correct_response_pattern
    else:
        model_response_pattern_remapped = None
        correct_response_pattern_remapped = None

    # Save results to file (in the order of the arguments)
    filename = f"enem-experiments-results/{args.model}-{args.model_size}-{args.temperature}-{args.system_prompt_type}-{args.enem_exam}-{args.exam_type}-{args.question_order}-{args.language}-{args.number_options}-{seed}.parquet"
    df = pd.DataFrame({"MODEL_NAME": [args.model], "MODEL_SIZE": [args.model_size], "TEMPERATURE": [args.temperature], "SYSTEM_PROMPT_TYPE": [args.system_prompt_type], "ENEM_EXAM": [args.enem_exam], "ENEM_EXAM_TYPE": [args.exam_type], "QUESTION_ORDER": [args.question_order], "LANGUAGE": [args.language], "NUMBER_OPTIONS": [args.number_options], "SEED": [seed], "CTT_SCORE": [ctt_score], "TX_RESPOSTAS": [model_response_pattern], "TX_GABARITO": [correct_response_pattern], "TX_RESPOSTAS_SHUFFLE": [model_response_pattern_remapped], "TX_GABARITO_SHUFFLE": [correct_response_pattern_remapped], "RESPONSE_PATTERN": [model_response_binary_pattern], "TOTAL_RUN_TIME_SEC": [end_time-start_time], "AVG_RUN_TIME_PER_ITEM_SEC": [(end_time-start_time)/enem.get_enem_size()]})
    df.to_parquet(filename)

    # # Saving the full answers to a parquet file (each answer is a row)
    filename = f"enem-experiments-results/{args.model}-{args.model_size}-{args.temperature}-{args.system_prompt_type}-{args.enem_exam}-{args.exam_type}-{args.question_order}-{args.language}-{args.number_options}-{seed}-full-answers.parquet"
    df = pd.DataFrame({"QUESTION": enem.get_question_number_array() ,"CORRECT_ANSWER": correct_answers, "PARSED_ANSWER": parsed_answers, "FULL_ANSWER": full_answers})
    df.to_parquet(filename)

    del model
    # Call garbage collector
    torch.cuda.empty_cache()
    gc.collect()

print("Execution finished\n")