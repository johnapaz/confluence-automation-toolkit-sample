from pathlib import Path

import pytest

from confluence_toolkit.errors import InputError
from confluence_toolkit.models import PageSnapshot, RedirectRequest
from confluence_toolkit.redirects import (
    MANAGED_MARKER,
    RedirectService,
    build_redirect_macro,
    parse_redirect_csv,
    remove_managed_redirect,
)


class FakeClient:
    def __init__(self, storage_value: str = "<p>Original body</p>") -> None:
        self.page = PageSnapshot("10001", "Reset a demo password", storage_value, 7)
        self.updates: list[tuple[PageSnapshot, str, str]] = []
        self.labels_added: list[tuple[str, str]] = []
        self.labels_removed: list[tuple[str, str]] = []

    def get_page(self, page_id: str) -> PageSnapshot:
        assert page_id == self.page.page_id
        return self.page

    def update_page(self, page: PageSnapshot, storage_value: str, comment: str) -> int:
        self.updates.append((page, storage_value, comment))
        return page.version + 1

    def add_label(self, page_id: str, label: str) -> None:
        self.labels_added.append((page_id, label))

    def remove_label(self, page_id: str, label: str) -> None:
        self.labels_removed.append((page_id, label))


def test_macro_escapes_user_controlled_text() -> None:
    macro = build_redirect_macro("https://kb.example.com/a?x=1&y=2", "A <new> home")
    assert "https://kb.example.com/a?x=1&amp;y=2" in macro
    assert "A &lt;new&gt; home" in macro
    assert MANAGED_MARKER in macro


def test_add_dry_run_makes_no_write() -> None:
    client = FakeClient()
    service = RedirectService(client)
    result = service.add(
        RedirectRequest("10001", "https://kb.example.com/articles/10001", "New article"),
        dry_run=True,
    )
    assert result.status == "planned"
    assert result.previous_version == 7
    assert result.new_version == 8
    assert client.updates == []
    assert client.labels_added == []


def test_add_writes_versioned_content_then_labels_page() -> None:
    client = FakeClient()
    service = RedirectService(client)
    result = service.add(
        RedirectRequest("10001", "https://kb.example.com/articles/10001", "New article")
    )
    assert result.status == "changed"
    assert result.new_version == 8
    assert MANAGED_MARKER in client.updates[0][1]
    assert client.updates[0][1].endswith("<p>Original body</p>")
    assert client.labels_added == [("10001", "redirected")]


def test_remove_only_deletes_managed_macro() -> None:
    managed = build_redirect_macro("https://kb.example.com/articles/10001", "New article")
    other_macro = '<ac:structured-macro ac:name="html">Other</ac:structured-macro>'
    original = f"{other_macro}<p>Keep me</p>{managed}"
    updated, removed = remove_managed_redirect(original)
    assert removed is True
    assert "Keep me" in updated
    assert ">Other</ac:structured-macro>" in updated
    assert MANAGED_MARKER not in updated


def test_label_failure_is_reported_after_successful_page_update() -> None:
    class LabelFailureClient(FakeClient):
        def add_label(self, page_id: str, label: str) -> None:
            raise RuntimeError("label endpoint unavailable")

    client = LabelFailureClient()
    service = RedirectService(client)
    result = service.add(
        RedirectRequest("10001", "https://kb.example.com/articles/10001", "New article")
    )
    assert result.status == "changed"
    assert "tracking label was not added" in result.warnings[0]


def test_parse_csv_reports_source_rows(tmp_path: Path) -> None:
    source = tmp_path / "redirects.csv"
    source.write_text(
        "page_id,target_url,target_title\n"
        "10001,https://kb.example.com/articles/10001,Reset a demo password\n",
        encoding="utf-8",
    )
    records = parse_redirect_csv(source)
    assert records == [
        RedirectRequest(
            "10001",
            "https://kb.example.com/articles/10001",
            "Reset a demo password",
            source_row=2,
        )
    ]


def test_parse_csv_rejects_non_http_target(tmp_path: Path) -> None:
    source = tmp_path / "redirects.csv"
    source.write_text(
        "page_id,target_url,target_title\n10001,javascript:alert(1),Unsafe\n",
        encoding="utf-8",
    )
    with pytest.raises(InputError, match="Invalid target URL"):
        parse_redirect_csv(source)
