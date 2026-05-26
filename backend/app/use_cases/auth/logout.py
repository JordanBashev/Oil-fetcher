from fastapi.responses import Response

from app.config import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from app.utils.global_messages import LOGOUT_SUCCESS_MESSAGE


class LogoutUseCase:
    def execute(self, response: Response) -> dict:
        response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME)
        response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME)
        return {"detail": LOGOUT_SUCCESS_MESSAGE}
