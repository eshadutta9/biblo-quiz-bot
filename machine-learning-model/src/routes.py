from flask import Blueprint
from .controllers.main_controller import resources

from .services.short_term_memory_service import save_to_short_term_memory

api = Blueprint('api', __name__)

api.register_blueprint(resources, url_prefix="/v1")