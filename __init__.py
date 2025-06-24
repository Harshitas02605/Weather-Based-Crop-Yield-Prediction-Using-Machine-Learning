from flask import Flask;
from flask_sqlalchemy import SQLAlchemy;
from flask_restful import Api;
import os;
from flask_login import LoginManager;
from dotenv import load_dotenv; # type: ignore

load_dotenv();

app = Flask(__name__, static_folder='./static', template_folder='./templates');

api = Api(app)

app.secret_key = os.getenv('SECRET_KEY');

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CropMaster.db';

db = SQLAlchemy(app);

login_manager = LoginManager();
login_manager.init_app(app);
login_manager.login_view = 'login';
login_manager.login_message_category = 'success';


from CropMaster import routes;
from CropMaster.apis import PredictionAPI

api.add_resource(PredictionAPI, '/api/predict')