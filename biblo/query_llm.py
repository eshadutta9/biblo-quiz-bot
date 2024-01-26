from transformers import T5Tokenizer, T5ForConditionalGeneration
import requests


class AskLLM:
    def __init__(self) -> None:
        self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
        self.BASE_URL = "http://127.0.0.1:3000/api/v1"

    def ask_llm_flan(self, prompt):
        print("Prompt to FLAN LLM is :", prompt)
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Response from FLAN LLM is : ", response)
        return response

    def make_api_call(self, route, method, data):
        url = f"{self.BASE_URL}/{route}"

        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError("Invalid HTTP method")
        return response.json()

    def ask_llm_openai(self, prompt):
        payload = {"user": prompt}
        print("Prompt to OPENAI LLM is :", payload)
        res = self.make_api_call("ask_llm_wo_mem", "POST", payload)
        print("Response from OPENAI LLM is : ", res["data"])
        return res["data"]


if __name__ == "__main__":
    prompt = "Do I want to stop the session if I say the following, answer yes/no: I want to talk to you"
    AskLLM().ask_llm_openai(prompt)
