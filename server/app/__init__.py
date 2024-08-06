from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
from .service.LLM.ollama_service import Ollama

socketio = SocketIO()

def create_app():
    app = Flask(__name__, template_folder='../templates')  # 指定模板目录
    app.config.from_object(Config)

    CORS(app)  # 允许跨域请求

    # 创建 Ollama 对象
    app.ollama = Ollama(
        host=app.config['OLLAMA_HOST'],
        port=app.config['OLLAMA_PORT'],
        model=app.config['OLLAMA_MODEL']
    )

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .events import register_socketio_events
    register_socketio_events(socketio, app)

    socketio.init_app(app, cors_allowed_origins="*")  # 允许跨域 WebSocket 请求

    return app
