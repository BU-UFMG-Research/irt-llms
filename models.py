from abc import ABC, abstractmethod
import re
from transformers import LlamaForCausalLM , LlamaTokenizer, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed
import torch

# Define abstract model class
class Model(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_answer_from_question(self, prompt, temperature=0.1):
        pass
   
    @abstractmethod
    def create_prompt(self, question, system_prompt_type=None):
        pass

    def parse_answer(self, answer, question):
        pos_inst = answer.split('[/INST]')[-1]
        ans = pos_inst.strip()

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
                if question[option] in pos_inst:
                    return option
        
        return ans


# Define LLAMA2 model class

"""
4 bit quantization code

from transformers import BitsAndBytesConfig


nf4_config = BitsAndBytesConfig(
   load_in_4bit=True,
   bnb_4bit_quant_type="nf4",
   bnb_4bit_use_double_quant=True,
   bnb_4bit_compute_dtype=torch.bfloat16
)

model_nf4 = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=nf4_config)


"""
class LLAMA2(Model):
    """
    LLAMA2 model class
    """
    def __init__(self, model_size, token, device, max_time=120, temperature=0.6, load_4bit=False, random_seed=0):
        """
        Args:
            model_size (str): model size
            token (str): token
            device (str): device
        """
        super().__init__()

        if load_4bit:
            self.bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )

        self.tokenizer = LlamaTokenizer.from_pretrained(f"meta-llama/Llama-2-{model_size}-chat-hf", token=token)
        if load_4bit:
            self.model = LlamaForCausalLM.from_pretrained(f"meta-llama/Llama-2-{model_size}-chat-hf", token=token, device_map="auto", quantization_config=self.bnb_config)
        else:
            self.model = LlamaForCausalLM.from_pretrained(f"meta-llama/Llama-2-{model_size}-chat-hf", token=token, device_map="auto", torch_dtype=torch.float16)
        self.model_size = model_size
        self.device = device
        self.max_time = max_time # Max time in seconds to generate an answer
        self.temperature = temperature
        self.seed = random_seed
        set_seed(random_seed)

    def get_answer_from_question(self, question, system_prompt_type=None):
        """
        Get answer from question
        """
        prompt = self.create_prompt(question, system_prompt_type)
        inputs = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.device)
        outputs = self.model.generate(inputs, temperature=self.temperature, max_time=self.max_time) # We can check out the gen config by model.generation_config. More details in how to change the generation available in: https://huggingface.co/docs/transformers/generation_strategies
        full_answer = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return self.parse_answer(full_answer, question), full_answer
    
    def create_prompt(self, question, system_prompt_type=None, language="pt-br"):
        """
        Create prompt
        """
        # For the multi-turn prompt, we need to add <s> and </s> tokens and concatenate the previous turns

        if language == "en":
            question_word = "Question"
            if system_prompt_type == "simple":
                system_prompt = '\nYou are a machine designed to answer multiple choice questions with the correct alternative among (A),(B),(C),(D) ou (E). Answer only with the correct alternative.'
            elif system_prompt_type == "cot":
                raise NotImplementedError
        elif language == "pt-br":
            question_word = "Questão"
            if system_prompt_type == "simple":
                system_prompt = 'Você é uma máquina projetada para responder questões de múltipla escolha com a alternativa correta entre (A),(B),(C),(D) ou (E). Responda apenas com a alternativa correta.'
            elif system_prompt_type == "cot":
                raise NotImplementedError
            
        prompt = f"""<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{question_word}: {question["body"]}\n\n(A) {question["A"]}\n(B) {question["B"]}\n(C) {question["C"]}\n(D) {question["D"]}\n(E) {question["E"]} [/INST]\n"""

        return prompt
    
class Mistral(Model):
    """
    Mistral model class
    """

    def __init__(self, token, device, max_time=120, temperature=0.6, random_seed=0):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", token=token)
        self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", token=token, device_map="auto", torch_dtype=torch.float16)
        self.device = device
        self.max_time = max_time
        self.temperature = temperature
        self.seed = random_seed
        set_seed(random_seed)

    def get_answer_from_question(self, question, system_prompt_type=None):
        """
        Get answer from question
        """
        prompt = self.create_prompt(question, system_prompt_type)
        inputs = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.device)
        outputs = self.model.generate(inputs, temperature=self.temperature, max_time=self.max_time, do_sample=True, top_p=0.9, top_k=0, max_length=4096)
        full_answer = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return self.parse_answer(full_answer, question), full_answer
    
    def create_prompt(self, question, system_prompt_type=None, language="pt-br"):
        """
        Create prompt
        """
        # For the multi-turn prompt, we need to add <s> and </s> tokens and concatenate the previous turns

        if language == "en":
            question_word = "Question"
            if system_prompt_type == "simple":
                system_prompt = "You are a machine designed to answer multiple choice questions with the correct alternative among (A),(B),(C),(D) ou (E). Answer only with the correct alternative."
            elif system_prompt_type == "cot":
                raise NotImplementedError
        elif language == "pt-br":
            question_word = "Questão"
            if system_prompt_type == "simple":
                system_prompt = "Você é uma máquina projetada para responder questões de múltipla escolha com a alternativa correta entre (A),(B),(C),(D) ou (E). Responda apenas com a alternativa correta."
            elif system_prompt_type == "cot":
                raise NotImplementedError
            
        prompt = f"""<s>[INST] {system_prompt}\n\n{question_word}: {question["body"]}\n\n(A) {question["A"]}\n(B) {question["B"]}\n(C) {question["C"]}\n(D) {question["D"]}\n(E) {question["E"]} [/INST]"""

        return prompt




