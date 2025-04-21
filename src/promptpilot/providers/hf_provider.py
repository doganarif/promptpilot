from transformers import pipeline
from .base import BaseProvider

class HFProvider(BaseProvider):
    def __init__(self, model_name=None):
        self.model_name = model_name or 'gpt2'
        self.pipe = pipeline('text-generation', model=self.model_name)

    def send_prompt(self, prompt: str):
        out = self.pipe(prompt, max_length=200)[0]['generated_text']
        return out, len(out.split())
