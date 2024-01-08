from abc import ABC, abstractmethod
import re
from transformers import LlamaForCausalLM , LlamaTokenizer, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed
import torch
import numpy as np

# Define abstract model class
class Model(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_answer_from_question(self, prompt, temperature=0.1):
        pass
   
    @abstractmethod
    def create_prompt(self, question, system_prompt_type, language):
        pass

    def get_system_prompt(self, system_prompt_type, language, options_letters):
        if language == "en":
            if system_prompt_type == "simple":
                # Create system_prompt using options_letters
                system_prompt = "You are a machine designed to answer multiple choice questions with the correct alternative among "
                for option in options_letters[:-1]:
                    system_prompt += f"({option}), " if len(options_letters) > 2 else f"({option}) "
                system_prompt += f"or ({options_letters[-1]}). Answer only with the correct alternative."    
            elif system_prompt_type == "cot":
                system_prompt = "Formulate a logical reasoning chain explanation that allows you to answer the multiple-choice question below. Only one alternative is correct.\nDesired format: point out the alternatives that make sense, choose the CORRECT alternative and justify it, and finish justifying why the other alternatives are incorrect. End the explanation with \"Answer: \" followed by the alternative."
        elif language == "pt-br":
            if system_prompt_type == "simple":
                # Create system_prompt using options_letters
                system_prompt = "Você é uma máquina projetada para responder questões de múltipla escolha com a alternativa correta entre "
                for option in options_letters[:-1]:
                    system_prompt += f"({option}), " if len(options_letters) > 2 else f"({option}) "
                system_prompt += f"ou ({options_letters[-1]}). Responda apenas com a alternativa correta."
            elif system_prompt_type == "cot":
                system_prompt = "Formule uma explicação em cadeia que permita responder à questão de múltipla escolha abaixo. Apenas uma alternativa é correta.\nFormato desejado: aponte as alternativas que fazem sentido, escolha a alternativa CORRETA e justifique, e termine justificando porque as demais alternativas estão incorretas. Encerre a explicação com \"Resposta: \" seguido pela alternativa."

        return system_prompt


    def parse_answer(self, answer, question):
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

        pattern = r'Resposta: ([A-E])'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'Resposta: \(([A-E])\)'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'Answer: ([A-E])'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'Answer: \(([A-E])\)'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)

        pattern = r'answer is ([A-E])'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'answer is \(([A-E])\)'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'Answer: ([ABCDE])'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'A resposta correta é (\w):'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'[Tt]he answer is ([A-E])'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'answer is \(([A-E])\)'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
            
        pattern = r'A resposta correta é (\w) '
        match = re.search(pattern, ans)
        if match:
            return match.group(1)

        pattern = r'A resposta certa é (\w):'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
        
        pattern = r'option ([A-E])'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)

        if re.match(r"^(A|B|C|D|E)$", ans):
            return ans
        
        pattern = r'\(([A-E])\)'
        match = re.search(pattern, ans)
        if match:
            return match.group(1)
    
        ans = re.search('[ABCDE]\.',ans).group().rstrip('.') if re.search('[ABCDE]\.',ans) else None
        
        if ans is None:
            pos_inst = answer.split('[/INST]')[-1]
            ans = pos_inst.strip()
            ans = re.search('[ABCDE]\)',ans).group().rstrip(')') if re.search('[ABCDE]\)',ans) else None
        
        if ans is None and question is not None:
            for option in ['A', 'B', 'C', 'D', 'E']:
                if str(question["options"][option]) in pos_inst:
                    return option
        
        return ans


