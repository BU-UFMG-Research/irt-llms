from copy import deepcopy
import gc
import itertools
import os
from matplotlib import pyplot as plt

import numpy as np
import argparse
import time
import pandas as pd
import torch
from models import LLAMA2, Mistral, RandomModel, GPT
from exam import ENEM
from transformers import set_seed
import seaborn as sns

model_name = "gpt-3.5-turbo-0613"
temperature = 0.6
system_prompt_type = "few-shot"
enem_exam = "ENEM_2022_LC_CO_PROVA_1072" #"ENEM_2022_CH_CO_PROVA_1062" #"ENEM_2022_CN_CO_PROVA_1092" "ENEM_2022_MT_CO_PROVA_1082"
language = "pt-br"
number_options = 5
seed = 2724839799
question_order = "original"
exam_type = "default"
# Load ENEM exam
enem = ENEM(enem_exam, exam_type=exam_type, question_order=question_order, seed=seed, language=language, number_options=number_options)
# Load model
model = GPT(model_name, temperature=temperature, random_seed=seed)

# Run model on ENEM exam and save results to file

# Also measure time
start_time = time.time()

model_response_patterns = []
correct_answers = []

# Skipping English as foreign language questions
start = 5 if enem_exam == "ENEM_2022_LC_CO_PROVA_1072" else 0
enem_size = enem.get_enem_size() - start

for i in range(start, enem.get_enem_size()):
    # Saving model responses (letters and binary pattern), correct responses (for each question)
    model_response_pattern = ""

    print(f"Question {i}")
    st = time.time()
    question = enem.get_question(i)
    correct_answer = enem.get_correct_answer(i)
    correct_answers.append(correct_answer)

    if correct_answer == "anulada":
        # Voided question
        model_response_pattern += "V"
        model_response_patterns.append(model_response_pattern)
        continue

    # Make all the permutations of the A, B, C, D, E options
    for permutation in itertools.permutations("ABCDE"):
        permutation = list(permutation)

        model_answer, model_full_answer = model.get_answer_from_question(question, system_prompt_type=system_prompt_type, language=language, options_letters=permutation)

        if model_answer is None or not model_answer in list("ABCDE"):
            # Raise warning when model answer is None
            print("Warning: model answer is None for question ", i)
            model_answer = "X"

        model_response_pattern += model_answer

        print(f"Time: {time.time()-st} seconds\n")

    model_response_patterns.append(model_response_pattern)

end_time = time.time()
enem_size = enem.get_enem_size() - start

# Save results to file (in the order of the arguments)
df = pd.DataFrame({"MODEL": [model_name] * enem_size, "TEMPERATURE": [temperature] * enem_size, "QUESTION": list(range(enem_size)), "ENEM_EXAM": [enem_exam] * enem_size,  "LANGUAGE": [language] * enem_size, "SEED": [seed] * enem_size, "MODEL_RESPONSE_PATTERN": model_response_patterns, "CORRECT_ANSWER": correct_answers})
filename = f"shuffle_experiment_{enem_exam}.parquet"
df.to_parquet(filename)

print("Execution finished\n")