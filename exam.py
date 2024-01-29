import pandas as pd
import numpy as np
class ENEM():
    def __init__(self, enem_exam, exam_type, question_order="original", seed=42, language="pt-br", number_options=5, number_options_method="random"):
        self.df_enem = pd.read_csv(f"data/parsed-enem-exams/{language}/{exam_type}/{enem_exam}.csv")

        # Shuffle questions if necessary
        if question_order == "random":
            self.df_enem = self.df_enem.sample(frac=1, random_state=seed).reset_index(drop=True)
        elif question_order == "original":
            pass
        else:
            raise Exception("Question order not implemented")
            
        self.enem_exam = self.df_enem.to_dict(orient='records')

        # Dict has "A", "B", "C", "D", "E" keys. Nest them in a dict ("options")
        for question in self.enem_exam:
            options = {}
            for key in question.keys():
                if key in ["A", "B", "C", "D", "E"]:
                    options[key] = question[key]
            question["options"] = options

        # Remove "A", "B", "C", "D", "E" keys
        for question in self.enem_exam:
            for key in ["A", "B", "C", "D", "E"]:
                del question[key]

        if number_options >= 2 and number_options <= 4:
            if number_options_method == "random":
                random = np.random.RandomState(seed)
                
                for question in self.enem_exam:
                    correct_answer = question["answer"]
                    if correct_answer == "anulada":
                        continue
                    candidate_options = ["A", "B", "C", "D", "E"]
                    candidate_options.remove(correct_answer)
                    options_to_remove = random.choice(candidate_options, size=5-number_options, replace=False)
                    for option in options_to_remove:
                        del question["options"][option]
            else:
                raise Exception("Number of options method not implemented")
        elif number_options == 5:
            pass
        else:
            raise Exception("Number of options not implemented")

    def get_question(self, question_id):
        return self.enem_exam[question_id]

    def get_enem_size(self):
        return len(self.enem_exam)
    
    def get_correct_answer(self, question_id):
        return self.enem_exam[question_id]["answer"]
    
    def remapping_answer_pattern(self, answer_pattern):
        # Remap answer pattern to original order
        original_order = list("ABCDE")
        remapping_answer_pattern = ""
        for i in range(len(answer_pattern)):
            if answer_pattern[i] == "V" or answer_pattern[i] == "X":
                remapping_answer_pattern += answer_pattern[i]
            else:
                answer_order = eval(self.enem_exam[i]["answer_order"])
                remapping_answer_pattern += answer_order[original_order.index(answer_pattern[i])]
        return remapping_answer_pattern
    
    def get_question_number_array(self):
        return [self.enem_exam[i]["question"] for i in range(len(self.enem_exam))]
