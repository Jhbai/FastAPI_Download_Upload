import os
import torch
import warnings
warnings.filterwarnings("ignore")
from transformers import AutoModelForCausalLM, AutoTokenizer
class LLM:
    def __init__(self, setup):
        """設定資訊"""
        self.setup = setup

        """準備模型參數"""
        self.device = setup["device"]
        self.model = AutoModelForCausalLM.from_pretrained(setup["model_name"], torch_dtype="auto", device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(setup["model_name"])
        self.messages = [{"role": self.setup["role"], "content": self.setup["set"]}]
        self.role = self.setup["role"]

    def predict(self, prompt = "Give me a short introduction to large language model."):
        self.messages += [{"role": "Others", "content": prompt}]
        if len(self.messages) > 51:
            self.messages.pop(1)
        text = self.tokenizer.apply_chat_template(
            self.messages,
            tokenize=False,
            add_generation_prompt=True
            )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        res = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        self.messages += [{"role": self.role, "content": res}]
        return res