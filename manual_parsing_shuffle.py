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
# Get only shuffle files
files = [file for file in files if "shuffle" in file]
print("Total files:", len(files))
files.sort()

files_parsed = glob.glob("enem-experiments-results-new-parsing-shuffle/*")
files_parsed = [file for file in files_parsed if "full-answers" not in file]
files_parsed = [file.split("/")[-1] for file in files_parsed]

files = [file for file in files if file.split("/")[-1] not in files_parsed]
files = files[::-1]

new_df = None
count = 0
total = 0
count_x = 0
errors_exam = {}
errors_language = {}
errors_model = {}
for file in files:
    print("Processing file ", file)
    print()
    new_file = file.replace("enem-experiments-results", "enem-experiments-results-new-parsing-shuffle")

    df = pd.read_parquet(file)
    df_full_answers = pd.read_parquet(file.replace(".parquet", "-full-answers.parquet"))

    enem_exam = df.iloc[0, :].ENEM_EXAM
    enem_exam_type = df.iloc[0, :].ENEM_EXAM_TYPE
    question_order = df.iloc[0, :].QUESTION_ORDER
    language = df.iloc[0, :].LANGUAGE
    seed = df.iloc[0, :].SEED
    number_options = df.iloc[0, :].NUMBER_OPTIONS

    enem = ENEM(enem_exam=enem_exam, exam_type=enem_exam_type, 
                question_order=question_order, seed=seed,
                language=language, number_options=number_options)

    new_TX_RESPOSTAS_SHUFFLE = ""
    new_RESPONSE_PATTERN = ""
    new_CTT_SCORE = 0

    # Iterate over df_full_answers
    for idx, row in df_full_answers.iterrows():
        full_answer = row.FULL_ANSWER
        parsed_answer = row.PARSED_ANSWER
        correct_answer = row.CORRECT_ANSWER

        if parsed_answer == "anulada":
            parsed_answer = "V"

        # Try to reparse
        if parsed_answer is None:
            # 1) try to split by "(D) 11"
            ans = full_answer.split("[/INST]")[-1].split("(D) 11")[-1].strip()
            # Parse the ans using the Conservative parsing
            # Get the option after "Answer:" or "Resposta:"
            match = re.findall(r"(?i)(Answer|Resposta):[ ]{0,1}(\([A-E]\))", ans)
            if len(set(match)) == 1:
                # Return only the letter
                parsed_answer = match[0][-1].removeprefix("(").removesuffix(")")
            else:
                match = re.findall(r"(\([A-E]\))", ans)
                if len(set(match)) == 1:
                    parsed_answer = match[0].removeprefix("(").removesuffix(")")
                else:
                    match = re.findall(r"([A-E]\))", ans) # Case were there is only one parenthesis (e.g. "A)")
                    if len(set(match)) == 1:
                        parsed_answer = match[0].removesuffix(")")
                    else:
                        match = re.findall(r"(?i)(Answer|Resposta):[ ]{0,1}([A-E])", ans)
                        if len(set(match)) == 1:
                            parsed_answer = match[0][-1]
                        else:
                            parsed_answer = None
            
            # Conservative parsing failed:
            # Parse the following patter: Correct answer: (B)
            if parsed_answer is None:
                match = re.findall(r"(?i)Correct answer: \([A-E]\)", ans)
                if len(set(match)) == 1:
                    parsed_answer = match[0][-2].removeprefix("(").removesuffix(")")
                else:
                    parsed_answer = None
            
            # Get also the following formats:
            # A resposta é (A)
            # A resposta correta é (A)
            # The answer is (A)
            # The correct answer is (A)
            if parsed_answer is None:
                match = re.findall(r"(?i)(A resposta é|A resposta correta é|The answer is|The correct answer is|The best answer is|La respuesta correcta es) \(([A-E])\)", ans)
                if len(set(match)) == 1:
                    parsed_answer = match[0][1].removeprefix("(").removesuffix(")")
                else:
                    parsed_answer = None

            # Conservative parsing failed:
            # LLAMA models try to have an explanation for the answer.
            if parsed_answer is None:
                ans_no_exp = ans.split("Explanation:")[0]
                match = re.findall(r"(\([A-E]\))", ans_no_exp)
                if len(set(match)) == 1:
                    parsed_answer = match[0].removeprefix("(").removesuffix(")")
                else:
                    parsed_answer = None

            # If parsed_answer is None, get the cases where the model refuses to answer
            if "which option do you think is the correct answer?" in full_answer.lower() or "can you" in full_answer.lower() or "i'm just an ai" in full_answer.lower() or "i cannot" in full_answer.lower() or "i cannot assist you with questions that are not in english" in full_answer.lower() or "not in the form of a multiple-choice question" in full_answer.lower() or "i'm not able to answer this question" in full_answer.lower() or "apologize" in full_answer.lower() or "i cannot answer" in full_answer.lower() or "large language model" in full_answer.lower() or "i notice that the question" in full_answer.lower() or "i'm a large language model" in full_answer.lower() or "i'm happy to help" in full_answer.lower() or "is not a multiple choice question" in full_answer.lower():
                parsed_answer = "X"

            # Sometimes the model have more than one answer after splitting by "(D) 11". Parse this as X
            if parsed_answer is None:
                match = re.findall(r"(?i)(Answer|Resposta):[ ]{0,1}(\([A-E]\))", ans)
                if len(set(match)) > 1:
                    parsed_answer = "X"
                match = re.findall(r"(?i)(A resposta é|A resposta correta é|The answer is|The correct answer is|The best answer is|La respuesta correcta es) \(([A-E])\)", ans)
                if len(set(match)) > 1:
                    parsed_answer = "X"
                match = re.findall(r"(?i)Correct answer: \([A-E]\)", ans)
                if len(set(match)) > 1:
                    parsed_answer = "X"

            # Model answer things like: Could you please provide a more specific and concrete question that I can answer?
            if parsed_answer is None:
                match = re.findall(r"provide a more specific and concrete question", full_answer.lower())
                if len(set(match)) >= 1:
                    parsed_answer = "X"
            
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
        
        new_TX_RESPOSTAS_SHUFFLE += parsed_answer
        new_RESPONSE_PATTERN += "1" if parsed_answer == correct_answer else "0"
        new_CTT_SCORE += 1 if parsed_answer == correct_answer else 0

    df["TX_RESPOSTAS_SHUFFLE"] = new_TX_RESPOSTAS_SHUFFLE
    df["TX_RESPOSTAS"] = enem.remapping_answer_pattern(new_TX_RESPOSTAS_SHUFFLE)
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