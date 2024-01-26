import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
import pinecone
import time
import uuid
from datetime import datetime
load_dotenv()

class ShortTermMemoryError(Exception):
    pass


def save_to_short_term_memory(raw_conversation_log):
    try:
        index_name = 'bot-short-term-memory'
        pinecone.init(
            api_key=os.environ.get('pinecone_short_term_mem'),
            environment="gcp-starter",
        )

        # Create or fetch Index
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                index_name,
                dimension=384,  # Remember to change this dimension based on encoder
                metric='cosine'
            )

            # Wait for index to finish initialization
            while not pinecone.describe_index(index_name).status['ready']:
                time.sleep(1)

        index = pinecone.Index(index_name)

        # Fetch Model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        user_embed = context_encoding(raw_conversation_log)
        unique_id = str(uuid.uuid4())
        current_timestamp = int(time.mktime(datetime.now().timetuple()))
        metadata = {"BOT":  raw_conversation_log.get('BOT'), "USER": raw_conversation_log.get('USER'), "timestamp": current_timestamp, "context": raw_conversation_log['current_user_context']}
        index.upsert([(unique_id, user_embed, metadata)])

    except Exception as e:
        # Catch any exception that occurs during execution
        error_message = f"An error occurred: {str(e)}"
        raise ShortTermMemoryError(error_message)


def get_recent_conversation_history(raw_convo, number_of_convo=6):
    try:
        some_related_convo = None
        index_name = 'bot-short-term-memory'
        encoded_query = context_encoding(raw_convo)
        pinecone.init(
            api_key=os.environ.get('pinecone_short_term_mem'),
            environment="gcp-starter",
        )
        index = pinecone.Index(index_name)
        response = index.query(
            vector=encoded_query,
            filter = {
                "context": {"$eq": raw_convo['context']}
            },
            top_k=number_of_convo,
            include_metadata=True
        )
        print("Recent Convo: ", response)
        return response.to_dict()['matches']

    except Exception as e:
        print(e)
        error_message = f"An error occurred while fetching recent convo 001x: {str(e)}"
        raise ShortTermMemoryError(error_message)


def update_stm_metadata(update_id, values, meta_data):
    index_name = 'bot-short-term-memory'
    pinecone.init(
        api_key=os.environ.get('pinecone_short_term_mem'),
        environment="gcp-starter",
    )
    index = pinecone.Index(index_name)
    print(update_id, values, meta_data)
    index.upsert([(update_id, values, meta_data)])


def context_encoding(raw_conversation_log):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    bot_message = raw_conversation_log.get('BOT')
    user_message = raw_conversation_log.get('USER')
    return model.encode("When you said " + bot_message + "the user replied " + user_message).tolist()


def get_data_for_stm_to_ltm():
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        encoded = model.encode("BIT, USER, QUIZ, PHYSICS, GENERAL").tolist()
        index_name = 'bot-short-term-memory'
        pinecone.init(
            api_key=os.environ.get('pinecone_short_term_mem'),
            environment="gcp-starter",
        )
        index = pinecone.Index(index_name)
        response = index.query(
            vector=encoded,
            top_k=1000,
            include_values=False,
            include_metadata = True
        )
        return response.to_dict()

    except Exception as e:
        print(e)
        error_message = f"An error occurred while fetching recent convo 001x: {str(e)}"
        raise ShortTermMemoryError(error_message)


def clear_stm():
    index_name = 'bot-short-term-memory'
    pinecone.init(
        api_key=os.environ.get('pinecone_short_term_mem'),
        environment="gcp-starter",
    )
    index = pinecone.Index(index_name)
    index.delete(delete_all=True)

