# TODO: Create or update Domain Knowledge - NOT Needed, run from separate Script
from sentence_transformers import SentenceTransformer, util
from ..services.short_term_memory_service import get_data_for_stm_to_ltm, clear_stm
from ..services.predict_context import which_test_set_user_wants, ALGEBRA, GEOMETRY, PERCENTAGES, BODMAS, PROFITLOSS
import pinecone
import time
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class KnowledgeFetchError(Exception):
    pass


class UserLTMSaveError(Exception):
    pass


class TopicNotInRAG(Exception):
    pass


def fetch_from_domain_knowledge(query, user_id):
    user_wants = which_test_set_user_wants(query)
    print(user_wants)
    print(query)
    if user_wants in [ALGEBRA, GEOMETRY, BODMAS, PROFITLOSS, PERCENTAGES]:
        result = fetch_quiz_data_from_ltm(query, user_wants, user_id)
        print(result)
        if len(result) > 0:
            print("here 1")
            return result
        else:
            result_2 = fetch_quiz_data_from_knowledge_base(query, user_wants)
            return result_2
    else:
        raise TopicNotInRAG()


def fetch_quiz_data_from_ltm(query, user_test_topic, user_id):
    index_name = 'long-term-memory'
    model = SentenceTransformer('all-MiniLM-L6-v2')
    pinecone.init(
        api_key=os.environ.get('pinecone_ltm'),
        environment="gcp-starter",
    )
    print(user_id, user_test_topic, query)
    index = pinecone.Index(index_name)
    query = "User " + str(user_id)
    response = index.query(model.encode(query).tolist(),
                           filter={
                               "topic": {"$eq": user_test_topic},
                               "user_id": int(user_id),
                           },
                           top_k=10,
                           include_metadata=True
                           )
    return format_output(response.to_dict()['matches'])


def fetch_quiz_data_from_knowledge_base(query, topic):
    try:
        pinecone.init(
            api_key=os.environ.get('pinecone_long_term_mem'),
            environment="gcp-starter",
        )
        index_name = 'ca-v1-rag'
        index = pinecone.Index(index_name)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        encoded_query = model.encode(query).tolist()
        res = index.query(
            vector=encoded_query,
            top_k=15,
            include_metadata=True,
            include_values=True,
            filter={
                "topic": {"$eq": topic},
            },
        )
        formatted_questionnaire = format_output(res.to_dict()['matches'])
        return formatted_questionnaire
    except Exception as e:
        # You can log the error or handle it based on your requirements
        print(f"An error occurred: {str(e)}")
        raise KnowledgeFetchError("Error fetching knowledge from domain knowledge.")


def format_output(matches):
    formatted_data = []
    print(matches)
    for data in matches:
        formatted_data.append(data['metadata'])

    return formatted_data

# TODO: Store User Meta in Long Term
def create_or_update_user(payload):
    index_name = 'long-term-memory'
    try:
        pinecone.init(
            api_key=os.environ.get('pinecone_ltm'),
            environment="gcp-starter",
        )
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                index_name,
                dimension=384,
                metric='cosine'
            )
            # wait for index to finish initialization
            while not pinecone.describe_index(index_name).status['ready']:
                time.sleep(1)

        index = pinecone.Index(index_name)

        current_timestamp = int(time.mktime(datetime.now().timetuple()))
        model = SentenceTransformer('all-MiniLM-L6-v2')
        quiz_session_summary = (f"User {payload['user_name']} ({payload['user_id']}) interacted with the system "
                                f"in the '{payload['context']}' context. Duri"
                                f"ng the last test session on {payload['last_test_session_set']}, "
                                f"the user achieved category-wise scores of Physics: "
                                f"{payload['category_wise_score_category_1']}, Geometry: "
                                f"{payload['category_wise_score_category_2']}, and General: "
                                f"{payload['category_wise_score_category_3']}. The user's last reported state of "
                                f"mind was '{payload['last_state_of_mind']}'.")
        final_vector = model.encode(quiz_session_summary)
        metadata = payload
        metadata['last_session_summary'] = quiz_session_summary
        index.upsert([(payload["user_id"], final_vector.tolist(), metadata)])

    except Exception as e:
        # You can log the error or handle it based on your requirements
        print(f"An error occurred: {str(e)}")
        raise UserLTMSaveError("Error fetching knowledge from long term memory.")


def stm_to_ltm_migration():
    index_name = 'long-term-memory'
    model = SentenceTransformer('all-MiniLM-L6-v2')
    pinecone.init(
        api_key=os.environ.get('pinecone_ltm'),
        environment="gcp-starter",
    )
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            index_name,
            dimension=384,
            metric='cosine'
        )
    # wait for index to finish initialization
    while not pinecone.describe_index(index_name).status['ready']:
        time.sleep(1)
    index = pinecone.Index(index_name)
    try:
        # Fetch from STM
        data_list = get_data_for_stm_to_ltm()['matches']
        # TODO: empty STM
        upsert_data = []
        for item in data_list:
            upsert_data.append(
                (str(uuid.uuid4()), model.encode("micheal scott related data").tolist(), item['metadata']))
            print(upsert_data)
        index.upsert(upsert_data)
        clear_stm()
    except Exception as e:
        raise UserLTMSaveError("Error saving knowledge to long term memory.")


def save_user_quiz_responses_to_ltm(payload):
    index_name = 'long-term-memory'
    model = SentenceTransformer('all-MiniLM-L6-v2')
    pinecone.init(
        api_key=os.environ.get('pinecone_ltm'),
        environment="gcp-starter",
    )
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            index_name,
            dimension=384,
            metric='cosine'
        )
    # wait for index to finish initialization
    while not pinecone.describe_index(index_name).status['ready']:
        time.sleep(1)
    index = pinecone.Index(index_name)
    today_date = datetime.now().date()
    try:
        upsert_data = []
        for item in payload['payload']:
            quiz_search_prompt = f'''User ${item['user_id']} gave this test on ${today_date}'''
            item['test_session_id'] = payload['test_session_id']
            item['test_date'] = today_date
            upsert_data.append(
                (str(uuid.uuid4()), model.encode(quiz_search_prompt).tolist(), item))
        index.upsert(upsert_data)
    except Exception as e:
        print(e)
        raise UserLTMSaveError("Error saving knowledge to long term memory.")
