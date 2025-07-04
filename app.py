from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS                   
from config.setting import load_env

load_env()
from routes import register_routes
import os

app = Flask(__name__)
app.secret_key = 'super-secret'

# CORS + SocketIO
socketio = SocketIO(app, cors_allowed_origins=os.environ.get("FRONTEND_URL"))  
CORS(app, supports_credentials=True, origins=[os.environ.get("FRONTEND_URL")])

register_routes(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT") or 5000) 
    socketio.run(app, host="0.0.0.0", port=port, debug=True)


