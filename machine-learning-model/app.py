from src import config, app
from flask import request
# from gevent.pywsgi import WSGIServer
from src.services.predict_context import predict_context

# @app.before_request
# def check_user_context():
#     request_body = request.json
#     if 'user' in request_body:
#         predict_context(request_body['user'])
#     elif 'USER' in request_body:
#         predict_context(request_body['USER'])



if __name__ == "__main__":
    app.run(host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG)
    # http_server = WSGIServer((config.HOST, config.PORT), app)
    # http_server.spawn = 4
    # http_server.serve_forever()