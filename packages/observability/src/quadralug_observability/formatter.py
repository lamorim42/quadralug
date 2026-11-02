import json
import logging
import re
import traceback
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace

REDACTED = "[REDACTED]"
SENSITIVE_SUFFIX = re.compile(r"(^|[_-])(password|password_hash|token|cookie|authorization|email)$")
SEVERITIES = {
    logging.DEBUG: ("DEBUG", 5),
    logging.INFO: ("INFO", 9),
    logging.WARNING: ("WARN", 13),
    logging.ERROR: ("ERROR", 17),
    logging.CRITICAL: ("FATAL", 21),
}


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: REDACTED if _is_sensitive(key) else redact(item) for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [redact(item) for item in value]
    return value


def _is_sensitive(key: Any) -> bool:
    return SENSITIVE_SUFFIX.search(str(key).rsplit(".", 1)[-1].lower()) is not None


class JsonFormatter(logging.Formatter):
    def __init__(self, resource: Mapping[str, str]) -> None:
        super().__init__()
        self._resource = dict(resource)

    def format(self, record: logging.LogRecord) -> str:
        severity_text, severity_number = SEVERITIES.get(
            record.levelno, (record.levelname, record.levelno)
        )
        span_context = trace.get_current_span().get_span_context()
        has_span = span_context.is_valid
        timestamp = datetime.fromtimestamp(record.created, UTC)
        return json.dumps(
            {
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "severity_text": severity_text,
                "severity_number": severity_number,
                "body": record.getMessage(),
                "trace_id": trace.format_trace_id(span_context.trace_id) if has_span else None,
                "span_id": trace.format_span_id(span_context.span_id) if has_span else None,
                "resource": self._resource,
                "attributes": redact(_attributes_of(record)),
            },
            ensure_ascii=False,
            default=str,
        )


def _attributes_of(record: logging.LogRecord) -> dict[str, Any]:
    attributes: dict[str, Any] = dict(getattr(record, "attributes", {}))
    if record.exc_info and record.exc_info[1] is not None:
        error = record.exc_info[1]
        attributes["exception.type"] = type(error).__name__
        attributes["exception.message"] = str(error)
        attributes["exception.stacktrace"] = "".join(traceback.format_exception(error))
    return attributes
