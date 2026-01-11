from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from api.extensions import db
from api.models.user import UserModel
from api.schemas.user import UserResponseSchema
from api.tasks import debug as test_tasks

blp = Blueprint("debug", __name__, description="Developer endpoints (authentication tests, etc.)")

@blp.route("/debug/guest-route")
class TestGuestEndpoint(MethodView):
    @blp.response(200, description="Guest endpoint accessed successfully.")
    def get(self) -> dict[str, str]:
        """
        Developer test endpoint that demonstrates an open route.
        Accessible without authentication or JWT token.
        Useful for verifying that the API is reachable without protection.
        """
        return {"message": "This endpoint is open to everyone."}

@blp.route("/debug/protected-route")
class TestAuthEndpoint(MethodView):
    @jwt_required()
    @blp.response(200, description="Protected endpoint accessed successfully.")
    @blp.alt_response(401, description="Missing or invalid token.")
    def get(self) -> dict[str, str]:
        """
        Developer test endpoint that requires a valid JWT token.
        Demonstrates how protected routes behave when accessed with or without authentication.
        """
        return {"message": "This is a protected endpoint."}
    
@blp.route("/debug/fresh-protected-route")
class TestFreshAuthEndpoint(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, description="Fresh protected endpoint accessed successfully.")
    @blp.alt_response(401, description="Missing or invalid fresh token.")
    def get(self) -> dict[str, str]:
        """
        Developer test endpoint that requires a fresh JWT token.
        Demonstrates stricter authentication after login.
        """
        return {"message": "This is a protected endpoint. You used a fresh token to access it."}
    
@blp.route("/debug/users/<int:user_id>")
class UserManagement(MethodView):
    @blp.response(200, UserResponseSchema, description="User details retrieved successfully.")
    @blp.alt_response(404, description="User not found.")
    def get(self, user_id: int) -> UserModel:
        """
        Developer endpoint to retrieve user details by user ID.
        """
        user = db.session.get(UserModel, user_id) or abort(404)
        return user
    
    @blp.response(200, description="User deleted successfully.")
    @blp.alt_response(404, description="User not found.")
    def delete(self, user_id: int) -> dict[str, str]:
        """
        Developer endpoint to delete a user by user ID.
        """
        user = db.session.get(UserModel, user_id) or abort(404)

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the user.")

        return {"message": "User deleted."}

@blp.route("/debug/celery/test-task")
class TestCeleryCreateTask(MethodView):
    @blp.response(202, description="Celery task created successfully.")    
    def get(self) -> dict[str, str]:
        """
        Developer endpoint to create and enqueue a long-running Celery task for testing.
        """
        task = test_tasks.long_running_task.delay(10)
        return {
            "task_id": task.id,
            "status": task.status
        }

@blp.route("/debug/celery/test-retry")
class TestCeleryRetryTask(MethodView):
    @blp.response(202, description="Celery retry task created successfully.")
    def get(self) -> dict[str, object]:
        """
        Developer endpoint to create and enqueue a Celery task that tests retry logic.
        Accepts a query parameter 'should_fail' to determine if the task should fail initially.
        """
        should_fail_str = request.args.get("should_fail", "true").lower()

        should_fail = should_fail_str in ("1", "true", "yes", "y")

        task = test_tasks.test_retry_task.delay(should_fail=should_fail)

        return {
            "task_id": task.id,
            "status": task.status,
            "should_fail": should_fail
        }