import pandas as pd

class ENEM():
    def __init__(self, enem_exam):
        self.df_enem = pd.read_csv(f"data/parsed-enem-exams/{enem_exam}.csv")
        self.enem_exam = self.df_enem.to_dict(orient='records')

    def format_enem_prompt(self, question_id, sys=True):
        question = self.enem_exam[question_id]
        if sys:
            prompt += '<<SYS>>\nYou are a machine designed to answer multiple choice questions with the correct alternative among A,B,C,D or E. Answer only with the correct alternative.\n<</SYS>>\n\n'
        prompt += f'{question["body"]}\n\nA. {question["A"]}\nB. {question["B"]}\nC. {question["C"]}\nD. {question["D"]}\nE. {question["E"]}\n[/INST]'
        return prompt
    
    def get_enem_size(self):
        return len(self.enem_exam)
    
    def get_correct_answer(self, question_id):
        return self.enem_exam[question_id]["answer"]