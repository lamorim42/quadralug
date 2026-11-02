import json
import logging

import pytest
from quadralug_observability import JsonFormatter, redact


@pytest.mark.parametrize(
    "key",
    [
        "password",
        "password_hash",
        "token",
        "cookie",
        "set-cookie",
        "authorization",
        "email",
        "Email",
        "PASSWORD",
        "Set-Cookie",
        "http.request.header.cookie",
        "http.response.header.set-cookie",
        "user.email",
        "access_token",
        "refresh_token",
        "new_password",
        "http.response.header.set_cookie",
    ],
)
def test_redaction_replaces_value(key: str) -> None:
    result = redact({key: "segredo"})

    assert result == {key: "[REDACTED]"}


@pytest.mark.parametrize(
    "key",
    ["enduser.id", "email.domain", "token_count", "passwords", "http.route", "cookie.name"],
)
def test_redaction_preserves_other_keys(key: str) -> None:
    result = redact({key: "valor"})

    assert result == {key: "valor"}


def test_redaction_reaches_nested_mapping() -> None:
    result = redact({"http": {"request": {"token": "t", "route": "/x"}}})

    assert result == {"http": {"request": {"token": "[REDACTED]", "route": "/x"}}}


def test_redaction_reaches_mappings_in_lists() -> None:
    result = redact({"pessoas": [{"email": "a@b.c"}, {"nome": "x"}]})

    assert result == {"pessoas": [{"email": "[REDACTED]"}, {"nome": "x"}]}


def test_redaction_replaces_non_string_value() -> None:
    result = redact({"token": {"valor": "t"}})

    assert result == {"token": "[REDACTED]"}


def test_redaction_applies_in_the_formatter() -> None:
    record = logging.LogRecord("t", logging.INFO, __file__, 1, "evento", None, None)
    record.attributes = {"Email": "a@b.c", "enduser.id": "1"}

    line = JsonFormatter({}).format(record)

    assert "a@b.c" not in line
    assert json.loads(line)["attributes"] == {"Email": "[REDACTED]", "enduser.id": "1"}
