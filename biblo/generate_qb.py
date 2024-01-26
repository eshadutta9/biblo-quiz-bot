import json
import ast
import random
from read_json_config import read_json


def generate_qb_topic(topic="BODMAS"):
    question_bank = open("sample_questions.json").read()
    question_bank = json.loads(question_bank)
    topical_qb = []

    no_of_questions = read_json("TOTAL_QUESTIONS")
    for question in question_bank:
        if question["topic"].lower() == topic.lower():
            question["options"] = ast.literal_eval(question["options"])
            topical_qb.append(question)

    ask_questions = random.sample(topical_qb, no_of_questions)

    return ask_questions


if __name__ == "__main__":
    qs = generate_qb_topic("algebra")
    print(qs)
