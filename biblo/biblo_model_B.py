from furhat_connection_memory import FurhatConnection
from generate_prompt import PromptGenerator
from query_llm import AskLLM
from db_conn import DBConn
from read_json_config import read_json, fill_template
from ui import render_ui, show_evaluation, session_start
from generate_qb_memory import generate_qb_topic, make_api_call
import random
import math
import uuid


class Biblo:
    def __init__(self) -> None:
        self.llm = AskLLM()
        self.furhat_conn = FurhatConnection(self.llm)
        self.prompter = PromptGenerator(self.llm)
        self.sql_conn = DBConn()
        self.user_id = 0
        self.user_name = ""
        self.qb_ltm = []

    def introduce(self):
        try:
            context = "general"
            user, new_user = self.sql_conn.fetch_current_user()
            self.user_id = user[0]
            if new_user:
                intro_template = read_json("INTRODUCTION_NEW_USER")
                self.furhat_conn.furhat_speak(intro_template["1"], context=context)
                self.furhat_conn.furhat_speak(intro_template["2"], context=context)
                user_dialogue = self.furhat_conn.furhat_listen(context = context, current_user_context = context, user_id = self.user_id)
                user_name = self.prompter.prompt_generator_dialogue(user_dialogue, "NAME", "FLAN")
                self.sql_conn.update_name(self.user_id, user_name)
                self.user_name = user_name
                bot_dialogue = fill_template(["NAME"], [user_name], intro_template["3"])

            else:
                intro_template = read_json("INTRODUCTION_RETURNING_USER")
                self.furhat_conn.furhat_speak(intro_template["1"], context=context)
                self.user_name = user[1]  # get name from response
                bot_dialogue = fill_template(["NAME"], [self.user_name], intro_template["2"])

            self.furhat_conn.furhat_speak(bot_dialogue, context=context)
            user_dialogue = self.furhat_conn.furhat_listen(context = context, current_user_context = context, user_id = self.user_id)
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
                topic_chosen = "profit_and_loss"
            if topic_chosen not in read_json("LIST_OF_TOPICS_RAG"):
                self.furhat_conn.furhat_speak(topic_templates["2"])
                user_dialogue = self.furhat_conn.furhat_listen()
                topic_flag = self.prompter.prompt_generator_dialogue(user_dialogue, "YES_NO")
                if topic_flag == 'yes':
                    topic_chosen = "bodmas"
                else:
                    topic_chosen = self.prompter.prompt_generator_dialogue(user_dialogue, "TOPIC", "FLAN")
                    if "profit" in topic_chosen:
                        topic_chosen = "profit_and_loss"
                    if topic_chosen not in read_json("LIST_OF_TOPICS_RAG"):
                        topic_chosen = "bodmas"

            topic_chosen = topic_chosen.lower()
            if topic_chosen == "profit_and_loss":
                bot_dialogue = fill_template(["TOPIC"], ["profit and loss"], topic_templates["3"])
                self.furhat_conn.furhat_speak(bot_dialogue)
            else:
                bot_dialogue = fill_template(["TOPIC"], [topic_chosen], topic_templates["3"])
                self.furhat_conn.furhat_speak(bot_dialogue)
            return topic_chosen

        except Exception as e:
            raise Exception(e)

    def quiz(self, topic_chosen):
        to_study = True
        questions_asked = 0
        correct_questions, incorrect_questions = 0, 0
        total_questions = read_json("TOTAL_QUESTIONS")
        emotion_prompts = read_json("PROMPTS")
        quiz_dialogue = read_json("QUIZ_DIALOGUE")
        try:
            qb, full_qb, prev_correct, prev_incorrect = generate_qb_topic(self.user_id, topic_chosen)
            self.qb_ltm = full_qb.copy()
            if correct_questions > 0 or incorrect_questions > 0:
                recap_dialogue = fill_template(["CORRECT", "INCORRECT"],
                                         [str(prev_correct), str(prev_incorrect)],
                                         read_json("RECAP_PREV_SESSION"))
                self.furhat_conn.furhat_speak(recap_dialogue)

            started = False
            for question in qb:
                if started:
                    self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["NEXT_QUESTION"]))
                started = True

                if "is_correct" in question and not question["is_correct"]:
                    self.furhat_conn.furhat_speak("You had got this question wrong the last time, let's try to nail it now!")

                self.furhat_conn.furhat_speak(question["question"], block_flag=False)
                self.furhat_conn.furhat_speak("The options are: ")
                for option in question["options"]:
                    self.furhat_conn.furhat_speak(option, block_flag=False)

                question["choice"] = render_ui(question, self.furhat_conn)

                if question["choice"] == question["correct"]:
                    is_correct = True
                    correct_questions += 1

                    self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["CORRECT_ANSWER"]))
                    if correct_questions >= math.ceil(total_questions / 2):
                        self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["MANY_CORRECT_ANSWERS"]))

                else:
                    is_correct = False
                    incorrect_questions += 1
                    # render on UI, incorrect answer
                    self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["INCORRECT_ANSWER"]))
                    self.furhat_conn.furhat_speak(f"The correct answer is {question['correct']}, you answered {question['choice']}")
                    if incorrect_questions >= math.floor(total_questions / 2):
                        self.furhat_conn.furhat_speak(random.choice(quiz_dialogue["MANY_INCORRECT_ANSWERS"]))

                show_evaluation(is_correct, question)
                question["is_correct"] = is_correct
                questions_asked += 1

                emotion = self.detect_emotion()

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

                self.quiz_to_stm(question)

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

    def quiz_to_stm(self, question):
        route = "user_convo"
        stm_payload = dict()
        stm_payload["context"] = "quiz"
        stm_payload["current_user_context"] = "quiz"
        stm_payload["user_id"] = self.user_id
        is_correct = "correct" if question["is_correct"] else "incorrect"
        stm_payload["BOT"] = question["question"]
        stm_payload["USER"] = f"User gave the {is_correct} answer choosing option {question['choice']}"
        question_keys = ["correct", "explanation", "hint", "question", "question_id", "topic", "topic_id", "is_correct"]
        for key in question_keys:
            stm_payload[key] = question[key]
        stm_payload["options"] = str(question["options"])
        stm_payload["user_response"] = question["choice"]
        stm_payload["user_reasoning"] = ""
        print("STM payload for quiz: ", stm_payload)
        make_api_call(route, "POST", stm_payload)
        for item in self.qb_ltm:
            if item["question_id"] == stm_payload["question_id"]:
                self.qb_ltm.remove(item)
        del stm_payload["BOT"]
        del stm_payload["USER"]
        del stm_payload["current_user_context"]
        self.qb_ltm.append(stm_payload)


    def detect_emotion(self):
        emotion = self.sql_conn.fetch_emotion(self.user_id)
        if emotion in ["", "Fearful", "Disgusted"] or emotion is None:
            emotion = "Neutral"
        elif emotion in ["Angry", "Sad"]:
            emotion = "Sad"
        elif emotion in ["Happy", "Surprised"]:
            emotion = "Happy"
        return emotion

    def session_end(self, correct_questions, incorrect_questions):
        performance = str(correct_questions - incorrect_questions)
        performance_specific = read_json("PERFORMANCE_SPECIFIC_DIALOGUE")[performance]
        bot_dialogue = fill_template(["CORRECT", "INCORRECT", "PERFORMANCE_SPECIFIC"],
                                     [str(correct_questions), str(incorrect_questions), performance_specific],
                                     read_json("SESSION_END_DIALOGUE"))
        self.furhat_conn.furhat_speak(bot_dialogue)
        return

    def general_talk(self):
        try:
            context = "general" #because talk function call saves it automatically
            route = "lets_talk"
            user_id = self.user_id
            bot_dialogue = random.choice(read_json("GENERAL_TALK"))
            self.furhat_conn.furhat_speak(bot_dialogue, context=context)
            dialog_length = 0
            general_talk_prev = {}
            while True:
                user_dialogue = self.furhat_conn.furhat_listen(context=context, current_user_context=context, user_id=user_id)
                dialog_length += 1
                emotion = self.detect_emotion()

                general_talk_payload_list = []
                if "current" in general_talk_prev:
                    general_talk_prev["current"] = 0
                    general_talk_payload_list.append(general_talk_prev)
                general_talk_payload = {}
                general_talk_payload["BOT"] = bot_dialogue
                general_talk_payload["USER"] = user_dialogue + ". I feel " + emotion + "."
                general_talk_payload["context"] = context
                general_talk_payload["current_user_context"] = context
                general_talk_payload["user_id"] = user_id
                general_talk_payload["current"] = 1
                general_talk_payload_list.append(general_talk_payload)
                response = make_api_call(route, "POST", general_talk_payload_list)
                print(general_talk_payload_list)
                general_talk_prev = general_talk_payload


                bot_dialogue = response["generated_dialog"]
                self.furhat_conn.furhat_speak(bot_dialogue, context=context)
                if not dialog_length % 3:
                    bot_dialogue = read_json("GENERAL_TO_QUIZ_DIALOGUE")
                    self.furhat_conn.furhat_speak(bot_dialogue)
                    user_dialogue = self.furhat_conn.furhat_listen(context = context, current_user_context = context, user_id = user_id)
                    to_study = self.prompter.prompt_generator_dialogue(user_dialogue, "SWITCH_TO_STUDY")
                    if to_study == 'yes':
                        return True
                    else:
                        bot_dialogue = read_json("TO_STOP")
                        self.furhat_conn.furhat_speak(bot_dialogue, context=context)
                        user_dialogue = self.furhat_conn.furhat_listen(context = context, current_user_context = context, user_id = user_id)
                        to_end = self.prompter.prompt_generator_dialogue(user_dialogue, "END_SESSION")
                        if to_end == 'yes':
                            return False

        except Exception as e:
            raise Exception(e)

    def short_term_to_long_term(self):
        route = "move_stm_to_ltm"
        make_api_call(route, "GET")
        print("Moved STM to LTM")

        for item in self.qb_ltm:
            item["options"] = str(item["options"])

        route = "save-user-quiz-res-to-ltm"
        quiz_to_ltm_payload = {
            "test_session_id": str(uuid.uuid1()),
            "payload": self.qb_ltm
        }
        print("Quiz to LTM payload\n", quiz_to_ltm_payload)
        make_api_call(route, "POST", quiz_to_ltm_payload)
        print("Saved questions to LTM")

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
                print("Moving to memory")
                self.short_term_to_long_term()
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


