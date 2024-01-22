import glob
import re
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from exam import ENEM

files = glob.glob("enem-experiments-results/*")
# removing files with full-answers in the name
files = [file for file in files if "full-answers" not in file]
print(len(files))
files.sort()

files_parsed = glob.glob("enem-experiments-results-new-parsing/*")
files_parsed = [file for file in files_parsed if "full-answers" not in file]
files_parsed = [file.split("/")[-1] for file in files_parsed]

files = [file for file in files if file.split("/")[-1] not in files_parsed]

new_df = None
count = 0
total = 0
errors_exam = {}
errors_language = {}
errors_model = {}
for file in files:
    print("Processing file ", file)
    print()
    new_file = file.replace("enem-experiments-results", "enem-experiments-results-new-parsing")

    df = pd.read_parquet(file)
    df_full_answers = pd.read_parquet(file.replace(".parquet", "-full-answers.parquet"))

    enem_exam = df.iloc[0, :].ENEM_EXAM
    enem_exam_type = df.iloc[0, :].ENEM_EXAM_TYPE
    question_order = df.iloc[0, :].QUESTION_ORDER
    language = df.iloc[0, :].LANGUAGE
    seed = df.iloc[0, :].SEED
    number_options = df.iloc[0, :].NUMBER_OPTIONS

    #enem = ENEM(enem_exam, exam_type=enem_exam_type, question_order=question_order, seed=seed, language=language, number_options=number_options)
    #Questão: Nos livros Harry Potter , um anagrama do nome do personagem “TOM MARVOLO RIDDLE” gerou a frase “I AM LORD VOLDEMORT”. Suponha que Harry quisesse formar todos os anagramas da frase “I AM POTTER”, de tal forma que as vogais e consoantes aparecessem sempre intercaladas, e sem considerar o espaçamento entre as letras. Nessas condições, o número de anagramas formados é dado por

    new_TX_RESPOSTAS = ""
    new_RESPONSE_PATTERN = ""
    new_CTT_SCORE = 0

    # Iterate over df_full_answers
    for idx, row in df_full_answers.iterrows():
        full_answer = row.FULL_ANSWER
        parsed_answer = row.PARSED_ANSWER
        correct_answer = row.CORRECT_ANSWER
        
        total += 1
        if parsed_answer is None:
            count += 1
            try:
                errors_exam[enem_exam] += 1
            except KeyError:
                errors_exam[enem_exam] = 1

            try:
                errors_language[language] += 1
            except KeyError:
                errors_language[language] = 1

            try:
                errors_model[df.iloc[0, :].MODEL_NAME + " " + str(df.iloc[0, :].MODEL_SIZE)] += 1
            except KeyError:
                errors_model[df.iloc[0, :].MODEL_NAME + " " + str(df.iloc[0, :].MODEL_SIZE)] = 1

            # Manual parsing
            print("Full answer:", full_answer, "\n")
            parsed_answer = input("Model answer: ")
            while not parsed_answer in list("ABCDEX"):
                parsed_answer = input("Invalid Option. Model answer: ")
            print("\n-------------------------------------\n")
        
        new_TX_RESPOSTAS += parsed_answer
        new_RESPONSE_PATTERN += "1" if parsed_answer == correct_answer else "0"
        new_CTT_SCORE += 1 if parsed_answer == correct_answer else 0

    df["TX_RESPOSTAS"] = new_TX_RESPOSTAS
    df["RESPONSE_PATTERN"] = new_RESPONSE_PATTERN
    df["CTT_SCORE"] = new_CTT_SCORE

    df.to_parquet(new_file)

    print("Saved to ", new_file)
    print("\n\n")

print("Total:", total)
print("Count:", count)
print("Percentage:", count/total)
print()
print(errors_exam)
print()
print(errors_language)
print()
print(errors_model)