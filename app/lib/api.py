from flask import current_app
from requests import (
    ConnectionError,
    JSONDecodeError,
    Timeout,
    TooManyRedirects,
    codes,
    get,
)


class APIError(Exception):
    """Raised when the API returns an error status code."""

    def __init__(self, message, status_code, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ResourceNotFound(Exception):
    """Raised when the API returns a 404 status code."""

    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data


class ResourceForbidden(Exception):
    """Raised when the API returns a 403 status code."""

    pass


class JSONAPIClient:
    api_url = ""
    params = {}

    def __init__(self, api_url, params=None):
        self.api_url = api_url
        self.params = {} if params is None else params

    def add_parameter(self, key, value):
        self.params[key] = value

    def add_parameters(self, params):
        self.params = self.params | params

    def get(self, path="/"):
        url = f"{self.api_url}/{path.lstrip('/')}"
        headers = {
            "Cache-Control": "no-cache",
            "Accept": "application/json",
        }

        try:
            response = get(url, params=self.params, headers=headers)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            current_app.logger.error(f"Network error calling {url}: {type(e).__name__}")
            raise

        current_app.logger.debug(response.url)

        if response.status_code == codes.ok:
            try:
                return response.json()
            except JSONDecodeError as e:
                current_app.logger.error("JSON API provided non-JSON response")
                raise APIError(
                    "Invalid JSON response", response.status_code, response
                ) from e

        if response.status_code == 403:
            current_app.logger.warning("Forbidden")
            raise ResourceForbidden("Forbidden")

        if response.status_code == 404:
            current_app.logger.warning("Resource not found")
            try:
                data = response.json()
            except JSONDecodeError:
                data = None
            raise ResourceNotFound("Resource not found", data)

        # Handle all other error status codes
        current_app.logger.error(f"JSON API responded with {response.status_code}")
        raise APIError(
            f"API request failed with status {response.status_code}",
            response.status_code,
            response,
        )
