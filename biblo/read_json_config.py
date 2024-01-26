import json 

def read_json(key):
    with open("config.json") as jsonfile:
        config = json.load(jsonfile)

    return config[key]


def fill_template(keys, values, template):
    filled_string = template
    for key, value in list(zip(keys, values)):
        key = "{{" + key + "}}"
        filled_string = filled_string.replace(key, value)
    return filled_string


if __name__ == "__main__":
    correct_questions, incorrect_questions = 1,4
    if correct_questions >= incorrect_questions:
        performance = str(correct_questions-incorrect_questions)
    else:
        performance = "1"
    performance_specific = read_json("PERFORMANCE_SPECIFIC_DIALOGUE")[performance]
    bot_dialogue = fill_template(["CORRECT","INCORRECT","PERFORMANCE_SPECIFIC"], [str(correct_questions),str(incorrect_questions),performance_specific], read_json("SESSION_END_DIALOGUE"))
    print(bot_dialogue)