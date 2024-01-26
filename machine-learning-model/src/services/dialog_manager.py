from ..services.long_term_memory_service import fetch_from_domain_knowledge, TopicNotInRAG
from ..services.predict_context import predict_context, ask_llm, stm_llm_talk
from ..services.short_term_memory_service import (save_to_short_term_memory, get_recent_conversation_history,
                                                  update_stm_metadata)


class DialogManagerError(Exception):
    pass


def lets_talk(two_conversation):
    print("$%$%$%$%$%$%$%$%%$%$%%$%$%%$%$")
    print(two_conversation)

    raw_conversation = [item for item in two_conversation if item.get("current") == 1][0]
    prev_conversation = None
    if (len(two_conversation) > 1):
        prev_conversation = [item for item in two_conversation if item.get("current") == 0][0]
    print("&$&#$&#&$#&$#&$#&$*&#$#$")
    # Predict Context
    user_intent = predict_context(raw_conversation['USER'])
    # if Study, fetch RAG
    domain_knowledge = None
    try:
        if user_intent['rag_fetch'] == 'yes':
            domain_knowledge = fetch_from_domain_knowledge(raw_conversation['USER'], raw_conversation['user_id'])
    except TopicNotInRAG:
        domain_knowledge = None
    # TODO: Get recent Conversations based on just
    recent_convos = get_recent_conversation_history(raw_conversation)
    if(prev_conversation is not None):
        psuedo_augment_no_db = {
                'metadata': raw_conversation
            }
        recent_convos.append(
            psuedo_augment_no_db
        )
    print("#############$$$$$$##")
    print(recent_convos)
    print("$####################")
    # Else Get last few convos and Reply to most resent user conversation
    generated_dialog = generate_dialog(raw_conversation, user_intent, domain_knowledge, recent_convos)
    # Store to Short Term Memory
    save_to_short_term_memory(raw_conversation)
    return generated_dialog


def generate_dialog(user_conversation, user_intent, domain_knowledge, recent_convos):
    knowledge = prompt_ready_recent_conversation(recent_convos)
    #augmented_prompt = ".Use the above information to respond to the message: "
    #prompt = "Below are some of the most relevant interactions from this chat: " + knowledge + " " + augmented_prompt + " " + user_conversation['USER']
    generated_dialog = stm_llm_talk(knowledge)
    return {
        "generated_dialog": generated_dialog,
        "domain_knowledge": domain_knowledge,
        "user_intent": user_intent
    }


def prompt_ready_recent_conversation(recent_convos):
    # Combine BOT and USER messages from recent conversations
    conversation_strings = []
    messages = [
        {
            "role": "system",
            "content": "You are a Quizzing bot that quizzes students and also cares about their emotional state. You do not have a questions and will be provided externally. Respond in less than 10 words. Do not ask questions"
        },
    ]

    for convo in recent_convos:
        bot_message = convo["metadata"]["BOT"]
        user_message = convo["metadata"]["USER"]
        bot_chat = {
            "role": "system",
            "content": bot_message
        }
        user_chat = {
            "role": "user",
            "content": user_message
        }
        # conversation_strings.append(f"BOT: {bot_message} USER: {user_message}")
        messages.append(bot_chat)
        messages.append(user_chat)

    # Combine all conversation strings into a single prompt
    # full_prompt = "\n".join(conversation_strings)

    return messages


def update_rag_with_user_response(quiz_payload):
    try:
        # Get Short term memory index
        # do something like index.update(id="id-3", set_metadata={"type": "web", "new": True})
        # FIXME: LTM new pinecone db.
        """
        :param quiz_payload:
        :return:
        """
        update_id = quiz_payload['rag_data']['id']
        values = quiz_payload['rag_data']['values']
        user_response = quiz_payload['user_response']
        metadata = quiz_payload['rag_data']['metadata']
        metadata['user_answer'] = user_response['answer']
        metadata['is_correct'] = user_response['is_correct']
        metadata['user_reasoning'] = user_response['reason']
        metadata['context'] = 'quiz'
        set_metadata = metadata
        update_stm_metadata(update_id, values, set_metadata)
    except Exception as e:
        error_message = f"An error with dialog manager: {str(e)}"
        raise DialogManagerError(error_message)
