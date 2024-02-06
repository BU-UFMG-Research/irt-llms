from copy import deepcopy
import glob
import re
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from exam import ENEM

# Argparse
import argparse
parser = argparse.ArgumentParser(description="Aggregate results from different experiments")
parser.add_argument("--shuffle", action="store_true", help="If the results are from shuffle experiments")
args = parser.parse_args()

if args.shuffle:
    files = glob.glob("enem-experiments-results-new-parsing-shuffle/*")
else:
    files = glob.glob("enem-experiments-results-new-parsing/*")

# Few-shot
files = [file for file in files if "cot" not in file]
# COT
# files = [file for file in files if "cot" in file]
# files.sort()

# # Get only the following seeds
# seeds = ["2724839799", "224453832", "1513448043", "745130168", "730262723", "4040595804", "362978403", "418235748", "444231693", "3113980281"]
# files = [file for file in files for seed in seeds if seed in file]
# # Get only the following years
# years = ["2022"]
# files = [file for file in files for year in years if year in file]

new_df = None
for file in files:
    if "LC" in file:
        # Different process for LC (we have to create two versions of the same file)
        df = pd.read_parquet(file)
        # v1: discard first 5 questions (spanish as foreign language)
        #"CTT_SCORE", "TX_RESPOSTAS", "TX_GABARITO", "RESPONSE_PATTERN":
        df_v1 = deepcopy(df)
        df_v1.TX_RESPOSTAS = df_v1.TX_RESPOSTAS.apply(lambda x: x[5:])
        df_v1.TX_GABARITO = df_v1.TX_GABARITO.apply(lambda x: x[5:])
        df_v1.RESPONSE_PATTERN = df_v1.RESPONSE_PATTERN.apply(lambda x: x[5:])
        #CTT SCORE (sum of the number of ones in the RESPONSE_PATTERN)
        df_v1.CTT_SCORE = df_v1.RESPONSE_PATTERN.apply(lambda x: x.count("1"))
        # If it is shuffle (TX_RESPOSTAS_SHUFFLE not None), we have to do the same with TX_RESPOSTAS_SHUFFLE and TX_GABARITO_SHUFFLE
        if args.shuffle:
            df_v1.TX_RESPOSTAS_SHUFFLE = df_v1.TX_RESPOSTAS_SHUFFLE.apply(lambda x: x[5:])
            df_v1.TX_GABARITO_SHUFFLE = df_v1.TX_GABARITO_SHUFFLE.apply(lambda x: x[5:])

        df_v1 = df_v1.reset_index(drop=True)

        if new_df is None:
            new_df = df_v1
        else:
            new_df = pd.concat([new_df, df_v1])
    else:
        if new_df is None:
            new_df = pd.read_parquet(file)
        else:
            new_df = pd.concat([new_df, pd.read_parquet(file)])

new_df["CO_PROVA"] = new_df.ENEM_EXAM.apply(lambda x: x.split("_")[-1])
new_df["EXAM_YEAR"] = new_df.ENEM_EXAM.apply(lambda x: x.split("_")[1])
new_df["EXAM_SUBJECT"] = new_df.ENEM_EXAM.apply(lambda x: x.split("_")[2])
new_df = new_df.reset_index(drop=True)
new_df.MODEL_NAME.replace({"gpt-3.5-turbo": "gpt-3.5-turbo-0613"}, inplace=True)
if args.shuffle:
    new_df.to_parquet("enem-experiments-results-shuffle-processed.parquet")
else:
    new_df.to_parquet("enem-experiments-results-processed.parquet")

count = 0
total = 0
for row in new_df.itertuples():
    # Count how many "X" are in list(row.TX_RESPOSTAS)
    count += list(row.TX_RESPOSTAS).count("X")
    total += len(list(row.TX_RESPOSTAS))
print("\nNon-answered count: ", count)
print("Total count: ", total)
print("Percentage: ", count/total)

