import json

from starlette.responses import JSONResponse


class JsonHTTPException(Exception):
    def __init__(
        self,
        status_code: int,
        error_name: str,
        error_description: str,
        error_code: int | None = None,
        error_meta: dict | None = None,
        headers: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_name = error_name
        self.error_description = error_description
        self.error_code = error_code
        self.error_meta = error_meta
        self.headers = headers or {}

        if status_code == 401:
            if self.headers.get("WWW-Authenticate") is None:
                self.headers["WWW-Authenticate"] = "Bearer"

    def _render_response_body(self) -> dict:
        return {
            "error": {
                "name": self.error_name,
                "code": self.error_code or self.status_code,
                "description": self.error_description,
                "meta": self.error_meta or {},
            }
        }

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content=self._render_response_body(),
            headers=self.headers,
        )

    def raw_response(self) -> dict:
        return self._render_response_body()

    def json_raw_response(self) -> str:
        return json.dumps(self._render_response_body())

    def __str__(self) -> str:
        return str(self._render_response_body())