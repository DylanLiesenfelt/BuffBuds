from flask import Flask
from .routes.api import api_bp
from .routes.auth import auth_bp
from .routes.user import user_bp
import logging
from flask_cors import CORS

# intializing in default config mode for testing purposes, can be changed to ProductionConfig later
def create_app(config_object='app.config.DevelopmentConfig'):
    app = Flask(__name__)
    
    # logging instead of print, allows for debug messages to be entered and displayed only when needed
    logging.basicConfig(level=logging.INFO) # change INFO to DEBUG for debugging
    logger = logging.getLogger(__name__)

    try:
        logger.info("CREATING APP...")
        app.config.from_object(config_object)

        # allow Netlify frontend
        CORS(
            app,
            resources={r"/*": {"origins": [
                "https://buffbuds.netlify.app"
            ]}},
            supports_credentials=True,
            automatic_options=True
        )
        
        # registering Blueprints
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(user_bp, url_prefix='/user')

        logger.info('APP CREATED!')

    except Exception as e:
        logger.error(f"Error creating app: {e}")

    return app

"""
Logging Levels and Activation

The logging module supports multiple severity levels, which control
the importance of the logged messages. The active logging level acts
as a threshold: only messages at that level or higher are output.

Levels (from lowest to highest severity):

DEBUG (10)    - Detailed diagnostic information for developers.
INFO (20)     - General informational messages about app operation.
WARNING (30)  - Indications of potential issues or important events.
ERROR (40)    - Errors that prevent normal program execution.
CRITICAL (50) - Severe errors causing program failure.

Activation:

- The logger's level is set via configuration (e.g., logging.basicConfig(level=logging.INFO))
- Messages with severity **equal or higher** than the configured level are emitted.
- Messages below the set level are ignored.
- For example, if level=INFO, DEBUG messages will not be shown, but INFO, WARNING, ERROR, and CRITICAL will.
"""
