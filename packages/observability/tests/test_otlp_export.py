import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from quadralug_observability import build_tracer_provider

RESOURCE = {"service.name": "quadralug-bff", "deployment.environment": "test"}


class Collector(ThreadingHTTPServer):
    paths: list[str]


class Handler(BaseHTTPRequestHandler):
    server: Collector

    def do_POST(self) -> None:
        self.rfile.read(int(self.headers["Content-Length"]))
        self.server.paths.append(self.path)
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        pass


@pytest.fixture
def collector() -> Iterator[Collector]:
    server = Collector(("127.0.0.1", 0), Handler)
    server.paths = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


def span_exporters(provider: TracerProvider) -> list[Any]:
    processors = provider._active_span_processor._span_processors
    return [processor.span_exporter for processor in processors]


def test_otlp_exports_spans_to_the_endpoint(collector: Collector) -> None:
    endpoint = f"http://127.0.0.1:{collector.server_port}"
    provider = build_tracer_provider(RESOURCE, {"OTEL_EXPORTER_OTLP_ENDPOINT": endpoint})

    with provider.get_tracer("t").start_as_current_span("s"):
        pass
    provider.force_flush()

    assert collector.paths == ["/v1/traces"]
    provider.shutdown()


def test_otlp_endpoint_with_trailing_slash(collector: Collector) -> None:
    endpoint = f"http://127.0.0.1:{collector.server_port}/"
    provider = build_tracer_provider(RESOURCE, {"OTEL_EXPORTER_OTLP_ENDPOINT": endpoint})

    with provider.get_tracer("t").start_as_current_span("s"):
        pass
    provider.force_flush()

    assert collector.paths == ["/v1/traces"]
    provider.shutdown()


def test_otlp_exporter_created_when_defined() -> None:
    provider = build_tracer_provider(
        RESOURCE, {"OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:4318"}
    )

    exporters = span_exporters(provider)

    assert len(exporters) == 1
    assert isinstance(exporters[0], OTLPSpanExporter)
    provider.shutdown()


@pytest.mark.parametrize(
    "environ", [{}, {"OTEL_EXPORTER_OTLP_ENDPOINT": ""}, {"OTEL_EXPORTER_OTLP_ENDPOINT": "  "}]
)
def test_otlp_exporter_absent_when_undefined(environ: dict[str, str]) -> None:
    provider = build_tracer_provider(RESOURCE, environ)

    exporters = span_exporters(provider)

    assert exporters == []
