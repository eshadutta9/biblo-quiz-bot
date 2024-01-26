from flask import request, Response, json, Blueprint
from ..services.short_term_memory_service import (save_to_short_term_memory, get_recent_conversation_history,
                                                  ShortTermMemoryError, get_data_for_stm_to_ltm, clear_stm)
from ..services.long_term_memory_service import (fetch_from_domain_knowledge, KnowledgeFetchError, UserLTMSaveError, TopicNotInRAG , create_or_update_user, stm_to_ltm_migration, save_user_quiz_responses_to_ltm)

from ..services.predict_context import (predict_context, InferenceError, ask_llm_advanced_without_memory)

from ..services.dialog_manager import lets_talk, DialogManagerError, update_rag_with_user_response

resources = Blueprint("cabot", __name__)


@resources.route('/user_convo', methods=["POST"])
def save_to_short_term_memory_controller():
    try:
        # Assuming raw_conversation_log is obtained from the POST request
        raw_conversation_log = request.json
        # Call the function to save to short-term memory
        save_to_short_term_memory(raw_conversation_log)

        # Return success response
        return Response(
            response=json.dumps({'status': "success"}),
            status=200,
            mimetype='application/json'
        )
    except ShortTermMemoryError as e:
        # Handle the custom exception and return an error response
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/get_recent_conversations', methods=["POST"])
def get_recent_conversation_controller():
    try:
        raw_conversation = request.json
        result = get_recent_conversation_history(raw_conversation)
        if result is not None:
            return Response(
                response=json.dumps({'data': result, 'status': "success"}),
                status=200,
                mimetype='application/json'
            )
    except ShortTermMemoryError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/get_domain_knowledge', methods=["POST"])
def fetch_from_domain_knowledge_controller():
    try:
        raw_conversation = request.json
        result = fetch_from_domain_knowledge(raw_conversation['user'], raw_conversation['user_id'])
        if result is not None:
            return Response(
                response=json.dumps({'data': result, 'status': "success"}),
                status=200,
                mimetype='application/json'
            )
    except TopicNotInRAG as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "Search Fail", 'message': "Oops Topic not found"}),
            status=200,  # Internal Server Error
            mimetype='application/json'
        )
    except KnowledgeFetchError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/predict_context', methods=["POST"])
def predict_context_controller():
    try:
        raw_conversation = request.json
        result = predict_context(raw_conversation['user'])
        if result is not None:
            return Response(
                response=json.dumps({'data': result, 'status': "success"}),
                status=200,
                mimetype='application/json'
            )
    except InferenceError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/lets_talk', methods=["POST"])
def lets_talk_controller():
    try:
        raw_conversation = request.json
        result = lets_talk(raw_conversation)
        if result is not None:
            return Response(
                response=json.dumps({'data': result, 'status': "success"}),
                status=200,
                mimetype='application/json'
            )
    except InferenceError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/update_rag_user_input', methods=["POST"])
def update_rag_user_input_controller():
    try:
        response = request.json
        update_rag_with_user_response(response)
        return Response(
            response=json.dumps({'status': "success"}),
            status=200,
            mimetype='application/json'
        )
    except DialogManagerError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/create_update_user', methods=["POST"])
def create_or_update_user_controller():
    try:
        payload = request.json
        create_or_update_user(payload)
        return Response(
            response=json.dumps({'status': "user ltm save success"}),
            status=200,
            mimetype='application/json'
        )
    except DialogManagerError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/get_all_stm_data', methods=["GET"])
def get_all_stm_controller():
    try:
        response = get_data_for_stm_to_ltm()
        return Response(
            response=json.dumps({'data':  response,'status': "user ltm save success"}),
            status=200,
            mimetype='application/json'
        )
    except DialogManagerError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/move_stm_to_ltm', methods=["GET"])
def stm_to_ltm_controller():
    try:
        stm_to_ltm_migration()
        return Response(
            response=json.dumps({'status': "user ltm save success"}),
            status=200,
            mimetype='application/json'
        )
    except DialogManagerError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/save-user-quiz-res-to-ltm', methods=["POST"])
def save_user_quiz_responses_to_ltm_controller():
    try:
        payload = request.json
        save_user_quiz_responses_to_ltm(payload)
        return Response(
            response=json.dumps({'status': "user ltm save success"}),
            status=200,
            mimetype='application/json'
        )
    except UserLTMSaveError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/clear_stm', methods=["GET"])
def clear_stm_controller():
    try:
        clear_stm()
        return Response(
            response=json.dumps({'status': "STM cleared"}),
            status=200,
            mimetype='application/json'
        )
    except UserLTMSaveError as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )


@resources.route('/ask_llm_wo_mem', methods=['POST'])
def ask_llm_wo_meme():
    try:
        raw_conversation = request.json
        response = ask_llm_advanced_without_memory(raw_conversation['user'])
        return Response(
            response=json.dumps({'data':  response,'status': "LM response"}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_message = str(e)
        return Response(
            response=json.dumps({'status': "error", 'message': error_message}),
            status=500,  # Internal Server Error
            mimetype='application/json'
        )

