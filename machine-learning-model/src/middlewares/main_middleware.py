# Define your middleware class
from ..services.predict_context import predict_context
from werkzeug.wrappers import Request
import json
# class MainMiddleware:
#     def __init__(self, app):
#         self.app = app
#
#     def __call__(self, environ, start_response):
#         req = Request(environ, shallow=True)
#         print(req)
#         request_body_text = req.get_data(as_text=True)
#         request_body_json = json.loads(request_body_text)
#         return self.app(environ, start_response)
