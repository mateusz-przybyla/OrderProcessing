from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from prometheus_flask_exporter import PrometheusMetrics

db = SQLAlchemy()
migrate = Migrate()
api = Api()
jwt = JWTManager()
metrics = PrometheusMetrics.for_app_factory()