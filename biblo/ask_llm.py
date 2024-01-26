import requests
import json

BASE_URL = "http://127.0.0.1:3000/api/v1"

# Function to make API calls
def make_api_call(route, method, data):
    url = f"{BASE_URL}/{route}"

    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
    else:
        raise ValueError("Invalid HTTP method")
    return response.json()

def ask_llm(user_dialogue):
    payload = {"user": user_dialogue}
    res = make_api_call("ask_llm_wo_mem", "POST", payload)
    print(res["data"])
    return res["data"]

# make wrapper to take in the user_dialogue


if __name__ == "__main__":
    ask_llm("Answer yes/no whether the following statement is affirmative? Yes")
    ask_llm("Answer yes/no whether the following statement is affirmative? No")
    ask_llm("Answer yes/no whether the following statement is affirmative? I don't want to")
    ask_llm("Answer yes/no whether the following statement is affirmative? Let's go")
    ask_llm("Answer yes/no whether the following statement is affirmative? Sure thing")
    ask_llm("Do I want to stop if they say the following, answer yes/no: I'm done")
    ask_llm("Do I want to stop if they say the following, answer yes/no: I don't want to answer quesions")
    ask_llm("Do I want to stop if they say the following, answer yes/no: Yes let's go")
