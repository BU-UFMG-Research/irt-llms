from copy import deepcopy
import gc
import itertools
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

#model_name = "gpt-3.5-turbo-1106"
model_name = "gpt-3.5-turbo-0613"
temperature = 0.6
system_prompt_type = "few-shot"
enem_exam = "ENEM_2022_MT_CO_PROVA_1082"
language = "pt-br"
number_options = 5
seed = 2724839799
question_order = "original"
exam_type = "default"
# Load ENEM exam
enem = ENEM(enem_exam, exam_type=exam_type, question_order=question_order, seed=seed, language=language, number_options=number_options)
order = []
for i in range(enem.get_enem_size()):
    question = enem.get_question(i)
    order.append(eval(question["question"].split(" ")[-1]))

df = pd.read_parquet("shuffle_experiment.parquet")
df["FREQUENCY_CORRECT_ANSWER"] = df.apply(lambda x: x["MODEL_RESPONSE_PATTERN"].count(x["CORRECT_ANSWER"]), axis=1)
df["FREQUENCY_CORRECT_ANSWER"] /= 120
df["ENEM_EXAM"] = "ENEM_2022_MT_CO_PROVA_1082"
df["CO_POSICAO"] = order

df_items = pd.read_csv("data/raw-enem-exams/microdados_enem_2022/DADOS/ITENS_PROVA_2022.csv", sep=";", encoding="latin-1")
df_items = df_items[df_items["CO_PROVA"] == 1082]
df_items = df_items[["CO_POSICAO", "NU_PARAM_B"]]

df = df.merge(df_items, on="CO_POSICAO", how="inner")
df.dropna(inplace=True)
df.sort_values(by=["NU_PARAM_B"], inplace=True)

# # Plot the relationship between FREQUENCY_CORRECT_ANSWER and NU_PARAM_B
# import seaborn as sns
# import matplotlib.pyplot as plt
# sns.heatmap(df["FREQUENCY_CORRECT_ANSWER"].values.reshape(1, -1), annot=True)
# plt.show()

exit()


model = GPT(model_name, temperature=temperature, random_seed=seed)
# Run model on ENEM exam and save results to file

# Also measure time
start_time = time.time()

model_response_patterns = []
correct_answers = []

for i in range(enem.get_enem_size()):
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
        # new_question = deepcopy(question)
        # new_question["answer"] = permutation[original_order.index(question["answer"])]
        # for option in original_order:
        #     idx_option = permutation.index(option)
        #     new_question["options"][option] = question["options"][original_order[idx_option]]

        model_answer, model_full_answer = model.get_answer_from_question(question, system_prompt_type=system_prompt_type, language=language, options_letters=permutation)

        if model_answer is None or not model_answer in list("ABCDE"):
            # Raise warning when model answer is None
            print("Warning: model answer is None for question ", i)
            model_answer = "X"

        model_response_pattern += model_answer

        print(f"Time: {time.time()-st} seconds\n")

    model_response_patterns.append(model_response_pattern)

end_time = time.time()
enem_size = enem.get_enem_size()

# Save results to file (in the order of the arguments)
df = pd.DataFrame({"MODEL": [model_name] * enem_size, "TEMPERATURE": [temperature] * enem_size, "QUESTION": list(range(enem_size)), "ENEM_EXAM": [enem_exam] * enem_size,  "LANGUAGE": [language] * enem_size, "SEED": [seed] * enem_size, "MODEL_RESPONSE_PATTERN": model_response_patterns, "CORRECT_ANSWER": correct_answers})
filename = "shuffle_experiment.parquet"
df.to_parquet(filename)

print("Execution finished\n")