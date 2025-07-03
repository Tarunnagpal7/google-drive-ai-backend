from .auth_routes import auth_bp
from .google_drive import drive_bp
from .ai_organizer import ai_bp
def register_routes(app):
    app.register_blueprint(ai_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(drive_bp)
