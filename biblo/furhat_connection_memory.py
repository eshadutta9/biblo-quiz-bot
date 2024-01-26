from furhat_remote_api import FurhatRemoteAPI
import time
import random
from read_json_config import read_json
from generate_prompt import PromptGenerator
from query_llm import AskLLM
from generate_qb_memory import make_api_call

class Status:
    def __init__(self):
        self.message = ''
        self.success = ''

class FurhatConnection:
    def __init__(self, llm):
        self.furhat = FurhatRemoteAPI("localhost")
        self.furhat.set_voice(name='Matthew')
        self.furhat.set_face(mask="adult", character="Alex")
        self.unclear = read_json("UNCLEAR_DIALOGUE")
        self.no_dialog = read_json("NO_DIALOGUE")
        self.end_dialog = read_json("SESSION_END_DIALOGUE")
        self.prompts = read_json("PROMPTS")
        self.gestures = read_json("FURHAT_GESTURES")  
        self.prompter = PromptGenerator(llm)
        self.dialogue = {}

    def furhat_listen(self, timeout=15, to_check = True, context = "study", current_user_context = "study", user_id = 0):
        result = Status()
        start_time = time.time()
        while not result.message and time.time() - start_time < timeout:
            result = self.furhat.listen()
        print(result)
        if to_check:
            is_dialogue, dialogue = self.check_response(result)
            if is_dialogue:
                if context != "study":
                    self.dialogue["USER"] = dialogue
                    self.dialogue["context"] = context
                    self.dialogue["current_user_context"] = current_user_context
                    self.dialogue["user_id"] = user_id
                    print("STM Dialogue: ", self.dialogue)
                    # self.send_to_stm(self.dialogue)
                    self.dialogue = {}
                return dialogue
            else:
                return
        else:
            self.dialogue["USER"] = result.message
            return result


    def check_response(self, result=Status()):
        if not result.success or not result.message:
            user_dialogue = self.ask_again("no_dialog")
        else:
            # is_coherent = self.prompter.prompt_generator_dialogue(result.message, "COHERENT_DIALOGUE")
            # print(is_coherent)
            is_coherent = 'yes'
            if is_coherent == 'yes':
                return True, result.message
            else:
                user_dialogue = self.ask_again("unclear_dialog")
        
        if not user_dialogue.success or not user_dialogue.message:
            return False, ""
        else:
            # is_coherent = self.prompter.prompt_generator_dialogue(result.message, "COHERENT_DIALOGUE")
            # print(is_coherent)
            is_coherent = 'yes' #temporary since llm is giving no always
            if is_coherent == 'yes':
                return True, user_dialogue.message
            else:
                return False, ""

    def ask_again(self, type):
        if type == 'no_dialog':
            self.furhat_speak(self.no_dialog)
            user_dialogue = self.furhat_listen(timeout=30, to_check=False)
            if not user_dialogue.message:
                self.furhat_end_session()
        elif type == 'unclear_dialog':
            self.furhat_speak(random.choice(self.unclear))
            user_dialogue = self.furhat_listen(timeout=15, to_check=False)
        return user_dialogue
        
    
    def furhat_speak(self, speech, context = "study", block_flag = True):
        if context != "study":
            self.dialogue["context"] = context
            if "BOT" not in self.dialogue:
                self.dialogue["BOT"] = speech
            else:
                self.dialogue["BOT"] = self.dialogue["BOT"] + ". " + speech
        self.furhat.say(text=speech, blocking=block_flag)

    def furhat_gesture(self, gesture):
        if gesture in self.gestures:
            gesture_name = self.gestures[gesture]
            self.furhat.gesture(name=gesture_name)
        else:
            self.furhat.gesture(name=self.gestures["default"])
    
    def send_to_stm(self, general_talk_payload):
        route = "user_convo"
        make_api_call(route, "POST", general_talk_payload)

    def furhat_end_session(self):
        self.furhat.say(text=self.end_dialog, blocking=True)


if __name__ == "__main__":
    furhat = FurhatConnection(AskLLM())
    furhat.furhat_speak("Hi there. How are you doing today?")
    dialogue = furhat.furhat_listen(timeout=10)
    # dialogue = furhat.furhat_listen_new()
    print(dialogue)
    #TODO : If want to stop, stop