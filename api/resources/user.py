from flask.views import MethodView
from flask_smorest import abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.extensions import db
from api.models.user import UserModel
from api.schemas.user import UserResponseSchema

blp = Blueprint("user", __name__, description="Endpoints for user account management.")

@blp.route("/users/me")
class UserMe(MethodView):
    @jwt_required()
    @blp.response(200, UserResponseSchema, description="Authenticated user's profile.")
    def get(self) -> UserModel:
        user_id = get_jwt_identity()
        user = db.session.get(UserModel, user_id) or abort(404)
        return user