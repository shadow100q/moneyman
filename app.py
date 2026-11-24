import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, session
from config import Config
from database.db import db, init_db
from models import User
from routes import register_blueprints

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    init_db(app)

    # Register all routes and blueprints
    register_blueprints(app)

    # Context processor to make common data available across all templates
    @app.context_processor
    def inject_globals():
        user_obj = None
        if "user_id" in session:
            user_obj = User.query.get(session["user_id"])
        
        now = datetime.now()
        return {
            "current_user": user_obj,
            "app_name": "MoneyMate",
            "current_year": now.year,
            "current_month": now.month,
            "currency_symbol": user_obj.currency if user_obj else app.config.get("DEFAULT_CURRENCY", "₹"),
            "dev_mode": app.config.get("DEV_OTP_MODE", True)
        }

    # Centralized Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("base.html", error_title="Page Not Found (404)", error_msg="The page you requested does not exist."), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error("Internal Server Error: %s", error)
        return render_template("base.html", error_title="Server Error (500)", error_msg="An unexpected error occurred. Please try again."), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        logger.error("Unhandled Exception: %s", e, exc_info=True)
        return jsonify({"success": False, "error": "An internal server error occurred"}), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    logger.info("Starting MoneyMate on http://%s:%d", host, port)
    app.run(host=host, port=port, debug=True)
