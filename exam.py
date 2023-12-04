import pandas as pd

class ENEM():
    def __init__(self, enem_exam, answer_order="ABCDE", question_order="random", seed=42):
        self.df_enem = pd.read_csv(f"data/parsed-enem-exams/{enem_exam}.csv")
        self.answer_order = list(answer_order)
        original_order = list("ABCDE")
        # Map the answer in the original order to the answer in the answer_order
        # We fisrt find the index of the answer in the original order, then we use that index to find the answer in the answer_order
        # For instance: if the answer is "B", we find the index of "B" in the original order, which is 1. 
        # Then we use that index to find the answer in the answer_order ("CABDE"), which is "A"
        # The corner case is where the answer is "anulada" (voided), in which case we just return "anulada"
        self.df_enem["answer"] = self.df_enem["answer"].apply(lambda x: answer_order[original_order.index(x)] if x in self.answer_order else "anulada")

        # We have columns A, B, C, D, E. Map them to answer_order
        self.df_enem.rename(columns={"A": self.answer_order[0], "B": self.answer_order[1], "C": self.answer_order[2], "D": self.answer_order[3], "E": self.answer_order[4]}, inplace=True)

        print(self.df_enem.head())
        a = input()

        # Shuffle questions if necessary
        if question_order == "random":
            self.df_enem = self.df_enem.sample(frac=1, random_state=seed).reset_index(drop=True)
        elif question_order == "original":
            pass
        else:
            raise Exception("Question order not implemented")
        
        print(self.df_enem.head())

        self.enem_exam = self.df_enem.to_dict(orient='records')
        print()
        print(self.enem_exam[0])

    def get_question(self, question_id):
        return self.enem_exam[question_id]

    def get_enem_size(self):
        return len(self.enem_exam)
    
    def get_correct_answer(self, question_id):
        return self.enem_exam[question_id]["answer"]