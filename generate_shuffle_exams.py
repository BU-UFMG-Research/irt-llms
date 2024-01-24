import argparse
import glob
import os
import pandas as pd
import numpy as np

# Including exams with 2019, 2020, 2021, 2022 in the name
exams = glob.glob("data/parsed-enem-exams/pt-br/default/*2019*.csv")
exams = exams + glob.glob("data/parsed-enem-exams/pt-br/default/*2020*.csv")
exams = exams + glob.glob("data/parsed-enem-exams/pt-br/default/*2021*.csv")
exams = exams + glob.glob("data/parsed-enem-exams/pt-br/default/*2022*.csv")
exams = exams + glob.glob("data/parsed-enem-exams/en/default/*2019*.csv")
exams = exams + glob.glob("data/parsed-enem-exams/en/default/*2020*.csv")
exams = exams + glob.glob("data/parsed-enem-exams/en/default/*2021*.csv")
exams = exams + glob.glob("data/parsed-enem-exams/en/default/*2022*.csv")
exams.sort()

# Argparse the seed
parser = argparse.ArgumentParser(description='Run model on ENEM exam')
parser.add_argument('--seed', type=int, required=True, help='Seed')
args = parser.parse_args()

original_order = list("ABCDE")

for exam in exams:
    # Set seed for reproducibility (same seed for all exams)
    random = np.random.RandomState(args.seed)

    df = pd.read_csv(exam)

    # iterate over the rows of the dataframe
    for index, row in df.iterrows():
        answer_order = list(random.permutation(original_order))

        # Map the answer in the original order to the answer in the answer_order
        # We first find the index of the answer in the answer order. Then, we use that index to find the answer in the original order.
        # For instance: we have original order "ABCDE" and answer order "CABDE". 
        # If the answer is "B", we find the index of "B" in the answer order, which is 2.
        # Then we use that index to find the answer in the original order ("ABCDE"), which is "C". Then we map "B" to "C" in the answer column.
        # The corner case is where the answer is not in the answer order, in which case we just return the answer.
        # For this exam, it happens when the question is voided ("anulada").
        df.loc[index, "answer"] = original_order[answer_order.index(row["answer"])] if row["answer"] in original_order else row["answer"]

        # We have columns A, B, C, D, E. Map them to answer_order in this row.
        for i in range(5):
            df.loc[index, original_order[i]] = row[answer_order[i]]

        df.loc[index, "answer_order"] = str(answer_order)

    # Get the language of the exam
    language = "pt-br" if "pt-br" in exam else "en"

    # Save the exam
    try:
        os.mkdir(f"data/parsed-enem-exams/{language}/shuffle-{args.seed}")
    except:
        pass

    df.to_csv(f"data/parsed-enem-exams/{language}/shuffle-{args.seed}/{os.path.basename(exam)}", index=False)
