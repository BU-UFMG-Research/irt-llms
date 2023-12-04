from abc import ABC, abstractmethod
import re
from transformers import LlamaForCausalLM , LlamaTokenizer

# Define abstract model class
class Model(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_answer_from_prompt(self, prompt, temperature=0.1):
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
    def __init__(self, model_size, token, device):
        """
        Args:
            model_size (str): model size
            token (str): token
            device (str): device
        """
        super().__init__()
        self.tokenizer = LlamaTokenizer.from_pretrained(f"meta-llama/Llama-2-{model_size}b-chat-hf", token=token)
        self.model = LlamaForCausalLM.from_pretrained(f"meta-llama/Llama-2-{model_size}b-chat-hf", token=token)
        self.model_size = model_size
        self.device = device
        self.model.to(device)

    def get_answer_from_prompt(self, prompt, temperature=0.1):
        """
        Get answer from prompt

        Args:
            prompt (str): prompt
            temperature (float): temperature

        Returns:
            str: parsed answer
        """
        inputs = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.device)
        outputs = self.model.generate(inputs, temperature=temperature)
        full_answer = self.tokenizer.batch_decode(outputs,skip_special_tokens=True)[0]
        return self.parse_answer(full_answer)