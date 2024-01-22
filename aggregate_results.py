from copy import deepcopy
import glob
import re
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from exam import ENEM

files = glob.glob("enem-experiments-results-new-parsing/*")
# removing files with full-answers in the name
files = [file for file in files if "full-answers" not in file]
files.sort()

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
        df_v1 = df_v1.reset_index(drop=True)

        if new_df is None:
            new_df = df_v1
        else:
            new_df = pd.concat([new_df, df_v1])

        # # v2: discard from 5th to 10th question (english as foreign language)
        # df_v2 = deepcopy(df)
        # df_v2.TX_RESPOSTAS = df_v2.TX_RESPOSTAS.apply(lambda x: x[:5] + x[10:])
        # df_v2.TX_GABARITO = df_v2.TX_GABARITO.apply(lambda x: x[:5] + x[10:])
        # df_v2.RESPONSE_PATTERN = df_v2.RESPONSE_PATTERN.apply(lambda x: x[:5] + x[10:])
        # #CTT SCORE (sum of the number of ones in the RESPONSE_PATTERN)
        # df_v2.CTT_SCORE = df_v2.RESPONSE_PATTERN.apply(lambda x: x.count("1"))
        # df_v2.ENEM_EXAM = df_v2.ENEM_EXAM.apply(lambda x: x + "-english-fl")
        # df_v2 = df_v2.reset_index(drop=True)

        # if new_df is None:
        #     new_df = pd.concat([df_v1, df_v2])
        # else:
        #     new_df = pd.concat([new_df, df_v1, df_v2])
    else:
        if new_df is None:
            new_df = pd.read_parquet(file)
        else:
            new_df = pd.concat([new_df, pd.read_parquet(file)])

new_df["CO_PROVA"] = new_df.ENEM_EXAM.apply(lambda x: x.split("_")[-1])
new_df = new_df.reset_index(drop=True)
new_df.MODEL_NAME.replace({"gpt-3.5-turbo": "gpt-3.5-turbo-0613"}, inplace=True)
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

