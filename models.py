from abc import ABC, abstractmethod
import re
from transformers import LlamaForCausalLM , LlamaTokenizer, set_seed

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

    def parse_answer(self, answer):
        ans = re.search('\([ABCDE]\)',answer).group().lstrip('(').rstrip(')') if re.search('\([ABCDE]\)',answer) else None
        if ans is None:
            ans = answer.split('[/INST]')[-1]
            ans = re.search('[ABCDE]\.',ans).group().rstrip('.') if re.search('[ABCDE]\.',ans) else None
        return ans


# Define LLAMA2 model class
class LLAMA2(Model):
    """
    LLAMA2 model class

    Attributes:
        model_size (str): model size
        token (str): token
        device (str): device
        tokenizer (LlamaTokenizer): tokenizer
        model (LlamaForCausalLM): model
    
    Methods:
        get_answer_from_prompt: get answer from prompt
        parse_answer: parse answer
    """
    def __init__(self, model_size, token, device, random_seed=0):
        """
        Args:
            model_size (str): model size
            token (str): token
            device (str): device
        """
        super().__init__()
        self.tokenizer = LlamaTokenizer.from_pretrained(f"meta-llama/Llama-2-{model_size}-chat-hf", token=token)
        self.model = LlamaForCausalLM.from_pretrained(f"meta-llama/Llama-2-{model_size}-chat-hf", token=token)
        self.model_size = model_size
        self.device = device
        self.model.to(device)
        set_seed(random_seed)
        print("Model config: ")
        print(self.model.config)
        print("Generation config: ")
        print(self.model.generation_config)

    def get_answer_from_question(self, question, temperature=0.1, system_prompt_type=None):
        """
        Get answer from question

        Args:
            question (dict): ENEM question
            temperature (float): temperature
            system_prompt_type (str): system prompt type (simple, chain-of-thought, llama2-paper). None for no system prompt

        Returns:
            str: parsed answer
        """
        prompt = self.create_prompt(question, system_prompt_type)
        inputs = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.device)
        outputs = self.model.generate(inputs, temperature=temperature) # We can check out the gen config by model.generation_config. More details in how to change the generation available in: https://huggingface.co/docs/transformers/generation_strategies
        full_answer = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return self.parse_answer(full_answer)
    
    def create_prompt(self, question, system_prompt_type=None):
        # For the multi-turn prompt, we need to add <s> and </s> tokens
        prompt = '[INST] '
        if system_prompt_type == "simple":
            prompt += '<<SYS>>\nYou are a machine designed to answer multiple choice questions with the correct alternative among A,B,C,D or E. Answer only with the correct alternative.\n<</SYS>>\n\n'
        elif system_prompt_type == "chain-of-though":
            raise NotImplementedError
        elif system_prompt_type == "llama2-paper":
            prompt += '<<SYS>>\nYou are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don\'t know the answer to a question, please don\'t share false information.\n<</SYS>>\n\n'
        prompt += f'{question["body"]}\n\nA. {question["A"]}\nB. {question["B"]}\nC. {question["C"]}\nD. {question["D"]}\nE. {question["E"]}\n[/INST]'
        return prompt