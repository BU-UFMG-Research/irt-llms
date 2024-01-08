import glob
import re
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns

def parse_answer(answer):
    """
    Parser is not correct. Example:

        Aponte as alternativas que fazem sentido: (A), (B), (C), (D).

    Escolha a alternativa CORRETA: (B) 74,51.

    Justifique: O gráfico mostra que a esperança de vida ao nascer em 2013 foi exatamente a média das registradas nos anos de 2012 e de 2014. Então, a esperança de vida ao nascer em 2014 seria a média das registradas nos anos de 2013 e de 2015. A média de 74,23 e 74,51 é 74,32. Então, a esperança de vida ao nascer em 2014 seria 74,32.

    Resposta: (B) 74,51.

    The answer should be B, but the parser returns A.

    def get_formatted_answer(question, answer):
        gold = ["A.", "B.", "C.", "D.", "E."][question["gold"]]
        pred = answer

        # regex processing. Useful for zero-shot
        match_1 = re.findall(r"(?:|[Ll]etra |[Aa]lternativa )([ABCDE])\.", pred)
        match_2 = re.findall(r"(?:|[Ll]etra |[Aa]lternativa )([ABCDE])", pred)
        if len(match_1) > 0:
            pred = match_1[-1] + "."
        elif len(match_2) > 0:
            pred = match_2[-1] + "."
        else:
            print(f"Regex failed at processing {pred=}")
            print(f"{gold=}, {pred=}")

        return pred, gold

    """
    pos_inst = answer.split('[/INST]')[-1]
    ans = pos_inst.strip()

    print("ans")
    print(ans)
    a = input()

    pattern = r'Resposta: ([A-E])'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'Resposta: \(([A-E])\)'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'Answer: ([A-E])'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'Answer: \(([A-E])\)'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")

    pattern = r'answer is ([A-E])'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'answer is \(([A-E])\)'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'Answer: ([ABCDE])'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'A resposta correta é (\w):'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'[Tt]he answer is ([A-E])'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'answer is \(([A-E])\)'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
        
    pattern = r'A resposta correta é (\w) '
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")

    pattern = r'A resposta certa é (\w):'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("1")
    
    pattern = r'option ([A-E])'
    match = re.search(pattern, ans)
    if match:
        return match.group(1)
    
    print("match: ", re.match(r"^(A|B|C|D|E)$", ans))
    a = input()

    if re.match(r"^(A|B|C|D|E)$", ans):
        return ans
    
    pattern = r'\(([A-E])\)'
    match = re.search(pattern, ans)
    print(match)
    a = input()
    if match:
        return match.group(1)

    ans = re.search('[ABCDE]\.',ans).group().rstrip('.') if re.search('[ABCDE]\.',ans) else None
    print(ans)
    a = input()
    
    if ans is None:
        pos_inst = answer.split('[/INST]')[-1]
        ans = pos_inst.strip()
        ans = re.search('[ABCDE]\)',ans).group().rstrip(')') if re.search('[ABCDE]\)',ans) else None
        print(ans)
        a = input()

    return ans


files = glob.glob("enem-experiments-results/*")
# removing files with full-answers in the name
files = [file for file in files if "full-answers" not in file]
files.sort()

new_df = None
for file in files:
    df = pd.read_parquet(file)
    # Checking if there is any parsing error
    if "X" in df.iloc[0, :]["TX_RESPOSTAS"]:
        print("Parsing error in file ", file)
        df_full_answers = pd.read_parquet(file.replace(".parquet", "-full-answers.parquet"))
        if df_full_answers["PARSED_ANSWER"].isnull().sum() > 0:
            print(df_full_answers[df_full_answers["PARSED_ANSWER"].isnull()].FULL_ANSWER.values[0])
        else:
            print(df_full_answers)
            print(df.iloc[0, :])
            print()
            # print(df_full_answers.iloc[32, :].FULL_ANSWER)
            # print()
            # print("parsed:", df_full_answers.iloc[32, :].PARSED_ANSWER)
            # print()
            #print(parse_answer(df_full_answers.iloc[32, :].FULL_ANSWER))

        a = input()
        print()

    if new_df is None:
        new_df = df
    else:
        # Concatenate dataframes
        new_df = pd.concat([new_df, df]).reset_index(drop=True) 

#new_df.to_parquet("enem-experiments-results-processed.parquet")

#print(new_df)