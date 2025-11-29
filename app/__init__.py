from flask import Flask
from app.routes.api import api_bp
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.posts import posts_bp
from app.routes.log import workout_logs_bp
from app.routes.workout_plans import workout_plans_bp
from app.routes.admin import admin_bp  # NEW
import logging
from flask_cors import CORS
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(config_object='app.config.DevelopmentConfig'):
    app = Flask(__name__)
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        logger.info("CREATING APP...")
        app.config.from_object(config_object)

        CORS(
            app,
            resources={r"/*": {"origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5174",
                "https://buffbuds.netlify.app"
            ]}},
            supports_credentials=True,
        )

        app.config["SESSION_TYPE"] = "filesystem"
        app.config["SESSION_PERMANENT"] = True
        app.config["SESSION_USE_SIGNER"] = True
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        Session(app)
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

        # registering Blueprints
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(user_bp, url_prefix='/user')
        app.register_blueprint(posts_bp, url_prefix='/posts')
        app.register_blueprint(workout_logs_bp, url_prefix='/sessions')
        app.register_blueprint(workout_plans_bp, url_prefix='/plans')
        app.register_blueprint(admin_bp, url_prefix='/admin')  # NEW

        logger.info('APP CREATED!')

    except Exception as e:
        logger.error(f"Error creating app: {e}")

    return app