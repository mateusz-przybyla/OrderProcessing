from flask import current_app
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from api.extensions import db
from api.models.user import UserModel
from api.schemas.user import UserRegisterSchema, UserLoginSchema
from api.services.blocklist import add_jti_to_blocklist
from api.tasks import email as email_tasks

blp = Blueprint("auth", __name__, description="Endpoints for user registration and authentication.")

@blp.route("/auth/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, description="User created successfully.")
    @blp.alt_response(409, description="A user with that email already exists.")
    def post(self, user_data: dict) -> dict:
        if UserModel.query.filter(UserModel.email == user_data['email']).first():
            abort(409, message="A user with that email already exists.")

        user = UserModel(
            username=user_data['username'],
            email=user_data['email'],
            password=sha256.hash(user_data['password'])
        )

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the user.")

        try:
            email_tasks.send_user_registration_email.delay(user.email, user.username)
        except Exception as e:
            current_app.logger.error(
                "Failed to enqueue async task for sending registration email.",
                extra={"error": str(e), "user_email": user.email}
            )

        return {"message": "User created successfully."}
        
@blp.route("/auth/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    @blp.response(200, description="User logged in successfully.")
    @blp.alt_response(401, description="Invalid credentials.")
    def post(self, user_data: dict[str, str]) -> dict[str, str]:
        user = UserModel.query.filter(UserModel.email == user_data['email']).first()

        if user and sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))
            return {"access_token": access_token, "refresh_token": refresh_token}

        abort(401, message="Invalid credentials.")

@blp.route("/auth/logout")
class UserLogout(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, description="User logged out successfully.")
    def post(self) -> dict[str, str]:
        jti = get_jwt()['jti']
        exp = get_jwt()['exp'] - datetime.now(timezone.utc).timestamp()
        add_jti_to_blocklist(jti, int(exp))
        return {"message": "Successfully logged out."}
    
@blp.route("/auth/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, description="Access token refreshed successfully.")
    def post(self) -> dict[str, str]:
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}