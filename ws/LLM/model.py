import os
import torch
import warnings
from opencc import OpenCC
from LLM.QwenModel import LLM
warnings.filterwarnings("ignore")
class AI_Agent:
    def __init__(self):
        path = "/mnt/d" + "/LLM"
        model_name = path + "/" + os.listdir(path)[1]
        setting = {
            "device": torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            "model_name": model_name,
            "set": """[Only Response in traditional Chinese] 
                    [回答可以更像聊天一樣，不要專注於回答問題]
                    [不要把自己當成解決問題的AI助理]
                    [不能說自己是AI]
                    [以找話題聊天為首要目標，不要結束對話]
                    """,
            "role": "oO貓咪大師Oo"
        }
        print(setting["device"])
        print(setting["model_name"])
        self.model = LLM(setting)
        self.cc = OpenCC('s2t')

    def say(self, prompt):
        text = self.model.predict(prompt)
        res = self.cc.convert(text)
        return res