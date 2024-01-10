import glob
import re
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from exam import ENEM

def parse_answer(answer, question, system_prompt_type, language):
    answer_word = "Answer:" if language == "en" else "Resposta:"
    regex = r"(?:|[Aa]lternativa|[Oo]pção )" if language == "pt" else r"(?:|[Aa]lternative|[Oo]ption|[Cc]orrect [Aa]nswer is )"
    ans = answer.split('[/INST]')[-1]

    if system_prompt_type == "cot":
        match = re.findall(r"{} (\([ABCDE]\))\n".format(answer_word), ans)
        if len(set(match)) == 1:
            return match[0].removeprefix("(").removesuffix(")")
        else:
            match = re.findall(r"{} [ABCDE]\)\n".format(answer_word), ans)
            if len(set(match)) == 1:
                return match[0]
            else:
                match = re.findall(r"{} [ABCDE]".format(answer_word), ans)
                if len(set(match)) == 1:
                    return match[0]
                    
        if len(ans.split(answer_word)) == 1:
            match = re.findall(r"{}(\([ABCDE]\))".format(regex), ans)
            if len(set(match)) == 1:
                return match[0].removeprefix("(").removesuffix(")")
            elif len(set(match)) > 1:
                return None
            else:
                match = re.findall(r"{}([ABCDE]\))".format(regex), ans)
                if len(set(match)) == 1:
                    return match[0]
                elif len(set(match)) > 1:
                    return None
                else:
                    match = re.findall(r"{}([ABCDE])".format(regex), ans)
                    if set(match) == 1:
                        return match[0]
                    else:
                        return None
        else:
            ans = ans.split(answer_word)[-1].strip()
            match = re.findall(r"(\([A-E]\))", ans)
            if len(set(match)) == 1:
                return match[0].removeprefix("(").removesuffix(")")
            elif len(set(match)) > 1:
                return None
            else:
                match = re.findall(r"([A-E]\))", ans)
                if len(set(match)) == 1:
                    return match[0].removesuffix(")")
                elif len(set(match)) > 1:
                    return None
                else:
                    match = re.findall(r"([A-E])", ans)
                    if len(set(match)) == 1:
                        return match[0]
                    else:
                        return None # Parser error
    else:
        match = re.findall(r"(\([A-E]\))", ans)
        if len(set(match)) == 1:
            return match[0]
        else:
            return None

files = glob.glob("enem-experiments-results/*")
# removing files with full-answers in the name
files = [file for file in files if "full-answers" not in file]
files.sort()

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
    # if new_file exists
    # if glob.glob(new_file):
    #     print("File already exists. Skipping...")
    #     print("\n\n")
    #     continue

    df = pd.read_parquet(file)
    df_full_answers = pd.read_parquet(file.replace(".parquet", "-full-answers.parquet"))

    enem_exam = df.iloc[0, :].ENEM_EXAM
    enem_exam_type = df.iloc[0, :].ENEM_EXAM_TYPE
    question_order = df.iloc[0, :].QUESTION_ORDER
    language = df.iloc[0, :].LANGUAGE
    seed = df.iloc[0, :].SEED
    number_options = df.iloc[0, :].NUMBER_OPTIONS

    enem = ENEM(enem_exam, exam_type=enem_exam_type, question_order=question_order, seed=seed, language=language, number_options=number_options)

    new_TX_RESPOSTAS = ""
    new_RESPONSE_PATTERN = ""
    new_CTT_SCORE = 0

    # Iterate over df_full_answers
    for idx, row in df_full_answers.iterrows():
        full_answer = row.FULL_ANSWER
        parsed_answer = row.PARSED_ANSWER
        previous_correct_answer = row.CORRECT_ANSWER
        question = enem.get_question(idx)
        #new_correct_answer = parse_answer(full_answer, question, df.iloc[0, :].SYSTEM_PROMPT_TYPE, language)
        
        # LLAMA2
        # Total: 370
        # Count: 18
        # Percentage: 0.04864864864864865

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
                errors_model[df.iloc[0, :].MODEL_NAME] += 1
            except KeyError:
                errors_model[df.iloc[0, :].MODEL_NAME] = 1
            print("Full answer:", full_answer)
            print("Parsed answer:", parsed_answer)
            a = input()
            print("\n-------------------------------------\n")
        
        #if new_correct_answer != previous_correct_answer:
            # print("\n\n\nQuestion ", idx)
            # print("Previous correct answer:", previous_correct_answer)
            # print("New correct answer:", new_correct_answer)
            # print("\nFull answer:", full_answer)

            #if new_correct_answer is None:
                #new_correct_answer = input("Enter the new correct answer: ")
                #print(new_correct_answer)
        
                #count += 1

        # new_TX_RESPOSTAS += new_correct_answer
        # new_RESPONSE_PATTERN += "1" if new_correct_answer == parsed_answer else "0"
        # new_CTT_SCORE += 1 if new_correct_answer == parsed_answer else 0

    # df["TX_RESPOSTAS"] = new_TX_RESPOSTAS
    # df["RESPONSE_PATTERN"] = new_RESPONSE_PATTERN
    # df["CTT_SCORE"] = new_CTT_SCORE

    # df.to_parquet(new_file)

    # print("Saved to ", new_file)
    # print("\n\n")

print("Total:", total)
print("Count:", count)
print("Percentage:", count/total)
print()
print(errors_exam)
print()
print(errors_language)
print()
print(errors_model)

# Old aggregate_results.py
# files = glob.glob("enem-experiments-results/*")
# # removing files with full-answers in the name
# files = [file for file in files if "full-answers" not in file]
# files.sort()

# new_df = None
# for file in files:
#     df = pd.read_parquet(file)
#     # Checking if there is any parsing error
#     if "X" in df.iloc[0, :]["TX_RESPOSTAS"]:
#         print("Parsing error in file ", file)
#         df_full_answers = pd.read_parquet(file.replace(".parquet", "-full-answers.parquet"))
#         if df_full_answers["PARSED_ANSWER"].isnull().sum() > 0:
#             #print(df_full_answers[df_full_answers["PARSED_ANSWER"].isnull()].FULL_ANSWER.values[0])
#             continue
#         else:
#             #print(df_full_answers)
#             idx = df.iloc[0, :].TX_RESPOSTAS.find("X")
#             print(df_full_answers.iloc[idx, :].FULL_ANSWER)
#             print()
#             # print("parsed:", df_full_answers.iloc[32, :].PARSED_ANSWER)
#             print()
#             spt, lang = df.iloc[0, :].SYSTEM_PROMPT_TYPE, df.iloc[0, :].LANGUAGE
#             print(spt, lang)
#             print()
#             print(parse_answer(df_full_answers.iloc[idx, :].FULL_ANSWER, None, spt, lang))

#         a = input()
#         print()

#     if new_df is None:
#         new_df = df
#     else:
#         # Concatenate dataframes
#         new_df = pd.concat([new_df, df]).reset_index(drop=True) 

#new_df.to_parquet("enem-experiments-results-processed.parquet")

#print(new_df)