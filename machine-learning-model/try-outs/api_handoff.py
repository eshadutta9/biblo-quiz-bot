import requests
import json

BASE_URL = "http://127.0.0.1:3000/api/v1/"



# Function to make API calls
def make_api_call(route, method, data=None):
    url = f"{BASE_URL}/{route}"

    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
    else:
        raise ValueError("Invalid HTTP method")

    return response.json()

# Example API calls
if __name__ == "__main__":
    # Example: Save to short-term memory
    save_to_stm_data = {"user": "example_user", "conversation": ["message1", "message2"]}
    save_to_stm_response = make_api_call("user_convo", "POST", data=save_to_stm_data)
    print(save_to_stm_response)

    # Example: Get recent conversations
    get_recent_data = {"user": "example_user"}
    get_recent_response = make_api_call("get_recent_conversations", "POST", data=get_recent_data)
    print(get_recent_response)

    # Example: Fetch from domain knowledge
    fetch_domain_data = {"user": "example_user"}
    fetch_domain_response = make_api_call("get_domain_knowledge", "POST", data=fetch_domain_data)
    print(fetch_domain_response)

    # Example: Predict context
    predict_context_data = {"user": "example_user"}
    predict_context_response = make_api_call("predict_context", "POST", data=predict_context_data)
    print(predict_context_response)

    # Example: Let's talk
    lets_talk_data = {"user": "example_user", "conversation": ["message1", "message2"]}
    lets_talk_response = make_api_call("lets_talk", "POST", data=lets_talk_data)
    print(lets_talk_response)

    # Example: Update RAG with user input
    update_rag_data = {"user": "example_user", "response": "user_response"}
    update_rag_response = make_api_call("update_rag_user_input", "POST", data=update_rag_data)
    print(update_rag_response)

    # Continue with similar calls for other routes...
