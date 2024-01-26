from furhat_connection import FurhatConnection
from generate_prompt import PromptGenerator
from query_llm import AskLLM
from db_conn import DBConn
from read_json_config import read_json, fill_template
from ui import render_ui, show_evaluation, session_start
from generate_qb import generate_qb_topic
import random
import math

class Biblo:
    def __init__(self) -> None:
        self.llm = AskLLM()
        self.furhat_conn = FurhatConnection(self.llm)
        self.prompter = PromptGenerator(self.llm)
        self.sql_conn = DBConn()  
        self.user_id = 0
        self.user_name = ""

    def introduce(self):
        try:
            user, new_user = self.sql_conn.fetch_current_user()
            self.user_id = user[0]
            if new_user:
                intro_template = read_json("INTRODUCTION_NEW_USER")
                self.furhat_conn.furhat_speak(intro_template["1"])
                self.furhat_conn.furhat_speak(intro_template["2"])
                user_dialogue = self.furhat_conn.furhat_listen()
                user_name = self.prompter.prompt_generator_dialogue(user_dialogue, "NAME", "FLAN")
                self.sql_conn.update_name(self.user_id,user_name)
                self.user_name = user_name
                bot_dialogue = fill_template(["NAME"], [user_name], intro_template["3"])
            
            else:
                intro_template = read_json("INTRODUCTION_RETURNING_USER")
                self.furhat_conn.furhat_speak(intro_template["1"])
                self.user_name = user[1]  # get name from response
                bot_dialogue = fill_template(["NAME"], [self.user_name], intro_template["2"])
            
            self.furhat_conn.furhat_speak(bot_dialogue)
            user_dialogue = self.furhat_conn.furhat_listen()
            study_flag = self.prompter.prompt_generator_dialogue(user_dialogue, "YES_NO")
            print("Study flag: ", study_flag)
            
            if study_flag == 'yes':
                return True
            else:
                return False
        
        except Exception as e:
            raise Exception(e)

    def choose_topic(self):
        try:
            topic_templates = read_json("TOPICS")
            self.furhat_conn.furhat_speak(topic_templates["1"])
            user_dialogue = self.furhat_conn.furhat_listen()
            topic_chosen = self.prompter.prompt_generator_dialogue(user_dialogue, "TOPIC","FLAN")
            if "profit" in topic_chosen:
                topic_chosen = "gain"
            if topic_chosen not in read_json("LIST_OF_TOPICS"):
                self.furhat_conn.furhat_speak(topic_templates["2"])
                user_dialogue = self.furhat_conn.furhat_listen()
                topic_flag = self.prompter.prompt_generator_dialogue(user_dialogue, "YES_NO")
                if topic_flag == 'yes':
                    topic_chosen = "bodmas"
                else:
                    topic_chosen = self.prompter.prompt_generator_dialogue(user_dialogue, "TOPIC", "FLAN")
                    if "profit" in topic_chosen:
                        topic_chosen = "gain"
                    if topic_chosen not in read_json("LIST_OF_TOPICS"):
                        topic_chosen = "bodmas"
                    
            bot_dialogue = fill_template(["TOPIC"], [topic_chosen], topic_templates["3"])
            self.furhat_conn.furhat_speak(bot_dialogue)
            return topic_chosen
            
        except Exception as e:
            raise Exception(e)
        
    def quiz(self, topic_chosen):
        questions_asked = 0
        to_study = True
        correct_questions, incorrect_questions = 0,0
        total_questions = read_json("TOTAL_QUESTIONS")
        emotion_prompts = read_json("PROMPTS")
        quiz_dialogue = read_json("QUIZ_DIALOGUE")
        try:
            qb = generate_qb_topic(topic_chosen)
            started = False
            for question in qb:
                if started:
                    self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["NEXT_QUESTION"]))
                started = True

                self.furhat_conn.furhat_speak(question["question"], False)
                self.furhat_conn.furhat_speak("The options are: ")
                for option in question["options"]:
                    self.furhat_conn.furhat_speak(option, False)

                question["choice"] = render_ui(question, self.furhat_conn)
                
                if question["choice"] == question["correct"]:
                    is_correct = True
                    correct_questions += 1

                    self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["CORRECT_ANSWER"]))
                    if correct_questions >= math.floor(total_questions/2):
                        self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["MANY_CORRECT_ANSWERS"]))

                else:
                    is_correct = False
                    incorrect_questions += 1
                    # render on UI, incorrect answer
                    self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["INCORRECT_ANSWER"]))
                    self.furhat_conn.furhat_speak(f"The correct answer is {question['correct']}, you answered {question['choice']}")
                    if incorrect_questions >= math.floor(total_questions/2):
                        self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["MANY_INCORRECT_ANSWERS"]))
                
                show_evaluation(is_correct, question)
                
                emotion = self.detect_emotion()
                questions_asked += 1

                user_answer = "correct" if is_correct else "incorrect"
                llm_prompt = fill_template(["RIGHT/WRONG", "EMOTION"], [user_answer, emotion], emotion_prompts["EMOTION_EXPRESSION"])
                llm_resp = self.llm.ask_llm_openai(llm_prompt)
                self.furhat_conn.furhat_gesture(llm_resp)

                if is_correct:
                    self.furhat_conn.furhat_speak("Would you like to hear the working?", block_flag = True)
                    user_dialogue = self.furhat_conn.furhat_listen()
                    explanation_wanted = self.prompter.prompt_generator_dialogue(user_dialogue, "YES_NO")
                    if explanation_wanted == 'yes':
                        self.furhat_conn.furhat_speak(question["explanation"])
                else:
                    self.furhat_conn.furhat_speak(question["explanation"])

                if questions_asked < read_json("TOTAL_QUESTIONS"):
                    llm_prompt = fill_template(["RIGHT/WRONG", "EMOTION"], [user_answer, emotion], emotion_prompts["EMOTION_DIALOGUE"])
                    llm_resp = self.llm.ask_llm_openai(llm_prompt)
                    if llm_resp.strip().lower() in ["yes", "maybe"]:
                        self.furhat_conn.furhat_speak(f"Do you want to take a break? {self.user_name}")
                        user_dialogue = self.furhat_conn.furhat_listen()
                        break_wanted = self.prompter.prompt_generator_dialogue(user_dialogue, "YES_NO")
                        if break_wanted == 'yes':
                            self.furhat_conn.furhat_speak("Okay, let's take a break")
                            to_study = self.general_talk()
                
                if not to_study:
                    break
            
            return correct_questions, incorrect_questions

        except Exception as e:
            raise Exception(e)

    def detect_emotion(self):
        emotion = self.sql_conn.fetch_emotion(self.user_id)
        if emotion in ["", "Fearful", "Disgusted"] or emotion is None:
            emotion = "Neutral"
        elif emotion in ["Angry", "Sad"]:
            emotion = "Sad"
        elif emotion in ["Happy", "Surprised"]:
            emotion = "Happy"
        return emotion

    def general_talk(self):
        try:
            bot_dialogue = random.choice(read_json("GENERAL_TALK"))
            prompt_list = read_json("PROMPTS")
            self.furhat_conn.furhat_speak(bot_dialogue)
            dialog_length = 0
            while True:
                user_dialogue = self.furhat_conn.furhat_listen()
                dialog_length += 1
                emotion = self.detect_emotion()
                general_talk_prompt = fill_template(["DIALOGUE", "EMOTION"], [user_dialogue, emotion], prompt_list["GENERAL_TALK"])
                print(general_talk_prompt)
                bot_dialogue = self.prompter.prompt_generator(general_talk_prompt)
                self.furhat_conn.furhat_speak(bot_dialogue)
                if not dialog_length % 3:
                    bot_dialogue = read_json("GENERAL_TO_QUIZ_DIALOGUE")
                    self.furhat_conn.furhat_speak(bot_dialogue)
                    user_dialogue = self.furhat_conn.furhat_listen()
                    to_study = self.prompter.prompt_generator_dialogue(user_dialogue, "SWITCH_TO_STUDY")
                    if to_study == 'yes':
                        return True
                    else:
                        bot_dialogue = read_json("TO_STOP")
                        self.furhat_conn.furhat_speak(bot_dialogue)
                        user_dialogue = self.furhat_conn.furhat_listen()
                        to_end = self.prompter.prompt_generator_dialogue(user_dialogue, "END_SESSION")
                        if to_end == 'yes':
                            return False

        except Exception as e:
            raise Exception(e)

    def session_end(self, correct_questions,incorrect_questions):
        performance = str(correct_questions-incorrect_questions)
        performance_specific = read_json("PERFORMANCE_SPECIFIC_DIALOGUE")[performance]
        bot_dialogue = fill_template(["CORRECT", "INCORRECT", "PERFORMANCE_SPECIFIC"], [str(correct_questions), str(incorrect_questions), performance_specific], read_json("SESSION_END_DIALOGUE"))
        self.furhat_conn.furhat_speak(bot_dialogue)
    
    def talk(self):
        try:
            session_start()
            to_study = self.introduce()
            if not to_study:
                to_study = self.general_talk()
            if to_study:
                topic = self.choose_topic()
                correct, wrong = self.quiz(topic)
                self.session_end(correct, wrong)
                return
            self.furhat_conn.furhat_end_session()

        except Exception as e:
            print(e)
            raise(e)
        finally:
            # self.sql_conn.exit_user(self.user_id)
            self.sql_conn.close_connection()

            
if __name__ == "__main__":
    Biblo().talk()


