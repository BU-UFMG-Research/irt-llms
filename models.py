from abc import ABC, abstractmethod
import re
from transformers import LlamaForCausalLM , LlamaTokenizer, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed
import torch
import numpy as np
from openai import OpenAI

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
            if system_prompt_type == "zs-cot":
                system_prompt = """Let's think step by step to answer the following multiple choice question.
Instructions: Please answer the question below in the following format: 
Answer: (Option)
"""
            elif system_prompt_type == "few-shot":
                system_prompt = """You will answer a multiple choice question with the following format:
Question: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?
Options:
(A) 5
(B) 12
(C) 7
(D) 11
(E) 9
Answer Format:
Answer: (D) 11
Instructions: Please answer the question below in accordance with the provided format.
"""
        elif language == "pt-br":
            if system_prompt_type == "zs-cot":
                system_prompt = """Vamos pensar passo a passo para responder à seguinte questão de múltipla escolha.
Instruções: Por favor, responda à pergunta abaixo no seguinte formato: 
Resposta: (Opção)
"""
            elif system_prompt_type == "few-shot":
                system_prompt = """Você responderá uma questão de multipla escolha com o seguinte formato:
Questão: Roger tem 5 bolas de tênis. Ele compra mais 2 latas de bolas de tênis. Cada lata tem 3 bolas de tênis. Quantas bolas de tênis ele tem agora?
Alternativas:
(A) 5
(B) 12
(C) 7
(D) 11
(E) 9
Formato da Resposta:
Resposta: (D) 11
Instruções: Responda a questão a seguir com o formato definido anteriormente.
"""
        return system_prompt


    def parse_answer(self, answer, question):
        """
        Parse answer from model output (conservative parsing, considering that there is a [/INST] tag at the end of the answer])
        """
        pos_inst = answer.split('[/INST]')[-1]
        ans = pos_inst.strip()

        # Conservative parsing
        # Get the option after "Answer:" or "Resposta:"
        match = re.findall(r"(Answer|Resposta):[ ]{0,1}(\([A-E]\))", ans)
        if len(set(match)) == 1:
            # Return only the letter
            return match[0][-1].removeprefix("(").removesuffix(")")
        else:
            match = re.findall(r"(\([A-E]\))", ans)
            if len(set(match)) == 1:
                return match[0].removeprefix("(").removesuffix(")")
            else:
                match = re.findall(r"([A-E]\))", ans) # Case were there is only one parenthesis (e.g. "A)")
                if len(set(match)) == 1:
                    return match[0].removesuffix(")")
                else:
                    return None

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
        set_seed(self.seed)

    def get_answer_from_question(self, question, system_prompt_type, language):
        """
        Get answer from question
        """
        set_seed(self.seed)
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
        if system_prompt_type != "few-shot":
            prompt = f"""<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{question_word}: {question["body"]}\n\n"""
            for option in options_letters:
                prompt += f"({option}) {options[option]}\n"
            prompt += f"[/INST]"""
        else:
            # Slighly different prompt for few-shot
            option_word = "Options" if language == "en" else "Alternativas"
            prompt = f"""<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{question_word}: {question["body"]}\n{option_word}:\n"""
            for option in options_letters:
                prompt += f"({option}) {options[option]}\n"
            prompt += f"[/INST]"""

        return prompt
    
class Mistral(Model):
    """
    Mistral model class
    """

    def __init__(self, model_size, token, device, temperature=0.6, random_seed=0):
        super().__init__()
        self.model_size = model_size
        if self.model_size == "7b":
            self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", token=token)
            self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", token=token, device_map="auto", torch_dtype=torch.float16)
        elif self.model_size == "8x7b":
            self.bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )

            self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1", token=token)
            self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1", device_map="auto", quantization_config=self.bnb_config)

        self.device = device
        self.temperature = temperature
        self.seed = random_seed
        set_seed(random_seed)

    def get_answer_from_question(self, question, system_prompt_type, language):
        """
        Get answer from question
        """
        set_seed(self.seed)
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
        if system_prompt_type != "few-shot":
            prompt = f"""<s>[INST] {system_prompt}\n\n{question_word}: {question["body"]}\n\n"""
            for option in options_letters:
                prompt += f"({option}) {options[option]}\n"
            prompt += f"[/INST]"""
        else:
            # Slighly different prompt for few-shot
            option_word = "Options" if language == "en" else "Alternativas"
            prompt = f"""<s>[INST] {system_prompt}\n\n{question_word}: {question["body"]}\n{option_word}:\n"""
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
    
class GPT(Model):
    """
    GPT model class
    """

    def __init__(self, model, temperature=0.6, random_seed=0):
        super().__init__()
        self.model = model
        self.client = OpenAI()
        self.temperature = temperature
        self.seed = random_seed

    def get_answer_from_question(self, question, system_prompt_type, language, options_letters=None):
        """
        Get answer from question
        """
        if options_letters is None:
            options_letters = sorted(list(question["options"].keys()))
        
        system_prompt, prompt = self.create_prompt(question, system_prompt_type, language, options_letters)
        
        response = self.client.chat.completions.create(
            model=self.model,
            seed=self.seed,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
        )

        answer = response.choices[0].message.content
        #fingerpring = response.system_fingerprint  TODO: save the fingerprint to check reproducibility
        return self.parse_answer(answer, question), answer
    
    def create_prompt(self, question, system_prompt_type, language, options_letters):
        """
        Create prompt
        """
        # For the multi-turn prompt, we need to add <s> and </s> tokens and concatenate the previous turns
        options = question["options"]
        system_prompt = self.get_system_prompt(system_prompt_type, language, options_letters)
        question_word = "Questão" if language == "pt-br" else "Question"
        option_word = "Options" if language == "en" else "Alternativas"

        prompt = f"""{question_word}: {question["body"]}\n{option_word}:\n"""
        for option in options_letters:
            prompt += f"({option}) {options[option]}\n"

        return system_prompt, prompt


    