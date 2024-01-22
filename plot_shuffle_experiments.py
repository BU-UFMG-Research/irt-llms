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

ENEM_MAPPING_NAME = {
    #2022
    "ENEM_2022_CH_CO_PROVA_1062": "2022 Humanities",
    "ENEM_2022_CN_CO_PROVA_1092": "2022 Natural Sciences",
    "ENEM_2022_LC_CO_PROVA_1072": "2022 Languages and Codes (Spanish as Foreign Language)",
    "ENEM_2022_MT_CO_PROVA_1082": "2022 Mathematics",

    #2021
    "ENEM_2021_CH_CO_PROVA_886": "2021 Humanities",
    "ENEM_2021_CN_CO_PROVA_916": "2021 Natural Sciences",
    "ENEM_2021_LC_CO_PROVA_896": "2021 Languages and Codes (Spanish as Foreign Language)",
    "ENEM_2021_MT_CO_PROVA_906": "2021 Mathematics",

    #2020
    "ENEM_2020_CH_CO_PROVA_574": "2020 Humanities",
    "ENEM_2020_CN_CO_PROVA_604": "2020 Natural Sciences",
    "ENEM_2020_LC_CO_PROVA_584": "2020 Languages and Codes (Spanish as Foreign Language)",
    "ENEM_2020_MT_CO_PROVA_594": "2020 Mathematics",

    #2019
    "ENEM_2019_CH_CO_PROVA_520": "2019 Humanities",
    "ENEM_2019_CN_CO_PROVA_519": "2019 Natural Sciences",
    "ENEM_2019_LC_CO_PROVA_521": "2019 Languages and Codes (Spanish as Foreign Language)",
    "ENEM_2019_MT_CO_PROVA_522": "2019 Mathematics",
}

enem_exams = [
    "ENEM_2022_CH_CO_PROVA_1062",
    "ENEM_2022_CN_CO_PROVA_1092",
    "ENEM_2022_LC_CO_PROVA_1072",
    "ENEM_2022_MT_CO_PROVA_1082",
]

permutations = list(itertools.permutations("ABCDE"))
permutations = [list(x) for x in permutations]

for enem_exam in enem_exams:
    CO_PROVA = eval(enem_exam.split("_")[-1])
    df = pd.read_parquet(f"shuffle_experiment_{enem_exam}.parquet")
    df["FREQUENCY_CORRECT_ANSWER"] = df.apply(lambda x: x["MODEL_RESPONSE_PATTERN"].count(x["CORRECT_ANSWER"]), axis=1)
    df["FREQUENCY_CORRECT_ANSWER"] /= 120

    frequency_arrays = []
    for row in df.itertuples():
        frequency_array = []
        for pos in range(5):
            correct_answer = row.CORRECT_ANSWER
            positions = []
            # Find all the positions where CORRECT_ANSWER is the pos element of the permutation
            for i in range(len(permutations)):
                if permutations[i][pos] == correct_answer:
                    positions.append(i)

            # Get the substring in row.MODEL_RESPONSE_PATTERN in those positions
            responses = []
            for position in positions:
                responses.append(row.MODEL_RESPONSE_PATTERN[position])

            n_correct = responses.count(correct_answer)
            
            frequency_array.append(n_correct)

        frequency_arrays.append(np.array(frequency_array))

    df["PATTERN_CORRECT_ANSWER"] = frequency_arrays

    x = df["PATTERN_CORRECT_ANSWER"].values
    # make it a 2D array
    x = np.vstack(x)

    # plot bars (each row of x is a subplot)
    fig, axes = plt.subplots(9, 5, figsize=(10, 5))
    idx = 0
    for i in range(9):
        for j in range(5):
            axes[i, j].bar(range(5), x[idx, :], color="black")
            axes[i, j].set_xlim(-1, 5)
            axes[i, j].set_ylim(0, 24)
            axes[i, j].set_xticks([])
            axes[i, j].set_yticks([])
            idx += 1
    plt.suptitle(f"Frequency of correct answer in each position of the permutation: {ENEM_MAPPING_NAME[enem_exam]}")
    plt.tight_layout()
    plt.savefig(f"plots/frequency-correct-answer-{enem_exam}.png", dpi=800)
    plt.close()

    df["UNIFORMITY_MEASURE"] = df["PATTERN_CORRECT_ANSWER"].apply(lambda x: np.max(x) - np.min(x))

    df_items = pd.read_csv(f"data/raw-enem-exams/microdados_enem_2022/DADOS/ITENS_PROVA_2022.csv", sep=";", encoding="latin-1")

    df_items = df_items[df_items.CO_PROVA == CO_PROVA].sort_values(by="CO_POSICAO")
    if enem_exam == "ENEM_2022_LC_CO_PROVA_1072":
        # Remove questions that are not in Spanish as foreign language
        df_items = df_items[df_items.TP_LINGUA != 0].sort_values(by="CO_POSICAO")

    uniformity_measure = df.UNIFORMITY_MEASURE.values
    item_difficulty = df_items.NU_PARAM_B.values

    # Removing questions that have no item difficulty (NaN)
    nan_indices = np.argwhere(np.isnan(item_difficulty))
    uniformity_measure = np.delete(uniformity_measure, nan_indices)
    item_difficulty = np.delete(item_difficulty, nan_indices)

    # Correlation between uniformity measure and item difficulty
    from scipy.stats import pearsonr
    corr, pvalue = pearsonr(uniformity_measure, item_difficulty)

    # Plot uniformity measure x item difficulty
    plt.scatter(uniformity_measure, item_difficulty)
    plt.xlabel("Uniformity Measure")
    plt.ylabel("Item Difficulty")
    plt.title(f"Uniformity Measure x Item Difficulty: {ENEM_MAPPING_NAME[enem_exam]}\nPearson correlation: {corr:.4f} (p-value: {pvalue:.4f})")
    plt.savefig(f"plots/uniformity-measure-x-item-difficulty-{enem_exam}.png", dpi=800)
    plt.close()