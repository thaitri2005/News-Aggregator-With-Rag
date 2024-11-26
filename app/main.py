# app/main.py
from flask import Flask
from flask_cors import CORS  # type: ignore
from api.routes import api
from utils.logging_config import setup_logging

# Initialize logging
setup_logging()

app = Flask(__name__)
CORS(app)

# Register Blueprints for API
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def home():
    return "RAG AI News Aggregator Backend"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
