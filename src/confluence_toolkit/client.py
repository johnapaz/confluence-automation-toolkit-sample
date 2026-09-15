"""Small Confluence REST API client used by the redirect service."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import requests
from requests.auth import HTTPBasicAuth

from .errors import ApiError, ConfigurationError
from .models import PageSnapshot

logger = logging.getLogger(__name__)


class ConfluenceClient:
    """Call the Confluence content and label endpoints needed by this sample.

    The client uses a username and API token with HTTP Basic authentication.
    Credentials are supplied at runtime and are never written by this package.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        api_token: str,
        *,
        timeout: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ConfigurationError("CONFLUENCE_BASE_URL must be an HTTP(S) URL.")
        if not username or not api_token:
            raise ConfigurationError("A Confluence username and API token are required.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.auth = HTTPBasicAuth(username, api_token)
        self.session.headers.update({"Accept": "application/json"})

    def test_connection(self) -> None:
        """Verify that the configured identity can reach the Confluence API."""
        self._request("GET", "/rest/api/space", params={"limit": 1})

    def get_page(self, page_id: str) -> PageSnapshot:
        """Return the body and version fields required for a safe update."""
        payload = self._request(
            "GET",
            f"/rest/api/content/{quote(page_id, safe='')}",
            params={"expand": "body.storage,version"},
        )
        try:
            return PageSnapshot(
                page_id=str(payload["id"]),
                title=payload["title"],
                storage_value=payload["body"]["storage"]["value"],
                version=int(payload["version"]["number"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ApiError(f"Page {page_id} returned an unexpected response shape.") from exc

    def update_page(self, page: PageSnapshot, storage_value: str, version_comment: str) -> int:
        """Create the next minor version of a page and return its version number."""
        next_version = page.version + 1
        payload = {
            "version": {
                "number": next_version,
                "minorEdit": True,
                "message": version_comment,
            },
            "title": page.title,
            "type": "page",
            "body": {
                "storage": {
                    "value": storage_value,
                    "representation": "storage",
                }
            },
        }
        response = self._request(
            "PUT",
            f"/rest/api/content/{quote(page.page_id, safe='')}",
            json=payload,
        )
        return int(response.get("version", {}).get("number", next_version))

    def add_label(self, page_id: str, label: str) -> None:
        """Apply a tracking label after a successful page update."""
        self._request(
            "POST",
            f"/rest/api/content/{quote(page_id, safe='')}/label",
            json=[{"prefix": "global", "name": label}],
        )

    def remove_label(self, page_id: str, label: str) -> None:
        """Remove a tracking label after a redirect is removed."""
        self._request(
            "DELETE",
            f"/rest/api/content/{quote(page_id, safe='')}/label/{quote(label, safe='')}",
            allowed_statuses={200, 204, 404},
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        allowed_statuses: set[int] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        logger.debug("HTTP %s %s", method, path)
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise ApiError(f"{method} {path} failed before a response was received: {exc}") from exc

        expected = allowed_statuses or {200, 201, 204}
        if response.status_code not in expected:
            request_id = response.headers.get("X-Request-Id") or response.headers.get("Atl-Traceid")
            suffix = f" Request ID: {request_id}." if request_id else ""
            raise ApiError(f"{method} {path} returned HTTP {response.status_code}.{suffix}")

        logger.debug("HTTP %s %s returned %s", method, path, response.status_code)
        if response.status_code in {204, 404} or not response.content:
            return {}
        try:
            return response.json()
        except requests.ValueError as exc:
            raise ApiError(f"{method} {path} returned a non-JSON response.") from exc
