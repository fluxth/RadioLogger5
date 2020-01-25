from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os.path

from server import BUILD_DIR, server
from common.utils import Config
from common.models import Base

# Check if client-side code is built
if not os.path.isfile(os.path.join(BUILD_DIR, 'index.html')):
    raise Exception('Client-side JS is not built, build it then restart server.')

config = Config('./config.json')

app = Flask('rl5gui',
    static_url_path='/static',
    static_folder=os.path.join(BUILD_DIR, 'static')
)

app.config['SQLALCHEMY_DATABASE_URI'] = config.get('database.uri')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

db = SQLAlchemy(app, model_class=Base)

# Route to /api/
app.route('/api/<path:path>')           (server.serve_api)

# Catch all route /*
app.route('/', defaults={'path': ''})   (server.serve_react)
app.route('/<path:path>')               (server.serve_react)