# Define LLAMA2 model class
class LLAMA2(Model):
    """
    LLAMA2 model class
    """
    def __init__(self, model_size, token, device, temperature=0.6, quantization=None, random_seed=0):
        """
        Args:
            model_size (str): model size
            token (str): token
            device (str): device
        """
        super().__init__()

        if quantization is not None:
            if quantization == "4bit":
                self.bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16
                )
            elif quantization == "8bit":
                self.bnb_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    bnb_8bit_use_double_quant=True,
                    bnb_8bit_quant_type="nf8",
                    bnb_8bit_compute_dtype=torch.float16
                )
            else:
                raise Exception("Invalid load mode. Please choose between 4bit and 8bit.")
            
            self.model = LlamaForCausalLM.from_pretrained(f"meta-llama/Llama-2-{model_size}-chat-hf", token=token, device_map="auto", quantization_config=self.bnb_config)
        else:
            self.model = LlamaForCausalLM.from_pretrained(f"meta-llama/Llama-2-{model_size}-chat-hf", token=token, device_map="auto", torch_dtype=torch.float16)

        self.tokenizer = LlamaTokenizer.from_pretrained(f"meta-llama/Llama-2-{model_size}-chat-hf", token=token)            
        self.model_size = model_size
        self.device = device
        self.temperature = temperature
        self.seed = random_seed
        set_seed(random_seed)

    def get_answer_from_question(self, question, system_prompt_type, language):
        """
        Get answer from question
        """
        prompt = self.create_prompt(question, system_prompt_type, language)
        inputs = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.device)
        outputs = self.model.generate(inputs, temperature=self.temperature) # We can check out the gen config by model.generation_config. More details in how to change the generation available in: https://huggingface.co/docs/transformers/generation_strategies
        full_answer = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return self.parse_answer(full_answer, question), full_answer
    
    def create_prompt(self, question, system_prompt_type, language):
        """
        Create prompt
        """
        # For the multi-turn prompt, we need to add <s> and </s> tokens and concatenate the previous turns        
        options = question["options"]
        options_letters = sorted(list(options.keys()))
        system_prompt = self.get_system_prompt(system_prompt_type, language, options_letters)
        question_word = "Questão" if language == "pt-br" else "Question"
        prompt = f"""<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{question_word}: {question["body"]}\n\n"""
        for option in options_letters:
            prompt += f"({option}) {options[option]}\n"
        prompt += f"[/INST]"""

        return prompt
    
class Mistral(Model):
    """
    Mistral model class
    """

    def __init__(self, token, device, temperature=0.6, random_seed=0):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", token=token)
        self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", token=token, device_map="auto", torch_dtype=torch.float16)
        self.device = device
        self.temperature = temperature
        self.seed = random_seed
        set_seed(random_seed)

    def get_answer_from_question(self, question, system_prompt_type, language):
        """
        Get answer from question
        """
        prompt = self.create_prompt(question, system_prompt_type, language)
        inputs = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.device)
        outputs = self.model.generate(inputs, temperature=self.temperature, do_sample=True, top_p=0.9, top_k=0, max_length=4096, pad_token_id=self.tokenizer.eos_token_id)
        full_answer = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return self.parse_answer(full_answer, question), full_answer
    
    def create_prompt(self, question, system_prompt_type, language):
        """
        Create prompt
        """
        # For the multi-turn prompt, we need to add <s> and </s> tokens and concatenate the previous turns
        options = question["options"]
        options_letters = sorted(list(options.keys()))
        system_prompt = self.get_system_prompt(system_prompt_type, language, options_letters)
        question_word = "Questão" if language == "pt-br" else "Question"
        prompt = f"""<s>[INST] {system_prompt}\n\n{question_word}: {question["body"]}\n\n"""
        for option in options_letters:
            prompt += f"({option}) {options[option]}\n"
        prompt += f"[/INST]"""

        return prompt
    
class RandomModel(Model):
    """
    Random baseline model class
    """

    def __init__(self, random_seed=0):
        super().__init__()
        self.random = np.random.RandomState(random_seed)
        self.seed = random_seed

    def get_answer_from_question(self, question, system_prompt_type=None, language=None):
        """
        Get answer from question
        """
        answer = self.random.choice(list("ABCDE"))
        return answer, answer
    
    def create_prompt(self):
        """
        Create prompt
        """
        return None
    