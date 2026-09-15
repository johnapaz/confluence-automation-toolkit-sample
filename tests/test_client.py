from dataclasses import dataclass, field
from typing import Any

from confluence_toolkit.client import ConfluenceClient
from confluence_toolkit.models import PageSnapshot


@dataclass
class FakeResponse:
    status_code: int
    payload: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    content: bytes = b"{}"

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.auth = None
        self.headers: dict[str, str] = {}
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append((method, url, kwargs))
        return self.response


def test_update_payload_increments_version_and_marks_minor_edit() -> None:
    session = FakeSession(FakeResponse(200, {"version": {"number": 12}}))
    client = ConfluenceClient(
        "https://docs.example.com/confluence",
        "portfolio-user",
        "local-test-value",
        session=session,  # type: ignore[arg-type]
    )
    page = PageSnapshot("10001", "Demo page", "<p>Before</p>", 11)
    new_version = client.update_page(page, "<p>After</p>", "Added redirect")

    assert new_version == 12
    method, url, kwargs = session.calls[0]
    assert method == "PUT"
    assert url.endswith("/rest/api/content/10001")
    assert kwargs["json"]["version"] == {
        "number": 12,
        "minorEdit": True,
        "message": "Added redirect",
    }
    assert kwargs["json"]["body"]["storage"]["value"] == "<p>After</p>"
