import json
import re
from read_json_config import fill_template
from query_llm import AskLLM

class PromptGenerator:
    def __init__(self, llm):
        self.llm = llm
        with open("config.json") as jsonfile:
            self.config = json.load(jsonfile)["PROMPTS"]

    def prompt_generator_dialogue(self, user_dialogue, prompt_type, llm="OPENAI"):
        prompt = fill_template(["DIALOGUE"], [user_dialogue], self.config[prompt_type])
        # ask llm 
        if llm == "FLAN":
            llm_response = self.llm.ask_llm_flan(prompt)
        else:
            llm_response = self.llm.ask_llm_openai(prompt)
        llm_response = re.sub('[^A-Za-z0-9 ]+', '', llm_response)
        return llm_response.lower().strip()

    def prompt_generator(self, prompt, llm="OPENAI"):
        if llm == "FLAN":
            llm_response = self.llm.ask_llm_flan(prompt)
        else:
            llm_response = self.llm.ask_llm_openai(prompt)
        llm_response = re.sub('[^A-Za-z0-9 ]+', '', llm_response)
        return llm_response.lower().strip()
    
if __name__ == "__main__":
    prompts = PromptGenerator(AskLLM())
    response = prompts.prompt_generator_dialogue("Yeah I'm good","YES_NO")
    print(response)
    response = prompts.prompt_generator_dialogue("yes let's go","YES_NO")
    print(response)
    