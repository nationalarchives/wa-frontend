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


class BadRequest(Exception):
    """Raised when the API returns a 400 status code."""

    pass


class ResourceForbidden(Exception):
    """Raised when the API returns a 403 status code."""

    pass


class ResourceNotFound(Exception):
    """Raised when the API returns a 404 status code."""

    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data


class JSONAPIClient:
    def __init__(self, api_url, default_headers=None, default_params=None):
        self.api_url = api_url
        self.headers = {
            "Cache-Control": "no-cache",
            "Accept": "application/json",
        }
        if default_headers:
            self.headers.update(default_headers)
        self.params = {} if default_params is None else default_params

    def add_parameter(self, key, value):
        self.params[key] = value

    def add_parameters(self, params):
        self.params = self.params | params

    def get(self, path="/"):
        url = f"{self.api_url}/{path.lstrip('/')}"
        try:
            response = get(url, params=self.params, headers=self.headers)
            if response.history:
                final_url = response.history[-1].headers.get("Location", url)
                final_url = final_url.replace("http://", "https://")
                final_url = final_url.replace("web-wagtail.live.local", "wagtail.nationalarchives.gov.uk")
                response = get(final_url, params=self.params, headers=self.headers)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            current_app.logger.error(f"Network error calling {url}: {type(e).__name__}")
            raise APIError(f"Network error: {e}", status_code=503) from e
        except Exception as e:
            current_app.logger.error(f"Unknown JSON API exception: {e}")
            raise APIError(f"Unexpected error: {e}", status_code=500) from e

        current_app.logger.debug(response.url)

        if response.status_code == codes.ok:
            try:
                return response.json()
            except JSONDecodeError as e:
                current_app.logger.error("JSON API provided non-JSON response")
                raise APIError(
                    "Invalid JSON response", response.status_code, response
                ) from e

        if response.status_code == 400:
            current_app.logger.error(f"Bad request: {response.url}")
            raise BadRequest("Bad request")

        if response.status_code == 403:
            current_app.logger.warning("Forbidden")
            raise ResourceForbidden("Forbidden")

        if response.status_code == 404:
            current_app.logger.warning("Resource not found")
            raise ResourceNotFound("Resource not found")

        # Handle all other error status codes
        current_app.logger.error(f"JSON API responded with {response.status_code}")
        raise APIError(
            f"API request failed with status {response.status_code}",
            response.status_code,
            response,
        )
